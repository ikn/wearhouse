import pygame as pg
from pygame import Rect

from .engine import conf, evt, gfx, util
from .engine.game import World

from .conf import Conf
from . import entity

conf.add(Conf)


def mk_tilemap (ident, *rects, **kwargs):
    # generate a random tilemap from an ident and rects, with keyword-only size
    sfc_size = kwargs.get('size')
    ts = conf.TILE_SIZE[ident]
    assert sfc_size[0] % ts == 0 and sfc_size[1] % ts == 0
    size = (sfc_size[0] // ts, sfc_size[1] // ts)
    freqs = dict(('{0}{1}.png'.format(ident, i), freq)
                 for i, freq in enumerate(conf.TILE_FREQS[ident]))

    tile_data = [[None for j in xrange(size[1])] for i in xrange(size[0])]
    for r in rects:
        r = Rect(r)
        for i in xrange(r.left, r.right):
            for j in xrange(r.top, r.bottom):
                tile_data[i][j] = util.weighted_rand(freqs)

    return gfx.Tilemap(ts, tile_data)


class Level (World):
    def init (self, ident=0, evt='start', bg=None, wall_graphic=None):
        # might get a negative number, which breaks progression
        self._ident = ident % len(conf.LEVELS)
        self._won = False
        size = self.graphics.orig_size
        self.rect = Rect((0, 0), size)
        data = conf.LEVELS[ident]

        # tilemaps: use existing ones if passed
        if bg is None:
            ts = conf.TILE_SIZE['bg']
            bg = mk_tilemap('bg', ((0, 0), (size[0] / ts, size[1] / ts)),
                            size=size)
            bg.layer = conf.LAYERS['bg']
        self._bg = bg
        if wall_graphic is None:
            wall_graphic = mk_tilemap('wall', *data.get('walls', []),
                                      size=size)
            wall_graphic.layer = conf.LAYERS['wall']
        self._wall_graphic = wall_graphic
        self.graphics.add(bg, wall_graphic)

        # entities
        self.player = entity.Player(data['player'])
        enemies = [entity.Enemy(pos) for pos in data.get('enemies', [])]
        self.goal = entity.Goal(data['goal'])
        self.changers = [entity.Changer(pos)
                         for pos in data.get('changers', ())]
        self.barriers = bs = [entity.Barrier(r)
                              for r in data.get('barriers', [])]
        self.switches = [entity.Switch(pos, bs[b])
                         for pos, b in data.get('switches', [])]
        walls = [entity.Wall(r) for r in data.get('walls', [])]
        self.bdy = entity.Boundary(self.rect)
        self.solid = [self.player] + enemies + walls
        self.moving = [self.player] + enemies
        self.add(self.player, enemies, self.goal, self.changers, self.barriers,
                 self.switches, walls, self.bdy)

        # controls
        eh = self.evthandler
        eh.load('game')
        eh['pause'].cb(lambda: self.pause(False))
        eh['secret_pause'].cb(lambda: self.pause(True))
        eh['reset'].cb(lambda: self.reset())
        for action in ('walk', 'jump', 'use'):
            eh[action].cb(getattr(self.player, action))

        # fade in
        if evt == 'start':
            self.graphics.fade_from(*conf.START_FADE_IN)
        elif evt == 'died':
            self.graphics.fade_from(*conf.DIE_FADE_IN)

    def pause (self, secret=False):
        conf.GAME.start_world(Paused, self.graphics.surface, secret)

    def reset (self, died=False):
        # immediately reset the level (starts a new world)
        # don't allow restart while winning
        if self._won:
            return
        if died:
            # stop all sounds but the dying sound
            # TODO
            #conf.GAME.stop_snd('die', exclude=True)
            pass
        else:
            # manual reset while dying: stop all sounds
            # TODO
            #conf.GAME.stop_snd()
            pass
        # don't regenerate tilemaps if on the same level so random tiles don't
        # change
        conf.GAME.switch_world(Level, self._ident, 'died' if died else None,
                               self._bg, self._wall_graphic)

    def die (self):
        # player died: reset with fade
        # don't allow restart while winning
        if self._won:
            return
        self.graphics.fade_to(*conf.DIE_FADE_OUT)
        self.scheduler.add_timeout(lambda: self.reset(True), conf.DIE_TIME)

    def progress (self):
        # progress to the next level
        i = self._ident + 1
        if i == len(conf.LEVELS):
            # no levels remaining
            conf.GAME.switch_world(End)
        else:
            # only generate bg once per game, for speed
            conf.GAME.switch_world(Level, i, bg=self._bg)

    def _real_win (self):
        self.graphics.fade_to(*conf.WIN_FADE_OUT)
        self.scheduler.add_timeout(self.progress, conf.WIN_TIME)

    def win (self):
        # progress with fade
        self._won = True
        # wait for lift doors to open a little
        self.scheduler.add_timeout(self._real_win, conf.WIN_DELAY)


class Paused (World):
    def init (self, sfc, secret):
        eh = self.evthandler
        eh.load('paused')
        eh['continue'].cb(lambda: conf.GAME.quit_world(1))
        eh['quit'].cb(lambda: conf.GAME.quit_world(2))

        self.graphics.add(gfx.Graphic(sfc.convert(), layer=1))
        if not secret:
            self.graphics.add(
                gfx.Colour(conf.PAUSE_DIM, self.graphics.orig_size),
                gfx.Graphic('paused.png', layer=-1)
            )[1].align()


class End (World):
    def init (self):
        self.graphics.add(gfx.Graphic('end.png'))[0].align()
        self.graphics.fade_from(*conf.END_FADE_IN)
        # allow input after a delay to avoid clicking through
        self.scheduler.add_timeout(self._init_input, conf.END_INPUT_DELAY)

    def _init_input (self):
        self.evthandler.load('end')
        self.evthandler['continue'].cb(self.restart)

    def restart (self):
        self.graphics.fade_to(*conf.END_FADE_OUT)
        self.scheduler.add_timeout(lambda: conf.GAME.switch_world(Level),
                                   conf.END_CONTINUE_TIME)
