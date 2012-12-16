import pygame as pg

from conf import conf
from util import ir, scale_up, weighted_rand, dd


class Rect (object):
    def __init__ (self, level, rect):
        self.ident = self.__class__.__name__.lower()
        self.level = level
        if not hasattr(self, 'tile_size'):
            self.tile_size = conf.TILE_SIZE
        ts = self.tile_size
        self.rect = pg.Rect(scale_up(rect, ts))
        # load images and generate tilemap
        imgs = {}
        for i, weighting in enumerate(self.img_freqs):
            imgs[level.game.img('{0}{1}.png'.format(self.ident, i))] = weighting
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
    tile_size = conf.BG_TILE_SIZE
    img_freqs = (1, .8, .05, .1, .07, .1, .07, .02)


class SolidRect (Rect):
    img_freqs = BG.img_freqs


class Entity (object):
    img_rect = None
    imgs = ('',)
    anims = {}

    def __init__ (self, level, pos, size = None, img = None):
        self.ident = self.__class__.__name__.lower()
        self.level = level
        pos = scale_up(pos)
        if size is None:
            size = conf.SIZES[self.ident]
            ts = conf.TILE_SIZE
            # move to centre of bottom edge of lower tile
            overlap = size[0] % ts
            if overlap != 0:
                pos[0] += (ts - overlap) / 2
            pos[1] -= size[1]
        self.rect = pg.Rect(pos, size)
        # load image
        imgs = {}
        if img is None:
            try:
                for ext in self.imgs:
                    img = level.game.img(self.ident + ('-' if ext else '') + ext + '.png')
                    imgs[ext] = img
            except Exception, e:
                print e
                imgs[''] = None
        else:
            imgs[''] = img
        self.imgs = imgs
        self.img = ''
        if imgs[''] is not None:
            self.offset = conf.IMG_OFFSETS[self.ident]
            if self.img_rect is None:
                self.img_rect = self.imgs[''].get_rect()
            self.anim_offset = 0
            self.anim = False
        self.dirty = False

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
        t = self.anims[self.img]
        self._n_frames = self.imgs[self.img].get_width() / self.img_rect.width
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

    def draw (self, screen):
        img = self.imgs[self.img]
        if img is None:
            screen.fill(self.colour, self.rect)
        else:
            r = self.img_rect.move(self.anim_offset * self.img_rect.width, 0)
            screen.blit(img, self.rect.move(self.offset), r)


class Barrier (Entity):
    def __init__ (self, level, rect):
        size = scale_up(rect[2:])
        img = pg.Surface(size).convert_alpha()
        img.fill(conf.BARRIER_COLOUR)
        Entity.__init__(self, level, rect[:2], size, img)
        self.on = True
        self.dirty = False

    def toggle (self):
        self.on = not self.on
        self.dirty = True

    def draw (self, screen):
        if self.on:
            Entity.draw(self, screen)


class Changer (Entity):
    pass


class Switch (Entity):
    imgs = ('', 'off')

    def __init__ (self, level, pos, barrier):
        Entity.__init__(self, level, pos)
        self.barrier = barrier
        self.on = True

    def toggle (self):
        g = self.level.game
        g.play_snd('lever')
        self.barrier.toggle()
        self.on = not self.on
        self.set_img('' if self.on else 'off')
        self.dirty = True


class Goal (Entity):
    img_rect = pg.Rect(0, 0, 20, 40)
    anims = {'': 10}


class MovingEntity (Entity):
    def __init__ (self, level, pos):
        self.level = level
        Entity.__init__(self, level, pos)
        # some initial values
        self.vel = [0, 0]
        self.overflow = [0, 0]
        self.on_ground = False
        self._to_move = [False, False]
        self.jumping = False
        self._jump_time = 0
        self._jumped = False
        self._step_snd_counter = 0
        self._extra_collide_es = []

    def collide (self, e, axis, dirn):
        if e.__class__ in SOLID_ES and not (isinstance(e, Enemy) and e.dead):
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
        ident = self.__class__.__name__.lower()
        speed = conf.MOVE_SPEED[ident] if self.on_ground else conf.MOVE_SPEED_AIR[ident]
        self._to_move[dirn] = speed
        if self.on_ground:
            self._step_snd_counter -= 1
            if self._step_snd_counter <= 0:
                self._step_snd_counter = conf.STEP_SOUND_TIME[ident]
                self.level.game.play_snd('hit', conf.SOUND_VOLUMES['step'])

    def jump (self, held):
        ident = self.__class__.__name__.lower()
        if not held and not self.jumping and self.on_ground:
            # start jumping
            self.vel[1] -= conf.JUMP_INITIAL[ident]
            self.jumping = True
            self._jump_time = conf.JUMP_TIME[ident]
            self._jumped = True
            self.level.game.play_snd('hit', conf.SOUND_VOLUMES['jump'])
        elif held and self.jumping and not self._jumped:
            # continue jumping
            self.vel[1] -= conf.JUMP_CONTINUE[ident]
            self._jumped = True
            self._jump_time -= 1
            if self._jump_time <= 0:
                self.jumping = False

    def dirty_rect (self):
        return (self.rect, self._old_rect)

    def update (self):
        # jumping
        if self.jumping and not self._jumped:
            self.jumping = False
        self._jumped = False
        # vel
        self._old_rect = self.rect.copy()
        v = self.vel
        v[0] += self._to_move[1] - self._to_move[0]
        self._to_move = [False, False]
        v[1] += conf.GRAVITY
        damp = conf.FRICTION if self.on_ground else conf.AIR_RESISTANCE
        for i in (0, 1):
            v[i] *= damp[i]
        # pos
        self.on_ground = False
        self.move_by(v)


class Player (MovingEntity):
    imgs = ('', 'standleft', 'right', 'left', 'villain', 'villainstandleft',
            'villainright', 'villainleft')
    anims = dd(5)
    img_rect = pg.Rect(0, 0, 20, 40)

    def __init__ (self, level, pos):
        MovingEntity.__init__(self, level, pos)
        self.villain = False
        self._extra_collide_es = self.level.barriers + [self.level.goal]
        self.dead = False
        self._walking = -1
        self._moved = False

    def update_img (self):
        w = self._walking
        img = 'villain' if self.villain else ''
        if w >= 0:
            img += ('left', 'right')[w]
        else:
            img += ('standleft', '')[w + 2]
        self.set_img(img)

    def move (self, dirn, held):
        if self.dead:
            return
        if dirn in (0, 2):
            if held:
                dirn /= 2
                if self._walking != dirn:
                    self._walking = dirn
                    self.update_img()
                    self.start_anim()
                self._moved = True
                self.run(dirn)
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

    def collide (self, e, axis, dirn):
        MovingEntity.collide(self, e, axis, dirn)
        if e.__class__ in SOLID_ES and not (isinstance(e, Enemy) and e.dead):
            return True
        elif isinstance(e, Barrier) and e.on and not self.villain:
            self.die()
        elif isinstance(e, Goal) and not self.dead:
            # stop moving
            self.dead = True
            self.level.win()

    def update (self):
        MovingEntity.update(self)
        if not self._moved:
            if self._walking >= 0:
                self._walking -= 2
            self.stop_anim()
            self.update_img()
        else:
            self._moved = False


class Enemy (MovingEntity):
    imgs = ('', 'right')
    anims = dd(5)
    img_rect = pg.Rect(0, 0, 16, 18)

    def __init__ (self, level, pos):
        MovingEntity.__init__(self, level, pos)
        self.colour = (255, 255, 255)
        self._extra_collide_es = self.level.barriers
        self._seeking = False
        self._los_time = 0
        self._initial_rect = self.rect.copy()
        self._blocked = False
        self.dead = False
        self._walking = False
        self._moved = False

    def collide (self, e, axis, dirn):
        if self.dead:
            return isinstance(e, SolidRect)
        MovingEntity.collide(self, e, axis, dirn)
        if isinstance(e, Player) and (axis == 0 or dirn == 1) and not e.villain:
            e.die()
        elif e.__class__ in SOLID_ES and not (isinstance(e, Enemy) and e.dead):
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
        if dp[0] != 0:
            dirn = int(dp[0] > 0)
            if self._walking is not dirn:
                self._walking = dirn
                self.set_img(('', 'right')[dirn])
                self.start_anim()
            self._moved = True
            self.run(dirn)
        if self._blocked or self.jumping:
            self.jump(self.jumping)

    def update (self):
        self._blocked = False
        self._los_time -= 1
        MovingEntity.update(self)
        if self.dead:
            return
        if not self._moved and self._walking is not False:
            self._walking = False
            self.stop_anim()
        else:
            self._moved = False
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
            max_dist = conf.STOP_SEEK if self._seeking else conf.START_SEEK
            if dist > max_dist:
                los = False
            if los:
                self._los_time = conf.SEEK_TIME
            # determine whether to chase the player
            if self._seeking:
                if self._los_time <= 0:
                    self._seeking = False
            elif dist <= conf.START_SEEK and los:
                self.level.game.play_snd('alert-guard')
                self._seeking = True
            if self._seeking:
                self._move_towards(dp)
        if not self._seeking:
            (pos0, pos1), dp, dist = self.dist(self._initial_rect)
            if abs(dp[0]) > conf.STOP_RETURN:
                self._move_towards(dp)


SOLID_ES = (Player, Enemy, SolidRect, pg.Rect)
