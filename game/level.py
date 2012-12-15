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
            #(conf.KEYS_LEFT, [(self._move, (0,))], eh.MODE_HELD),
        ])
        self.ident = ident
        self.init()

    def init (self):
        data = conf.LEVELS[self.ident]
        self.player = entity.Player(self, data['pos'])
        self.enemies = [entity.Enemy(self, pos) for pos in data['enemies']]
        self.moving = [self.player] + self.enemies
        self.rects = [entity.SolidRect(r) for r in data.get('solid', [])]
        self.static = self.rects

    def _move (self, k, t, m, dirn, held = True):
        self.player.move(dirn, held)

    def update (self):
        for e in [self.player] + self.enemies:
            e.update()

    def draw (self, screen):
        rects = []
        if self.dirty:
            screen.fill((255, 255, 255))
            for e in self.static:
                e.draw(screen)
        else:
            for e in self.moving:
                r = e.dirty_rect()
                rects.append(r)
                screen.fill((255, 255, 255), r)
        for e in self.moving:
            e.draw(screen)
        if self.dirty:
            self.dirty = False
            return True
        else:
            return rects
