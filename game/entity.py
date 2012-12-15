import pygame as pg

from conf import conf
from util import ir, scale_up


class SolidRect (object):
    def __init__ (self, rect):
        self.rect = pg.Rect(scale_up(rect))
        self.colour = (0, 0, 0)

    def draw (self, screen):
        screen.fill(self.colour, self.rect)


class Entity (object):
    def __init__ (self, pos, size):
        pos = scale_up(pos)
        ts = conf.TILE_SIZE
        # move to centre of bottom edge of lower tile
        pos[0] += (ts - (size[0] % ts)) / 2
        pos[1] -= size[1]
        x, y = pos
        ix, iy = ir(x), ir(y)
        self.overflow = (x - ix, y - iy)
        self.rect = pg.Rect((ix, iy), size)

    def draw (self, screen):
        screen.fill(self.colour, self.rect)


class MovingEntity (Entity):
    def __init__ (self, level, pos, size):
        self.level = level
        Entity.__init__(self, pos, size)
        # some initial values
        self.vel = [0, 0]
        self.on_ground = False
        self._to_move = [False, False]
        self.jumping = False
        self._jump_time = 0
        self._jumped = False

    def collide (self, e, axis, dirn):
        if e.__class__ in SOLID_ES:
            if axis == 1 and dirn == 1:
                self.on_ground = True
            return True

    def move_by (self, dp):
        # move and handle collisions
        collide = self.collide
        es = self.level.moving + self.level.static
        es.remove(self)
        o = self.overflow
        r = self.rect
        p = [r[0] + o[0] + dp[0], r[1] + o[1] + dp[1]]
        dest = [ir(p[0]), ir(p[1])]
        self.overflow = (p[0] - dest[0], p[1] - dest[1])
        for axis in (0, 1):
            dx = dest[axis] - r[axis]
            if dx == 0:
                continue
            dirn = 1 if dx > 0 else -1
            while dx != 0:
                r[axis] += dirn
                dx -= dirn
                col_es = [e for e in es if r.colliderect(e.rect)]
                if any(collide(e, axis, dirn) for e in col_es):
                    r[axis] -= dirn
                    break

    def run (self, dirn):
        ident = self.__class__.__name__.lower()
        speed = conf.MOVE_SPEED[ident] if self.on_ground else conf.MOVE_SPEED_AIR[ident]
        self._to_move[dirn] = speed

    def jump (self, held):
        ident = self.__class__.__name__.lower()
        if not held and not self.jumping and self.on_ground:
            # start jumping
            self.vel[1] -= conf.JUMP_INITIAL[ident]
            self.jumping = True
            self._jump_time = conf.JUMP_TIME[ident]
            self._jumped = True
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


class Enemy (MovingEntity):
    def __init__ (self, level, pos):
        MovingEntity.__init__(self, level, pos, conf.ENEMY_SIZE)
        self.colour = (50, 50, 50)
        self.seeking = False
        self._initial_rect = self.rect.copy()
        self._blocked = False

    def collide (self, e, axis, dirn):
        MovingEntity.collide(self, e, axis, dirn)
        if isinstance(e, Player) and axis == 0:
            e.die()
        elif e.__class__ in SOLID_ES:
            if axis == 0:
                self._blocked = True
            return True

    def dist (self, rect):
        pos = self.rect.center
        other_pos = rect.center
        dx = other_pos[0] - pos[0]
        dy = (other_pos[1] - pos[1])
        return ((dx, dy), (dx * dx + dy * dy) ** .5)

    def _move_towards (self, dp):
        if dp[0] != 0:
            self.run(dp[0] > 0)
        if self._blocked:
            self.jump(self.jumping)

    def update (self):
        self._blocked = False
        MovingEntity.update(self)
        player = self.level.player
        if not player.villain:
            # TODO: instead of distance, start seeking if can see player, stop
            #       if couldn't for SEEK_STOP_TIME
            dp, dist = self.dist(player.rect)
            if self.seeking:
                if dist > conf.STOP_SEEK:
                    self.seeking = False
            elif dist <= conf.START_SEEK:
                self.seeking = True
            if self.seeking:
                self._move_towards(dp)
        if not self.seeking:
            dp, dist = self.dist(self._initial_rect)
            if dist > conf.STOP_RETURN:
                self._move_towards(dp)


class Player (MovingEntity):
    def __init__ (self, level, pos):
        MovingEntity.__init__(self, level, pos, conf.PLAYER_SIZE)
        self.colour = (200, 50, 50)
        self.villain = False

    def move (self, dirn, held):
        if dirn in (0, 2):
            if held:
                self.run(dirn / 2)
        elif dirn == 1:
            self.jump(held)

    def die (self):
        self.level.restart()

    def collide (self, e, axis, dirn):
        MovingEntity.collide(self, e, axis, dirn)
        if e.__class__ in SOLID_ES:
            return True


SOLID_ES = (Player, Enemy, SolidRect)
