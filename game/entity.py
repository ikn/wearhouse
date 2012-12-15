import pygame as pg

from conf import conf
from util import ir, scale_up


class Entity (object):
    def __init__ (self, pos, size):
        self.pos = pos = scale_up(pos)
        self.size = list(size)
        ts = conf.TILE_SIZE
        # move to centre of bottom edge of lower tile
        pos[0] += (ts - (size[0] % ts)) / 2
        pos[1] -= size[1]
        self._update_draw_rect()

    def _update_draw_rect (self):
        self.draw_rect = pg.Rect((ir(self.pos[0]), ir(self.pos[1])), self.size)

    def draw (self, screen):
        screen.fill(self.colour, self.draw_rect)


class MovingEntity (Entity):
    def move_by (self, dp):
        p = self.pos
        p[0] += dp[0]
        p[1] += dp[1]
        self.rect = p + self.size

    def dirty_rect (self):
        return self.draw_rect.union(self._old_draw_rect)

    def update (self):
        # vel
        v = self.vel
        v[0] += self._to_move[1] - self._to_move[0]
        self._to_move = [False, False]
        v[1] += conf.GRAVITY
        damp = conf.FRICTION if self.on_ground else conf.AIR_RESISTANCE
        for i in (0, 1):
            v[i] *= damp[i]
        # pos
        self.move_by(v)
        self.on_ground = False

    def pre_draw (self):
        self._old_draw_rect = self.draw_rect
        self._update_draw_rect()


class Player (MovingEntity):
    def __init__ (self, pos):
        Entity.__init__(self, pos, conf.PLAYER_SIZE)
        # some initial values
        self.vel = [0, 0]
        self.on_ground = False
        self._to_move = [False, False]
        self.colour = (200, 50, 50)
        self.jumping = False
        self._jump_time = 0
        self._jumped = False

    def update (self):
        # jumping
        if self.jumping and not self._jumped:
            self.jumping = False
        self._jumped = False
        MovingEntity.update(self)

    def move (self, dirn, held):
        if dirn in (0, 2):
            if held:
                speed = conf.MOVE_SPEED if self.on_ground else conf.MOVE_SPEED_AIR
                self._to_move[dirn / 2] = speed
        elif dirn == 1:
            if not held and not self.jumping and self.on_ground:
                # start jumping
                self.vel[1] -= conf.JUMP_INITIAL
                self.jumping = True
                self._jump_time = conf.JUMP_TIME
                self._jumped = True
            elif held and self.jumping and not self._jumped:
                # continue jumping
                self.vel[1] -= conf.JUMP_CONTINUE
                self._jumped = True
                self._jump_time -= 1
                if self._jump_time <= 0:
                    self.jumping = False
