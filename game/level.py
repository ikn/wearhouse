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
            (conf.KEYS_JUMP, [(self._move, (1, False))], eh.MODE_ONDOWN),
            (conf.KEYS_JUMP, [(self._move, (1,))], eh.MODE_HELD),
            (conf.KEYS_RIGHT, [(self._move, (2,))], eh.MODE_HELD),
            (conf.KEYS_USE, [(self._move, (3,))], eh.MODE_ONDOWN),
            (conf.KEYS_RESET, self._force_restart, eh.MODE_ONDOWN),
            (conf.KEYS_BACK, lambda *args: game.quit_backend(), eh.MODE_ONDOWN)
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
            # don't reinitialise bg/solid rects if on the same level so random tiles don't change
            self.changers = [entity.Changer(self, pos) for pos in data.get('changers', [])]
            self.barriers = bs = [entity.Barrier(self, r) for r in data.get('barriers', [])]
            self.goal = entity.Goal(self, data['goal'])
            # draw tiles (solid and nonsolid) to bg image for speed
            entity.BG(self, (0, 0) + conf.BG_SIZE).draw(self.bg)
            self.solid = [entity.SolidRect(self, r) for r in data.get('solid', [])]
            for r in self.solid:
                r.draw(self.bg)
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
        self._restart_timeout_id = None

    def _force_restart (self, *args):
        if not self._winning:
            if self._restart_timeout_id is not None:
                self.game.cancel_fade(False)
                self.game.scheduler.rm_timeout(self._restart_timeout_id)
                self.game.stop_snd('die')
            self._real_restart()

    def _real_restart (self):
        self._restart = True

    def restart (self):
        self._restart_timeout_id = self.game.scheduler.add_timeout(self._real_restart, seconds = conf.RESTART_TIME)
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
                self.game.switch_backend(End)
            else:
                self.init()
        for e in self.moving:
            e.update()

    def draw (self, screen):
        rects = []
        if self.dirty:
            screen.blit(self.bg, (0, 0))
        else:
            for e in self.moving:
                for r in e.dirty_rect():
                    rects.append(r)
            for e in self.nonsolid:
                if e.dirty:
                    rects.append(e.draw_rect)
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


class End:
    def __init__ (self, game, event_handler):
        self.game = game
        self.bg = game.img('end.png')
        event_handler.add_key_handlers([
            (conf.KEYS_NEXT + conf.KEYS_BACK, self.restart, eh.MODE_ONDOWN)
        ])
        game.linear_fade(*conf.START_FADE)

    def _real_restart (self):
        self.game.switch_backend(Level)

    def restart (self, *args):
        self.game.linear_fade(*conf.END_FADE, persist = True)
        self.game.scheduler.add_timeout(self._real_restart, seconds = conf.END_TIME)

    def update (self):
        pass

    def draw (self, screen):
        if self.dirty:
            screen.blit(self.bg, (0, 0))
            self.dirty = False
            return True
        else:
            return False
