import pygame as pg

from .engine import conf, gfx, entity, util
from .engine.gfx.util import Spritemap


class Entity (entity.Entity):
    # .ident: identifier string derived from class name
    # .rect: pygame.Rect used for collision detection
    def __init__ (self, *args, **kwargs):
        entity.Entity.__init__(self)
        self.ident = self.__class__.__name__.lower()
        self.graphic = None
        self.init(*args, **kwargs)
        if self.graphic is not None:
            self.graphics.add(self.graphic)
            self.graphics.layer = conf.LAYERS[self.ident]

    def init (self):
        pass

    @property
    def solid (self):
        return self.ident in conf.SOLID_ENTITIES


class NonRect (Entity):
    def __init__ (self, pos, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)
        # align .rect within the tile we're placed in
        ts = conf.TILE_SIZE['wall']
        size = conf.ENTITY_SIZE[self.ident]
        # centre horizontally
        x = pos[0] * ts + (ts - size[0]) / 2
        # align bottoms
        y = pos[1] * ts - size[1]
        self.rect = pg.Rect((x, y), size)
        if self.graphic is not None:
            # align graphics with collision rect
            self.graphics.pos = util.align_rect(self.graphic.rect, self.rect,
                                                (0, 1))
            self.graphics.anchor = 'midbottom'


class Rect (Entity):
    # subclasses have .rect available in .init() (and may alter it)
    def __init__ (self, rect, *args, **kwargs):
        rect = pg.Rect(rect)
        ts = conf.TILE_SIZE['wall']
        graphics_rect = pg.Rect([x * ts for x in rect])
        self.rect = graphics_rect.copy()
        Entity.__init__(self, *args, **kwargs)
        if self.graphic is not None:
            self.graphics.pos = graphics_rect.topleft


class Player (NonRect):
    def init (self):
        self._graphics = dict((outfit, gfx.Animation(
            ['player-' + outfit + '-left.png',
             'player-' + outfit + '-right.png'] +
            list(Spritemap('player-' + outfit + '-walkleft.png', 4)) +
            list(Spritemap('player-' + outfit + '-walkright.png', 4))
        )) for outfit in ('hero', 'villain'))
        for outfit, g in self._graphics.iteritems():
            i = 10 if outfit == 'villain' else 0
            g.add('left', i + 0).add('right', i + 1)
            g.add('walkleft', *xrange(i + 2, i + 6))
            g.add('walkright', *xrange(i + 6, i + 10))
            g.frame_time = conf.ANIMATION_TIMES[self.ident]
        self.graphic = self._graphics['hero']

    def change_outfit (self):
        outfit = ('villain' if self.graphic == self._graphics['hero']
                            else 'hero')
        self.graphics.rm(self.graphic)
        self.graphic = self._graphics[outfit]
        self.graphics.add(self.graphic)


class Enemy (NonRect):
    def init (self):
        self.graphic = g = gfx.Animation(
            list(Spritemap('enemy-left.png', 2)) +
            list(Spritemap('enemy-right.png', 2))
        )
        g.add('left', 0).add('walkleft', 0, 1)
        g.add('right', 2).add('walkright', 2, 3)
        g.frame_time = conf.ANIMATION_TIMES[self.ident]


class Goal (NonRect):
    def init (self):
        self.graphic = gfx.Animation(Spritemap('goal.png', 6))
        self.graphic.frame_time = conf.ANIMATION_TIMES[self.ident]


class Changer (NonRect):
    def init (self):
        self.graphic = gfx.Graphic('changer.png')


class Barrier (Rect):
    def init (self):
        deflate = conf.BARRIER_DEFLATE
        self.graphic = gfx.Colour(conf.BARRIER_COLOUR, self.rect.size)
        self.rect = self.rect.inflate(-deflate, -deflate)


class Switch (NonRect):
    def init (self, barrier):
        self._barrier = barrier
        self.graphic = gfx.Animation(('switch-off.png', 'switch-on.png'))


class Wall (Rect):
    pass
