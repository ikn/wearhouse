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
            (conf.KEYS_RESET, self._real_restart, eh.MODE_ONDOWN)
        ])
        self.ident = ident
        self.rect = pg.Rect((0, 0), [conf.TILE_SIZE * x for x in conf.LEVEL_SIZE])
        game.linear_fade(*conf.START_FADE)
        self.bg = pg.Surface(conf.RES)
        self._last_ident = None
        self.init()

    def init (self):
        data = conf.LEVELS[self.ident]
        if self._last_ident != self.ident:
            # don't reinitialise if on the same level so random tiles don't change
            entity.BG(self, (0, 0) + conf.BG_SIZE).draw(self.bg)
            self.changers = [entity.Changer(self, pos) for pos in data.get('changers', [])]
            self.barriers = bs = [entity.Barrier(self, r) for r in data.get('barriers', [])]
            self.goal = entity.Goal(self, data['goal'])
            self.solid = [entity.SolidRect(self, r) for r in data.get('solid', [])]
        else:
            bs = self.barriers
            for b in bs:
                b.on = True
        # switches have changeable state I can't be bothered to reset
        self.switches = [entity.Switch(self, pos, bs[b]) for pos, b in data.get('switches', [])]
        self.nonsolid = self.changers + self.barriers + self.switches + [self.goal]
        self.player = entity.Player(self, data['player'])
        self.enemies = [entity.Enemy(self, pos) for pos in data.get('enemies', [])]
        self.moving = self.enemies + [self.player]
        self.dirty = True
        self._restart = False
        self._win = False
        self._winning = False
        self._last_ident = self.ident

    def _real_restart (self, *args):
        self._restart = True

    def restart (self):
        self.game.scheduler.add_timeout(self._real_restart, seconds = conf.RESTART_TIME)
        self.game.linear_fade(*conf.RESTART_FADE)

    def _real_win (self):
        self._win = True

    def win (self):
        if not self._winning:
            self._winning = True
            self.game.scheduler.add_timeout(self._real_win, seconds = conf.WIN_TIME)
            self.game.linear_fade(*conf.WIN_FADE)
            self.game.play_snd('door')
            self.goal.start_anim(0)

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
            screen.blit(self.bg, (0, 0))
            for e in self.solid:
                e.draw(screen)
        else:
            for e in self.moving:
                for r in e.dirty_rect():
                    rects.append(r)
            for e in self.nonsolid:
                if e.dirty:
                    rects.append(e.rect)
                    e.dirty = False
            for r in rects:
                screen.blit(self.bg, r, r)
        for e in self.nonsolid + self.moving:
            e.draw(screen)
        if self.dirty:
            self.dirty = False
            return True
        else:
            return rects
