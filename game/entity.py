import pygame as pg

from .engine import conf, gfx, entity, util
from .engine.gfx.util import Spritemap


class Entity (entity.Entity):
    # .ident: identifier string derived from class name
    # .rect: pygame.Rect used for collision detection

    def __init__ (self, *args, **kwargs):
        entity.Entity.__init__(self)
        self.ident = self.__class__.__name__.lower()
        self.graphic = None
        self.init(*args, **kwargs)
        if self.graphic is not None:
            self.graphic = self.graphics.add(self.graphic)[0]
            self.graphics.layer = conf.LAYERS[self.ident]

    def init (self):
        pass

    def added (self):
        # TODO: remove once GraphicView is fixed
        if self.graphic is not None:
            self.graphic.scheduler = self.world.scheduler

    def solid_to (self, e):
        return self.ident in conf.SOLID_ENTITIES[e.ident]


class Rect (Entity):
    # subclasses have .rect available in .init() (and may alter it)

    def __init__ (self, rect, *args, **kwargs):
        rect = pg.Rect(rect)
        ts = conf.TILE_SIZE['wall']
        graphics_rect = pg.Rect([x * ts for x in rect])
        self.rect = graphics_rect.copy()
        Entity.__init__(self, *args, **kwargs)
        if self.graphic is not None:
            self.graphics.pos = graphics_rect.topleft


class NonRect (Entity):
    def __init__ (self, pos, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)
        # align .rect within the tile we're placed in
        ts = conf.TILE_SIZE['wall']
        size = conf.ENTITY_SIZE[self.ident]
        # centre horizontally
        x = pos[0] * ts + (ts - size[0]) / 2
        # align bottoms
        y = pos[1] * ts - size[1]
        self.rect = pg.Rect((x, y), size)
        if self.graphic is not None:
            # align graphics with collision rect
            self.graphics.pos = util.align_rect(self.graphic.rect, self.rect,
                                                (0, 1))
            self.graphics.anchor = 'midbottom'


class MovingEntity (NonRect):
    # subclasses must implement .update_graphics() to do so when state changes

    def __init__ (self, *args, **kwargs):
        NonRect.__init__(self, *args, **kwargs)
        self.vel = [0, 0]
        self.overflow = [0, 0]
        self.on_ground = None # entity ident
        self.walking = False
        self.dirn = -1
        self._to_move = [0, 0]
        self.jumping = False
        self._jump_time = 0
        self._jumped = False
        self._autojump_cooldown = 0
        self._extra_collide_es = [] # non-solid entities to collide with
        self._step_snd_counter = 0

    def walk (self, dirn):
        # dirn is 0 (left) or 1 (right)
        # handle both directions together when we update
        self._to_move[dirn] = 1

    def collide (self, e, axis, dirn):
        # collision callback; axis is 0 or 1, dirn is -1 or 1; returns whether
        # to stop moving on this collision
        if e.solid_to(self):
            if axis and dirn == 1:
                self.on_ground = e.ident
            return True

    def move_graphics (self, dx, dy):
        self.graphics.move_by(dx, dy)

    def move_by (self, dp):
        # move and handle collisions
        collide = self.collide
        in_bounds = self.world.rect.contains
        es = self.world.solid + self._extra_collide_es
        es.remove(self)
        o = self.overflow
        r = self.rect
        orig_x, orig_y = r.topleft
        # get where to move to
        x = r.x + o[0] + dp[0]
        y = r.y + o[1] + dp[1]
        dest = [util.ir(x), util.ir(y)]
        self.overflow = o = [x - dest[0], y - dest[1]]
        # collide
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
                    col_es.append(self.world.bdy)
                if any(collide(e, axis, dirn) for e in col_es):
                    # stop moving (move back first)
                    r[axis] -= dirn
                    o[axis] = 0
                    self.vel[axis] = 0
                    break
        self.move_graphics(r.x - orig_x, r.y - orig_y)

    def update (self):
        # vel
        v = self.vel
        speed = (conf.MOVE_SPEED[self.ident]
                 if self.on_ground else conf.MOVE_SPEED_AIR[self.ident])
        dirn = self._to_move[1] - self._to_move[0]
        self._to_move = [0, 0]
        v[0] += speed * dirn
        v[1] += conf.GRAVITY
        damp = conf.FRICTION if self.on_ground else conf.AIR_RESISTANCE
        for i in (0, 1):
            v[i] *= damp[i]
        # pos
        self.on_ground = False
        self.move_by(v)
        # walk sound
        if dirn != 0 and self.on_ground:
            self._step_snd_counter -= 1
            if self._step_snd_counter <= 0:
                self._step_snd_counter = conf.STEP_SOUND_TIME[self.ident]
                conf.GAME.play_snd('hit', conf.SOUND_VOLUMES['step'])
        # animation
        if dirn == 0:
            if self.walking:
                # stop walking
                self.walking = False
                self.update_graphics()
        else:
            old_dirn = self.dirn
            self.dirn = dirn
            if not self.walking:
                # start walking
                self.walking = True
                self.update_graphics()
            elif old_dirn != dirn:
                # change direction
                self.update_graphics()


class Player (MovingEntity):
    def init (self):
        self.outfit = 'hero'
        self.dead = False

        self.graphic = g = gfx.Animation(sum([
            ['player-' + outfit + '-left.png',
            'player-' + outfit + '-right.png'] +
            list(Spritemap('player-' + outfit + '-walkleft.png', 4)) +
            list(Spritemap('player-' + outfit + '-walkright.png', 4))
        for outfit in ('hero', 'villain')], []))
        for outfit in ('hero', 'villain'):
            i = 0 if outfit == 'hero' else 10
            g.add(outfit + 'left', i + 0).add(outfit + 'right', i + 1)
            g.add(outfit + 'walkleft', *xrange(i + 2, i + 6))
            g.add(outfit + 'walkright', *xrange(i + 6, i + 10))
            g.frame_time = conf.ANIMATION_TIMES[self.ident]

    def added (self):
        MovingEntity.added(self)
        self._extra_collide_es = self.world.barriers + [self.world.goal]

    def update_graphics (self):
        # change to the correct animation based on .walking/.dirn
        self.graphic.play(self.outfit + ('walk' if self.walking else '') +
                          ('left' if self.dirn == -1 else 'right'))

    def walk (self, dirn, evt):
        if self.dead:
            return
        MovingEntity.walk(self, dirn)

    def use (self, evt):
        # use nearby items
        r = self.rect
        if any(r.colliderect(c.rect) for c in self.world.changers):
            conf.GAME.play_snd('change')
            self.outfit = 'villain' if self.outfit == 'hero' else 'hero'
            self.update_graphics()
        for s in self.world.switches:
            if r.colliderect(s.rect):
                s.toggle()

    def collide (self, e, axis, dirn):
        stopped = MovingEntity.collide(self, e, axis, dirn)
        if self.dead:
            return stopped
        elif stopped:
            return True
        elif isinstance(e, Barrier) and e.on and self.outfit == 'hero':
            self.die()
        elif isinstance(e, Goal):
            # stop moving
            self.dead = True
            self.world.goal.open()
            # TODO: self.world.win()

    def die (self):
        if not self.dead:
            self.dead = True
            # TODO: self.world.restart()
            conf.GAME.play_snd('die')


class Enemy (MovingEntity):
    def init (self):
        self.graphic = g = gfx.Animation(
            list(Spritemap('enemy-left.png', 2)) +
            list(Spritemap('enemy-right.png', 2))
        )
        g.add('left', 0).add('walkleft', 0, 1)
        g.add('right', 2).add('walkright', 2, 3)
        g.frame_time = conf.ANIMATION_TIMES[self.ident]


class Goal (NonRect):
    def init (self):
        self.graphic = g = gfx.Animation(Spritemap('goal.png', 6))
        g.add('open')
        g.frame_time = conf.ANIMATION_TIMES[self.ident]

    def open (self):
        self.graphic.play('open', 0)


class Changer (NonRect):
    def init (self):
        self.graphic = gfx.Graphic('changer.png')


class Barrier (Rect):
    def init (self):
        deflate = conf.BARRIER_DEFLATE
        self.graphic = gfx.Colour(conf.BARRIER_COLOUR, self.rect.size)
        self.rect = self.rect.inflate(-deflate, -deflate)
        self.on = True

    def toggle (self):
        self.on = not self.on
        self.graphics.visible = self.on


class Switch (NonRect):
    def init (self, barrier):
        self._barrier = barrier
        self.graphic = gfx.Animation(('switch-on.png', 'switch-off.png'))
        self.on = True

    def toggle (self):
        conf.GAME.play_snd('lever')
        self._barrier.toggle()
        self.on = not self.on
        self.graphic.graphic = not self.on


class Wall (Rect):
    pass


class Boundary (Rect):
    pass
