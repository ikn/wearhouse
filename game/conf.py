from .engine import conf
from .engine.util import dd


class Conf (object):
    IDENT = 'wearhouse'
    WINDOW_TITLE = 'Wearhouse'
    WINDOW_ICON = conf.IMG_DIR + 'icon.png'
    RES_W = RES_SINGLE = (960, 540)
    RES_DOUBLE = (RES_SINGLE[0] * 2, RES_SINGLE[1] * 2)
    SCALE = 'none'
    SCALES = ('none', 'scale', 'scale2x', 'smoothscale')

    # gameplay
    PAD_DEADZONE = .2
    # collision
    ENTITY_SIZE = {'player': (10, 36), 'enemy': (16, 18), 'goal': (20, 40),
                   'changer': (20, 40), 'switch': (20, 20)}
    SOLID_ENTITIES = dd(('player', 'enemy', 'wall', 'boundary'),
                        deadenemy=('wall',))
    # movement
    GRAVITY = .8 # making this much smaller breaks on_ground
    AIR_RESISTANCE = (.9, .8)
    FRICTION = (.75, .9)
    MOVE_SPEED = {'player': 1, 'enemy': .55}
    MOVE_SPEED_AIR = {'player': .5, 'enemy': .25}
    JUMP_INITIAL = {'player': 4.5, 'enemy': 0}
    JUMP_CONTINUE = {'player': 2.8, 'enemy': .9}
    JUMP_TIME = {'player': .04, 'enemy': 1.1}
    JUMP_BOOST = dd(1, enemy=2)
    BOUNCY = ('enemy',)
    AUTOJUMP_COOLDOWN = {'player': .6, 'enemy': 1.8}
    # AI
    START_SEEK_NEAR = 200
    STOP_SEEK_FAR = 250
    STOP_SEEK_NEAR = 5
    SEEK_TIME = 150

    # timing/cutscenes
    ALLOW_FADES = True
    FADE_SLOW = 1
    START_FADE_IN = (1,)
    DIE_FADE_OUT = (1, (255, 255, 255))
    DIE_TIME = 1.5
    DIE_FADE_IN = (.5, (255, 255, 255))
    WIN_DELAY = .5
    WIN_FADE_OUT = (.5,)
    WIN_TIME = 1
    END_FADE_IN = (1,)
    END_INPUT_DELAY = 1
    END_FADE_OUT = (1,)
    END_CONTINUE_TIME = 1

    # audio
    SOUND_VOLUMES = dd(1, {
        'walk': .2,
        'jump': 1,
        'die': .7,
        'door': .8,
        'lever': .5
    })
    SOUND_ALIASES = {'jump': 'hit', 'walk': 'hit'}
    STEP_SOUND_TIME = {'player': .25, 'enemy': .35}
    MAX_SOUNDS = dd(None, change=1, lever=1)

    # graphics
    LAYERS = dd(0, {
        'bg': 2,
        'wall': 1,
        'enemy': -1,
        'player': -2,
        'barrier': -3
    })
    ANIMATION_TIMES = {'player': .08, 'enemy': .08, 'goal': .25}
    TILE_SIZE = {'wall': 20, 'bg': 15}
    # {ident: freqs}
    TILE_FREQS = dd((1, .8, .05, .1, .07, .1, .07, .02))
    BARRIER_COLOUR = (255, 100, 100, 120)
    BARRIER_DEFLATE = 2 # on each axis, on each side
    PAUSE_DIM = (0, 0, 0, 150)

    # levels
    # y positions are the tile beneath the object (what it's standing on)
    LEVELS = [{
        'player': (17, 14),
        'enemies': [(35, 15)],
        'goal': (10, 12),
        'walls': [(0, 15, 48, 12), (0, 14, 23, 1), (0, 12, 15, 2)]
    }, {
        'player': (20, 8),
        'enemies': [(30, 8)],
        'goal': (22, 17),
        'walls': [(0, 0, 17, 27), (31, 0, 17, 27), (18, 8, 1, 7),
                  (19, 8, 8, 1), (28, 8, 3, 1), (19, 10, 2, 1),
                  (22, 10, 9, 1), (19, 12, 11, 1), (19, 14, 7, 1),
                  (27, 14, 4, 7), (17, 21, 14, 6)]
    }, {
        'player': (16, 16),
        'enemies': [(25, 16)],
        'changers': [(21, 16)],
        'goal': (35, 16),
        'walls': [(0, 0, 24, 14), (0, 16, 48, 11), (0, 14, 11, 2),
                  (37, 0, 11, 27)]
    }, {
        'player': (25, 15),
        'enemies': [(14, 15)],
        'changers': [(18, 15)],
        'goal': (12, 15),
        'walls': [(0, 0, 27, 13), (0, 15, 28, 12), (0, 13, 11, 2),
                  (28, 26, 20, 1)]
    }, {
        'player': (15, 15),
        'enemies': [(33, 15)],
        'changers': [(12, 15), (20, 15)],
        'barriers': [(18, 13, 1, 2), (26, 13, 1, 2)],
        'goal': (35, 15),
        'walls': [(0, 0, 48, 13), (0, 15, 48, 12), (0, 13, 11, 2),
                  (37, 13, 11, 2)]
    }, {
        'player': (15, 15),
        'enemies': [(34, 15)],
        'changers': [(11, 15)],
        'barriers': [(22, 13, 1, 2)],
        'switches': [((25, 15), 0)],
        'goal': (36, 15),
        'walls': [(0, 15, 48, 12), (22, 0, 26, 13), (0, 0, 8, 15),
                  (40, 13, 8, 2)]
    }, {
        'player': (31, 5),
        'enemies': [(21, 14), (25, 14)],
        'changers': [(26, 18)],
        'barriers': [(21, 9, 1, 1), (25, 9, 1, 1)],
        'goal': (23, 12),
        'walls': [(0, 0, 10, 27), (38, 0, 10, 27), (30, 5, 3, 1),
                  (10, 9, 10, 6), (20, 9, 1, 1), (22, 9, 3, 1),
                  (26, 9, 1, 1), (20, 12, 7, 1), (27, 9, 2, 7),
                  (29, 10, 1, 6), (30, 11, 1, 5), (31, 12, 1, 4),
                  (32, 13, 1, 3), (33, 14, 1, 2), (34, 15, 1, 1),
                  (10, 18, 28, 1), (21, 14, 5, 4), (36, 17, 2, 1),
                  (37, 16, 1, 1)]
    }, {
        'player': (33, 8),
        'enemies': [(17, 7), (19, 7)],
        'changers': [(26, 9), (14, 23)],
        'barriers': [(28, 14, 1, 3), (18, 17, 1, 4)],
        'goal': (10, 19),
        'walls': [(0, 0, 10, 27), (35, 0, 13, 27), (10, 23, 25, 4),
                  (10, 7, 12, 1), (10, 0, 12, 6), (10, 8, 7, 9), (17, 8, 1, 7),
                  (18, 16, 10, 1), (19, 10, 15, 4), (29, 14, 5, 3),
                  (24, 9, 4, 1), (29, 8, 6, 1), (18, 21, 1, 2)]
    }, {
        'player': (14, 12),
        'enemies': [(4, 12), (27, 14)],
        'barriers': [(16, 10, 1, 2), (29, 9, 1, 5), (33, 9, 1, 5)],
        'switches': [((27, 13), 1), ((31, 10), 2)],
        'goal': (33, 19),
        'walls': [(0, 0, 4, 27), (44, 0, 4, 27), (4, 12, 21, 2), (4, 14, 28, 5),
                  (4, 19, 44, 8), (32, 14, 3, 3), (35, 16, 1, 1),
                  (36, 14, 1, 1), (37, 14, 6, 3)]
    }, {
        'player': (15, 11),
        'enemies': [(30, 11)],
        'changers': [(16, 15)],
        'barriers': [(14, 17, 15, 1)],
        'goal': (32, 15),
        'walls': [(0, 0, 14, 27), (34, 0, 14, 27), (14, 18, 20, 9),
                  (14, 11, 4, 1), (21, 11, 13, 1), (14, 15, 4, 1),
                  (20, 15, 6, 1), (27, 15, 2, 1), (29, 12, 1, 2),
                  (31, 15, 3, 3)]
    }]
