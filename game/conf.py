from platform import system
import os
from os.path import sep, expanduser, join as join_path
from collections import defaultdict
from glob import glob

import pygame as pg

import settings
from util import dd


class Conf (object):

    IDENT = 'wearhouse'
    USE_SAVEDATA = False
    USE_FONTS = False

    # save data
    SAVE = ()
    # need to take care to get unicode path
    if system() == 'Windows':
        try:
            import ctypes
            n = ctypes.windll.kernel32.GetEnvironmentVariableW(u'APPDATA',
                                                               None, 0)
            if n == 0:
                raise ValueError()
        except Exception:
            # fallback (doesn't get unicode string)
            CONF_DIR = os.environ[u'APPDATA']
        else:
            buf = ctypes.create_unicode_buffer(u'\0' * n)
            ctypes.windll.kernel32.GetEnvironmentVariableW(u'APPDATA', buf, n)
            CONF_DIR = buf.value
        CONF_DIR = join_path(CONF_DIR, IDENT)
    else:
        CONF_DIR = join_path(os.path.expanduser(u'~'), '.config', IDENT)
    CONF = join_path(CONF_DIR, 'conf')

    # data paths
    DATA_DIR = ''
    IMG_DIR = DATA_DIR + 'img' + sep
    SOUND_DIR = DATA_DIR + 'sound' + sep
    MUSIC_DIR = DATA_DIR + 'music' + sep
    FONT_DIR = DATA_DIR + 'font' + sep

    # display
    WINDOW_ICON = IMG_DIR + 'icon.png'
    WINDOW_TITLE = 'Wearhouse'
    MOUSE_VISIBLE = dd(False) # per-backend
    FLAGS = 0
    FULLSCREEN = False
    RESIZABLE = False # also determines whether fullscreen togglable
    RES_W = (960, 540)
    RES_F = pg.display.list_modes()[0]
    RES = RES_W
    MIN_RES_W = (320, 180)
    ASPECT_RATIO = None

    # timing
    FPS = dd(60) # per-backend

    # debug
    PROFILE_STATS_FILE = '.profile_stats'
    DEFAULT_PROFILE_TIME = 5

    # input
    KEYS_NEXT = (pg.K_RETURN, pg.K_SPACE, pg.K_KP_ENTER)
    KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
    KEYS_MINIMISE = (pg.K_F10,)
    KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                    (pg.K_KP_ENTER, pg.KMOD_ALT, True))
    KEYS_LEFT = (pg.K_LEFT, pg.K_a)
    KEYS_RIGHT = (pg.K_RIGHT, pg.K_d, pg.K_e)
    KEYS_JUMP = (pg.K_UP, pg.K_w, pg.K_COMMA) + KEYS_NEXT
    KEYS_USE = (pg.K_DOWN, pg.K_s, pg.K_o, pg.K_LCTRL, pg.K_LSHIFT, pg.K_RCTRL,
                pg.K_RSHIFT, pg.K_z, pg.K_x, pg.K_c)
    KEYS_RESET = (pg.K_r, pg.K_p)
    KEYS_QUIT = (pg.K_q,)

    # audio
    MUSIC_AUTOPLAY = False # just pauses music
    MUSIC_VOLUME = dd(.5) # per-backend
    SOUND_VOLUME = .5
    EVENT_ENDMUSIC = pg.USEREVENT
    SOUND_VOLUMES = dd(1, jump = 1, step = .2, door = .8, lever = .5, die = .7)
    # generate SOUNDS = {ID: num_sounds}
    SOUNDS = {}
    ss = glob(join_path(SOUND_DIR, '*.ogg'))
    base = len(join_path(SOUND_DIR, ''))
    for fn in ss:
        fn = fn[base:-4]
        for i in xrange(len(fn)):
            if fn[i:].isdigit():
                # found a valid file
                ident = fn[:i]
                if ident:
                    n = SOUNDS.get(ident, 0)
                    SOUNDS[ident] = n + 1
    STEP_SOUND_TIME = {'player': 15, 'enemy': 20}
    MAX_SOUNDS = dd(None, change = 1, lever = 1)

    # text rendering
    # per-backend, each a {key: value} dict to update fonthandler.Fonts with
    REQUIRED_FONTS = dd({})

    # graphics
    BARRIER_COLOUR = (255, 100, 100, 120)
    BARRIER_DEFLATE = 2 # on each axis, on each side
    IMGS = {
        'player': ('right', 'left', 'walkleft', 'walkright', 'villainleft',
                   'villainright', 'villainwalkleft', 'villainwalkright'),
        'enemy': ('left', 'right'),
        'switch': ('on', 'off')
    }
    IMG_SIZES = {'player': (20, 37), 'goal': (20, 40), 'enemy': (16, 18)}
    IMG_OFFSETS = dd((0, 0), {
        'player': (-5, -1),
        'changer': (-1, 0),
        'barrier': (-BARRIER_DEFLATE, -BARRIER_DEFLATE)
    })
    ANIMATION_TIMES = {'player': dd(5), 'enemy': dd(5), 'goal': {'': 10}}
    # tiled images
    TILE_SIZES = {'bg': 15}
    # {entity.ident: freqs}
    TILED_IMG_FREQS = dd((1, .8, .05, .1, .07, .1, .07, .02))
    BG_SIZE = (64, 36)

    # gameplay
    TILE_SIZE = 20
    LEVEL_SIZE = (48, 27)
    SIZES = {'player': (10, 36), 'enemy': (16, 18), 'changer': (20, 40),
             'switch': (20, 20), 'goal': (20, 40)}
    SOLID_ENTITIES = ('player', 'enemy', 'solidrect')
    # movement
    GRAVITY = .8 # making this much smaller breaks on_ground
    AIR_RESISTANCE = (.9, .8)
    FRICTION = (.75, .9)
    MOVE_SPEED = {'player': 1, 'enemy': .5}
    MOVE_SPEED_AIR = {'player': .5, 'enemy': .1}
    JUMP_INITIAL = {'player': 4.5, 'enemy': 4.5}
    JUMP_CONTINUE = {'player': 2.8, 'enemy': 2.5}
    JUMP_TIME = {'player': 4, 'enemy': 4}
    JUMP_BOOST = dd(1, enemy=2)
    BOUNCY = ('enemy',)
    # AI
    START_SEEK_NEAR = 200
    STOP_SEEK_FAR = 250
    STOP_SEEK_NEAR = 5
    SEEK_TIME = 150
    MIN_CATCH_Y_OVERLAP = 3
    # timing/cutscenes
    START_FADE = ((0, 0, 0), (False, 1))
    RESTART_TIME = 1
    RESTART_FADE = (False, ((255, 255, 255), 1), ((255, 255, 255), 1.5),
                    (False, 2))
    WIN_TIME = 1
    WIN_FADE = (False, (False, .5), ((0, 0, 0), 1), ((0, 0, 0), 1.5), (False, 2))
    END_TIME = 1
    END_FADE = (False, ((0, 0, 0), 1))
    PAUSE_DIM = (0, 0, 0, 150)

    # levels
    # y positions are the tile beneath the object (what it's standing on)
    LEVELS = [{
        'player': (17, 14),
        'enemies': [(35, 15)],
        'goal': (10, 12),
        'solid': [(0, 15, 48, 13), (0, 14, 23, 1), (0, 12, 15, 2)]
    }, {
        'player': (20, 8),
        'enemies': [(30, 8)],
        'goal': (22, 17),
        'solid': [(0, 0, 17, 27), (31, 0, 17, 27), (19, 8, 10, 1),
                  (28, 0, 1, 4), (28, 6, 1, 2), (30, 8, 1, 1), (18, 8, 1, 7),
                  (19, 10, 6, 1), (26, 10, 5, 1), (19, 12, 8, 1),
                  (28, 12, 3, 1), (19, 14, 7, 1), (27, 14, 4, 7),
                  (17, 21, 14, 6)]
    }, {
        'player': (16, 16),
        'enemies': [(25, 16)],
        'changers': [(21, 16)],
        'goal': (35, 16),
        'solid': [(0, 0, 24, 14), (0, 16, 48, 11), (0, 14, 11, 2),
                  (37, 0, 11, 27)]
    }, {
        'player': (25, 15),
        'enemies': [(14, 15)],
        'changers': [(18, 15)],
        'goal': (12, 15),
        'solid': [(0, 0, 27, 13), (0, 15, 28, 12), (0, 13, 11, 2),
                  (28, 26, 20, 1)]
    }, {
        'player': (15, 15),
        'enemies': [(33, 15)],
        'changers': [(12, 15), (20, 15)],
        'barriers': [(18, 13, 1, 2), (26, 13, 1, 2)],
        'goal': (35, 15),
        'solid': [(0, 0, 48, 13), (0, 15, 48, 12), (0, 13, 11, 2),
                  (37, 13, 11, 2)]
    }, {
        'player': (15, 15),
        'enemies': [(34, 15)],
        'changers': [(11, 15)],
        'barriers': [(22, 13, 1, 2)],
        'switches': [((25, 15), 0)],
        'goal': (36, 15),
        'solid': [(0, 15, 48, 12), (22, 0, 26, 13), (0, 0, 8, 15),
                  (40, 13, 8, 2)]
    }, {
        'player': (33, 8),
        'enemies': [(17, 7), (19, 7)],
        'changers': [(26, 9), (14, 23)],
        'barriers': [(28, 14, 1, 3), (18, 17, 1, 4)],
        'goal': (10, 19),
        'solid': [(0, 0, 10, 27), (35, 0, 13, 27), (10, 23, 25, 4),
                  (10, 7, 12, 1), (10, 0, 12, 6), (10, 8, 7, 9), (17, 8, 1, 7),
                  (18, 16, 10, 1), (19, 10, 15, 4), (29, 14, 5, 3),
                  (24, 9, 4, 1), (29, 8, 6, 1), (18, 21, 1, 2)]
    }, {
        'player': (31, 4),
        'enemies': [(22, 13), (24, 13)],
        'changers': [(24, 16)],
        'barriers': [(22, 10, 1, 1), (24, 10, 1, 1)],
        'goal': (23, 13),
        'solid': [(0, 0, 10, 27), (38, 0, 10, 27), (30, 4, 3, 1),
                  (10, 10, 10, 4), (20, 10, 1, 1), (21, 10, 1, 1),
                  (23, 10, 1, 1), (25, 10, 1, 1), (26, 10, 1, 1),
                  (21, 13, 5, 1), (20, 11, 1, 1), (26, 11, 1, 1),
                  (27, 10, 2, 4), (29, 11, 2, 3), (31, 12, 2, 2),
                  (33, 13, 2, 1), (10, 16, 28, 1), (23, 14, 1, 2),
                  (36, 15, 2, 1), (37, 14, 1, 1)]
    }, {
        'player': (14, 14),
        'enemies': [(4, 14), (27, 14)],
        'barriers': [(16, 12, 1, 2), (29, 10, 1, 4), (33, 10, 1, 4)],
        'switches': [((27, 13), 1), ((31, 10), 2)],
        'goal': (33, 19),
        'solid': [(0, 0, 4, 27), (44, 0, 4, 27), (4, 14, 28, 5),
                  (4, 19, 44, 8), (32, 14, 3, 3), (35, 16, 1, 1),
                  (36, 14, 1, 1), (37, 14, 6, 3)]
    }, {
        'player': (15, 11),
        'enemies': [(30, 11)],
        'changers': [(16, 15)],
        'barriers': [(14, 17, 15, 1)],
        'goal': (32, 16),
        'solid': [(0, 0, 14, 27), (34, 0, 14, 27), (14, 18, 20, 9),
                  (14, 11, 4, 1), (21, 11, 13, 1), (14, 15, 4, 1),
                  (20, 15, 6, 1), (27, 15, 2, 1), (29, 12, 1, 2),
                  (31, 16, 3, 2)]
    }]


def translate_dd (d):
    if isinstance(d, defaultdict):
        return defaultdict(d.default_factory, d)
    else:
        # should be (default, dict)
        return dd(*d)
conf = dict((k, v) for k, v in Conf.__dict__.iteritems()
            if k.isupper() and not k.startswith('__'))
types = {
    defaultdict: translate_dd
}
if Conf.USE_SAVEDATA:
    conf = settings.SettingsManager(conf, Conf.CONF, Conf.SAVE, types)
else:
    conf = settings.DummySettingsManager(conf, types)
