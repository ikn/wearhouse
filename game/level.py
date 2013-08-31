import pygame as pg
from pygame import Rect

from .engine import conf, evt, gfx, util
from .engine.game import World

from .conf import Conf
from . import entity

conf.add(Conf)


def mk_tilemap (ident, *rects, **kwargs):
    # generate a random tilemap from an ident and rects, with keyword-only
    # size=conf.RES
    sfc_size = kwargs.get('size', conf.RES)
    ts = conf.TILE_SIZE[ident]
    assert sfc_size[0] % ts == 0 and sfc_size[1] % ts == 0
    size = (sfc_size[0] / ts, sfc_size[1] / ts)
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
    def init (self, ident, bg=None, wall_graphic=None):
        self.rect = Rect((0, 0), conf.RES)
        data = conf.LEVELS[ident]

        # tilemaps (don't reinitialise if on the same level so random tiles
        # don't change)
        if bg is None:
            ts = conf.TILE_SIZE['bg']
            bg = mk_tilemap('bg',
                            ((0, 0), (conf.RES[0] / ts, conf.RES[1] / ts)))
            bg.layer = conf.LAYERS['bg']
        self._bg = bg
        if wall_graphic is None:
            wall_graphic = mk_tilemap('wall', *data.get('walls', []))
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
        eh['reset'].cb(self.reset)
        for action in ('walk', 'jump', 'use'):
            eh[action].cb(getattr(self.player, action))

    def pause (self, secret=False):
        conf.GAME.start_world(Paused, self.graphics.surface, secret)

    def reset (self):
        # TODO
        pass


class Paused (World):
    def init (self, sfc, secret):
        eh = self.evthandler
        eh.load('paused')
        eh['continue'].cb(lambda: conf.GAME.quit_world(1))
        eh['quit'].cb(lambda: conf.GAME.quit_world(2))

        self.graphics.add(gfx.Graphic(sfc.convert(), layer=1))
        if not secret:
            self.graphics.add(
                gfx.Colour(conf.PAUSE_DIM, self.graphics.size),
                gfx.Graphic('paused.png', layer=-1)
            )[1].align()
