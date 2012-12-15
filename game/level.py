import pygame as pg

from conf import conf
from util import scale_up
from entity import Player
from game.ext import evthandler as eh


class Level (object):
    def __init__ (self, game, event_handler, ident = 0):
        self.game = game
        event_handler.add_key_handlers([
            (conf.KEYS_DIRN[i], [(self._move, (i,))], eh.MODE_HELD)
            for i in xrange(4)
        ])
        self.ident = ident
        self.init()

    def init (self):
        data = conf.LEVELS[self.ident]
        self.player = Player(data['pos'])
        self.enemies = []
        self.solid = [pg.Rect(scale_up(r)) for r in data.get('solid', [])]

    def _move (self, k, t, m, dirn):
        self.player.move(dirn)

    def _collide (self, r1, r2):
        return False

    def _resolve (self, e, r):
        pass

    def _handle_collisions (self):
        # resolve collisions with solid objects
        p = self.player
        es = self.enemies
        solid = self.solid
        collide = self._collide
        resolve = self._resolve
        for e in [p] + es:
            for r in solid:
                col_data = collide(e.rect, r)
                if col_data:
                    resolve(e, col_data)
        # handle player collisions with other objects
        for e in es:
            if collide(p.rect, e.rect):
                p.die()

    def update (self):
        self.player.update()
        self._handle_collisions()

    def draw (self, screen):
        rects = []
        if self.dirty:
            screen.fill((255, 255, 255))
            for r in self.solid:
                screen.fill((0, 0, 0), r)
        else:
            r = self.player.dirty_rect()
            rects.append(r)
            screen.fill((255, 255, 255), r)
        self.player.draw(screen)
        if self.dirty:
            self.dirty = False
            return True
        else:
            return rects
