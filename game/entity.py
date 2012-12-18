import pygame as pg

from conf import conf
from util import ir, scale_up, weighted_rand, dd


def solid (e):
    if hasattr(e, 'ident') and e.ident in conf.SOLID_ENTITIES:
        return not (e.ident == 'enemy' and e.dead)
    return isinstance(e, pg.Rect)


class Rect (object):
    def __init__ (self, level, rect):
        self.ident = ident = self.__class__.__name__.lower()
        self.level = level
        self.tile_size = ts = conf.TILE_SIZES.get(ident, conf.TILE_SIZE)
        self.rect = pg.Rect(scale_up(rect, ts))
        # load images and generate tilemap
        imgs = {}
        for i, weighting in enumerate(conf.TILED_IMG_FREQS[ident]):
            imgs[level.game.img('{0}{1}.png'.format(ident, i))] = weighting
        w, h = self.rect.size
        self.img_map = img_map = []
        for x in xrange(w / ts):
            col = []
            img_map.append(col)
            for y in xrange(h / ts):
                col.append(weighted_rand(imgs))

    def draw (self, screen):
        if self.img_map is None:
            screen.fill(self.colour, self.rect)
        else:
            ts = self.tile_size
            x0, y0 = self.rect.topleft
            for x, col in enumerate(self.img_map):
                for y, img in enumerate(col):
                    screen.blit(img, (x0 + ts * x, y0 + ts * y))


class BG (Rect):
    pass


class SolidRect (Rect):
    pass


class Entity (object):
    def __init__ (self, level, pos, size = None, img_size = None, imgs = None,
                  aligned = False):
        # imgs is list of (img_name, sfc) if given
        self.ident = ident = self.__class__.__name__.lower()
        self.level = level
        pos = scale_up(pos)
        if size is None:
            size = conf.SIZES[ident]
        if not aligned:
            ts = conf.TILE_SIZE
            # move to centre of bottom edge of lower tile
            overlap = size[0] % ts
            if overlap != 0:
                pos[0] += (ts - overlap) / 2
            pos[1] -= size[1]
        self.rect = pg.Rect(pos, size)
        # load images
        if imgs is None:
            imgs = {}
            img_names = conf.IMGS.get(ident, ('',))
            initial_img = img_names[0]
            for ext in img_names:
                img = level.game.img(ident + ('-' if ext else '') + ext + '.png')
                imgs[ext] = img
        else:
            initial_img = imgs[0][0]
            imgs = dict(imgs)
        self.imgs = imgs
        # drawing stuff
        if img_size is None:
            if ident in conf.IMG_SIZES:
                img_size = conf.IMG_SIZES[ident]
            elif ident in conf.SIZES:
                img_size = conf.SIZES[ident]
            else:
                img_size = imgs[initial_img].get_size()
        self.img_size = img_size
        self.img_offset = conf.IMG_OFFSETS[ident]
        self.update_draw_rect()
        self.anim_offset = 0
        self.anim = False
        self.set_img(initial_img)

    def set_img (self, img):
        self.img = img
        self.dirty = True

    def stop_anim (self):
        if self.anim:
            self.level.game.scheduler.rm_timeout(self._anim_timer)
            self.anim_offset = 0
            self.dirty = True

    def start_anim (self, n = None):
        if self.anim:
            self.stop_anim()
        self.anim = True
        if self.anim_offset != 0:
            self.anim_offset = 0
            self.dirty = True
        t = conf.ANIMATION_TIMES[self.ident][self.img]
        self._n_frames = self.imgs[self.img].get_width() / self.draw_rect.width
        self._anim_timer = self.level.game.scheduler.add_timeout(self._anim_cb, frames = t)
        self._repeat = n

    def _anim_cb (self):
        self.anim_offset += 1
        if self.anim_offset >= self._n_frames:
            if self._repeat is not None:
                self._repeat -= 1
                if self._repeat < 0:
                    self.anim_offset -= 1
                    return
            self.anim_offset = 0
        self.dirty = True
        return True

    def update_draw_rect (self):
        self.draw_rect = pg.Rect(self.rect.move(self.img_offset)[:2], self.img_size)

    def draw (self, screen):
        anim_pos = (self.anim_offset * self.draw_rect.width, 0)
        img_rect = pg.Rect(anim_pos, self.img_size)
        screen.blit(self.imgs[self.img], self.draw_rect, img_rect)


class Barrier (Entity):
    def __init__ (self, level, rect):
        deflate = conf.BARRIER_DEFLATE
        img_size = scale_up(rect[2:])
        size = (img_size[0] - 2 * deflate, img_size[1] - 2 * deflate)
        img = pg.Surface(img_size).convert_alpha()
        img.fill(conf.BARRIER_COLOUR)
        Entity.__init__(self, level, rect[:2], size, img_size, [('', img)], True)
        self.rect.move_ip(deflate, deflate)
        self.update_draw_rect()
        self.on = True

    def toggle (self):
        self.on = not self.on
        self.dirty = True

    def draw (self, screen):
        if self.on:
            Entity.draw(self, screen)


class Changer (Entity):
    pass


class Switch (Entity):
    def __init__ (self, level, pos, barrier):
        Entity.__init__(self, level, pos)
        self.barrier = barrier
        self.on = True

    def toggle (self):
        g = self.level.game
        g.play_snd('lever')
        self.barrier.toggle()
        self.on = not self.on
        self.set_img('on' if self.on else 'off')
        self.dirty = True


class Goal (Entity):
    def __init__ (self, level, pos):
        Entity.__init__(self, level, pos, img_size = conf.SIZES['goal'])


class MovingEntity (Entity):
    def __init__ (self, level, pos):
        self.level = level
        Entity.__init__(self, level, pos)
        # some initial values
        self.vel = [0, 0]
        self.overflow = [0, 0]
        self.on_ground = False
        self._to_move = [0, 0]
        self.jumping = False
        self._jump_time = 0
        self._jumped = False
        self._step_snd_counter = 0
        self._extra_collide_es = []
        self.dirn = -1
        self.walking = False

    def collide (self, e, axis, dirn):
        if solid(e):
            if axis == 1 and dirn == 1:
                self.on_ground = True
            return True

    def move_by (self, dp):
        # move and handle collisions
        collide = self.collide
        in_bounds = self.level.rect.contains
        es = self.level.moving + self.level.solid + self._extra_collide_es
        es.remove(self)
        o = self.overflow
        r = self.rect
        p = [r[0] + o[0] + dp[0], r[1] + o[1] + dp[1]]
        dest = [ir(p[0]), ir(p[1])]
        self.overflow = o = [p[0] - dest[0], p[1] - dest[1]]
        for axis in (0, 1):
            dx = dest[axis] - r[axis]
            if dx == 0:
                continue
            dirn = 1 if dx > 0 else -1
            while dx != 0:
                r[axis] += dirn
                dx -= dirn
                col_es = [e for e in es if r.colliderect(e.rect)]
                if not in_bounds(r):
                    col_es.append(self.level.rect)
                if any(collide(e, axis, dirn) for e in col_es):
                    r[axis] -= dirn
                    o[axis] = 0
                    self.vel[axis] = 0
                    break

    def run (self, dirn):
        self._to_move[dirn] = 1

    def jump (self, held):
        if not held and not self.jumping and self.on_ground:
            # start jumping
            self.vel[1] -= conf.JUMP_INITIAL[self.ident]
            self.jumping = True
            self._jump_time = conf.JUMP_TIME[self.ident]
            self._jumped = True
            self.level.game.play_snd('hit', conf.SOUND_VOLUMES['jump'])
        elif held and self.jumping and not self._jumped:
            # continue jumping
            self.vel[1] -= conf.JUMP_CONTINUE[self.ident]
            self._jumped = True
            self._jump_time -= 1
            if self._jump_time <= 0:
                self.jumping = False

    def dirty_rect (self):
        return (self.draw_rect, self._old_draw_rect)

    def update (self):
        # jumping
        if self.jumping and not self._jumped:
            self.jumping = False
        self._jumped = False
        # vel
        v = self.vel
        speed = conf.MOVE_SPEED[self.ident] if self.on_ground else conf.MOVE_SPEED_AIR[self.ident]
        dirn = self._to_move[1] - self._to_move[0]
        self._to_move = [0, 0]
        v[0] += speed * dirn
        v[1] += conf.GRAVITY
        damp = conf.FRICTION if self.on_ground else conf.AIR_RESISTANCE
        for i in (0, 1):
            v[i] *= damp[i]
        # run sound
        if dirn != 0 and self.on_ground:
            self._step_snd_counter -= 1
            if self._step_snd_counter <= 0:
                self._step_snd_counter = conf.STEP_SOUND_TIME[self.ident]
                self.level.game.play_snd('hit', conf.SOUND_VOLUMES['step'])
        # pos
        self.on_ground = False
        self._old_draw_rect = self.draw_rect.copy()
        self.move_by(v)
        self.update_draw_rect()
        # image
        if dirn == 0:
            if self.walking:
                self.walking = False
                self.update_img()
                self.stop_anim()
        else:
            if not self.walking or self.dirn != dirn:
                self.dirn = dirn
                self.walking = True
                self.update_img()
                self.start_anim()
            else:
                self.dirn = dirn


class Player (MovingEntity):
    def __init__ (self, level, pos):
        MovingEntity.__init__(self, level, pos)
        self.villain = False
        self._extra_collide_es = self.level.barriers + [self.level.goal]
        self.dead = False

    def update_img (self):
        self.set_img(('villain' if self.villain else '') + \
                     ('walk' if self.walking else '') + \
                     ('left' if self.dirn == -1 else 'right'))

    def collide (self, e, axis, dirn):
        MovingEntity.collide(self, e, axis, dirn)
        if self.dead:
            return solid(e)
        if solid(e):
            return True
        elif isinstance(e, Barrier) and e.on and not self.villain:
            self.die()
        elif isinstance(e, Goal):
            # stop moving
            self.dead = True
            self.level.win()

    def move (self, dirn, held):
        if self.dead:
            return
        if dirn in (0, 2):
            if held:
                self.run(dirn / 2)
        elif dirn == 1:
            self.jump(held)
        else: # dirn == 3
            r = self.rect
            if any(r.colliderect(c.rect) for c in self.level.changers):
                self.level.game.play_snd('change')
                self.villain = not self.villain
                self.update_img()
            for s in self.level.switches:
                if r.colliderect(s.rect):
                    s.toggle()

    def die (self):
        if not self.dead:
            self.dead = True
            self.level.restart()
            self.level.game.play_snd('die')


class Enemy (MovingEntity):
    def __init__ (self, level, pos):
        MovingEntity.__init__(self, level, pos)
        self.colour = (255, 255, 255)
        self._extra_collide_es = self.level.barriers
        self._seeking = False
        self._los_time = 0
        self._initial_rect = self.rect.copy()
        self._blocked = False
        self.dead = False

    def update_img (self):
        self.set_img('left' if self.dirn == -1 else 'right')

    def collide (self, e, axis, dirn):
        MovingEntity.collide(self, e, axis, dirn)
        if self.dead:
            return isinstance(e, SolidRect)
        if isinstance(e, Player) and (axis == 0 or dirn == 1) and not e.villain:
            # only catch player if overlap in y by more than a little
            y0 = self.rect[1]
            y1 = y0 + self.rect[3]
            py0 = e.rect[1]
            py1 = py0 + e.rect[3]
            if min(y1 - py0, py1 - y0) >= conf.MIN_CATCH_Y_OVERLAP:
                e.die()
            return True
        if solid(e):
            if axis == 0:
                self._blocked = True
            return True
        elif isinstance(e, Barrier) and e.on:
            self.die()

    def die (self):
        if not self.dead:
            self.dead = True
            self.level.game.play_snd('zap')

    def dist (self, rect):
        pos = self.rect.center
        other_pos = rect.center
        dx = other_pos[0] - pos[0]
        dy = (other_pos[1] - pos[1])
        return ((pos, other_pos), (dx, dy), (dx * dx + dy * dy) ** .5)

    def _move_towards (self, dp):
        if abs(dp[0]) > conf.STOP_SEEK_NEAR:
            self.run(dp[0] > 0)
        if self._blocked or self.jumping:
            self.jump(self.jumping)

    def update (self):
        self._blocked = False
        MovingEntity.update(self)
        if self.dead:
            return
        # AI
        self._los_time -= 1
        player = self.level.player
        if player.villain:
            self._seeking = False
        else:
            ((lx0, ly0), (lx1, ly1)), dp, dist = self.dist(player.rect)
            # check if can see player
            if lx0 > lx1:
                lx0, lx1 = lx1, lx0
            if ly0 > ly1:
                ly0, ly1 = ly1, ly0
            vert = dp[0] == 0
            if vert:
                c = lx0
            else:
                m = float(ly1 - ly0) / (lx1 - lx0)
                c = ly0 - m * lx0
            los = True
            for r in self.level.solid:
                x0, y0, w, h = r.rect
                x1, y1 = x0 + w, y0 + h
                if vert:
                    if x0 < c < x1 and ly0 < y0 < ly1:
                        los = False
                        break
                else:
                    if m != 0:
                        if x0 < (y0 - c) / m < x1 and ly0 < y0 < ly1:
                            los = False
                            break
                        if x0 < (y1 - c) / m < x1 and ly0 < y1 < ly1:
                            los = False
                            break
                    if y0 < m * x0 + c < y1 and lx0 < x0 < lx1:
                        los = False
                        break
                    if y0 < m * x1 + c < y1 and lx0 < x1 < lx1:
                        los = False
                        break
            max_dist = conf.STOP_SEEK_FAR if self._seeking else conf.START_SEEK_NEAR
            if dist > max_dist:
                los = False
            if los:
                self._los_time = conf.SEEK_TIME
            # determine whether to chase the player
            if self._seeking:
                if self._los_time <= 0:
                    self._seeking = False
            elif dist <= conf.START_SEEK_NEAR and los:
                self.level.game.play_snd('alert-guard')
                self._seeking = True
            if self._seeking:
                self._move_towards(dp)
        if not self._seeking:
            (pos0, pos1), dp, dist = self.dist(self._initial_rect)
            self._move_towards(dp)
