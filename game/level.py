import pygame as pg

from conf import conf
from util import scale_up
import entity
from game.ext import evthandler as eh


class Level (object):
    def __init__ (self, game, event_handler, ident = 0):
        self.game = game
        event_handler.add_key_handlers([
            (conf.KEYS_LEFT, [(self._move, (0,))], eh.MODE_HELD),
            (conf.KEYS_UP, [(self._move, (1, False))], eh.MODE_ONDOWN),
            (conf.KEYS_UP, [(self._move, (1,))], eh.MODE_HELD),
            (conf.KEYS_RIGHT, [(self._move, (2,))], eh.MODE_HELD),
            (conf.KEYS_DOWN, [(self._move, (3,))], eh.MODE_ONDOWN),
            (conf.KEYS_RESET, self.restart, eh.MODE_ONDOWN)
        ])
        self.ident = ident
        self.rect = pg.Rect((0, 0), [conf.TILE_SIZE * x for x in conf.LEVEL_SIZE])
        self.init()

    def init (self):
        data = conf.LEVELS[self.ident]
        self.changers = [entity.Changer(pos) for pos in data.get('changers', [])]
        self.barriers = bs = [entity.Barrier(r) for r in data.get('barriers', [])]
        self.switches = [entity.Switch(pos, bs[b]) for pos, b in data.get('switches', [])]
        self.goal = entity.Goal(data['goal'])
        self.nonsolid = self.changers + self.barriers + self.switches + [self.goal]
        self.player = entity.Player(self, data['player'])
        self.enemies = [entity.Enemy(self, pos) for pos in data.get('enemies', [])]
        self.moving = self.enemies + [self.player]
        self.solid = [entity.SolidRect(r) for r in data.get('solid', [])]
        self.dirty = True
        self._restart = False
        self._win = False

    def restart (self, *args):
        self._restart = True

    def win (self):
        self._win = True
        self.game.play_snd('door')

    def _move (self, k, t, m, dirn, held = True):
        self.player.move(dirn, held)

    def update (self):
        if self._restart:
            self.init()
        if self._win:
            self.ident += 1
            if self.ident == len(conf.LEVELS):
                self.game.quit_backend()
            else:
                self.init()
        for e in self.moving:
            e.update()

    def draw (self, screen):
        rects = []
        if self.dirty:
            screen.fill((255, 255, 255))
            for e in self.solid:
                e.draw(screen)
        else:
            for e in self.moving:
                for r in e.dirty_rect():
                    rects.append(r)
            for b in self.barriers:
                if b.dirty:
                    rects.append(b.rect)
                    b.dirty = False
            for r in rects:
                screen.fill((255, 255, 255), r)
        for e in self.nonsolid + self.moving:
            e.draw(screen)
        if self.dirty:
            self.dirty = False
            return True
        else:
            return rects
