import pygame as pg

from conf import conf
from util import scale_up
from entity import Player
from game.ext import evthandler as eh


class Level (object):
    def __init__ (self, game, event_handler, ident = 0):
        self.game = game
        event_handler.add_key_handlers([
            (conf.KEYS_LEFT, [(self._move, (0,))], eh.MODE_HELD),
            (conf.KEYS_UP, [(self._move, (1, False))], eh.MODE_ONDOWN),
            (conf.KEYS_UP, [(self._move, (1,))], eh.MODE_HELD),
            (conf.KEYS_RIGHT, [(self._move, (2,))], eh.MODE_HELD),
            #(conf.KEYS_LEFT, [(self._move, (0,))], eh.MODE_HELD),
        ])
        self.ident = ident
        self.init()

    def init (self):
        data = conf.LEVELS[self.ident]
        self.player = Player(data['pos'])
        self.enemies = []
        self.solid = [pg.Rect(scale_up(r)) for r in data.get('solid', [])]

    def _move (self, k, t, m, dirn, held = True):
        self.player.move(dirn, held)

    def _collide (self, r1, r2):
        x01, y01, w1, h1 = r1
        x02, y02, w2, h2 = r2
        col_data = ((x01 + w1) - x02, (y01 + h1) - y02, (x02 + w2) - x01,
                    (y02 + h2) - y01)
        col_data = [x for x in col_data if x > 0]
        return col_data if len(col_data) == 4 else False

    def _resolve (self, e, col_data):
        x = min(col_data)
        i = col_data.index(x)
        dp = [0, 0]
        dp[i % 2] = (1 if i >= 2 else -1) * x
        e.move_by(dp)
        if i == 1:
            e.on_ground = True

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

    def update (self):
        self.player.update()
        self._handle_collisions()

    def draw (self, screen):
        self.player.pre_draw()
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
