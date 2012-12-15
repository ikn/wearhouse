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
        self._update_rect(pos)

    def _update_rect (self, pos):
        self.rect = self.pos + self.size
        self.draw_rect = pg.Rect((ir(pos[0]), ir(pos[1])), self.size)


class MovingEntity (Entity):
    def dirty_rect (self):
        return self.draw_rect.union(self._old_draw_rect)

    def update (self):
        v = self.vel
        p = self.pos
        # update vel
        v[0] += self._to_move
        self._to_move = 0
        v[1] += conf.GRAVITY
        damp = conf.FRICTION if self.on_ground else conf.AIR_RESISTANCE
        for i in (0, 1):
            v[i] *= damp[i]
        # update pos
        p[0] += v[0]
        p[1] += v[1]
        self._old_draw_rect = self.draw_rect
        self._update_rect(p)

    def draw (self, screen):
        screen.fill(self.colour, self.draw_rect)


class Player (MovingEntity):
    def __init__ (self, pos):
        Entity.__init__(self, pos, conf.PLAYER_SIZE)
        # some initial values
        self.vel = [0, 0]
        self.on_ground = False
        self._to_move = 0
        self.colour = (200, 50, 50)

    def move (self, dirn):
        if dirn in (0, 2):
            speed = conf.MOVE_SPEED if self.on_ground else conf.MOVE_SPEED_AIR
            self._to_move += speed * (dirn - 1)
