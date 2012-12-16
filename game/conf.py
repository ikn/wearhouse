from platform import system
import os
from os.path import sep, expanduser, join as join_path
from collections import defaultdict
from glob import glob

import pygame as pg

import settings
from util import dd


class Conf (object):

    IDENT = 'game'
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
    WINDOW_ICON = None #IMG_DIR + 'icon.png'
    WINDOW_TITLE = ''
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
    KEYS_LEFT = (pg.K_LEFT, pg.K_a, pg.K_q)
    KEYS_RIGHT = (pg.K_RIGHT, pg.K_d, pg.K_e)
    KEYS_UP = (pg.K_UP, pg.K_w, pg.K_z, pg.K_COMMA)
    KEYS_DOWN = (pg.K_DOWN, pg.K_s, pg.K_o)
    KEYS_DIRN = (KEYS_LEFT, KEYS_UP, KEYS_RIGHT, KEYS_DOWN)
    KEYS_RESET = (pg.K_r, pg.K_p)

    # audio
    MUSIC_AUTOPLAY = False # just pauses music
    MUSIC_VOLUME = dd(.5) # per-backend
    SOUND_VOLUME = .5
    EVENT_ENDMUSIC = pg.USEREVENT
    SOUND_VOLUMES = dd(1, jump = 1, step = .2, door = .5, lever = .5)
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

    # gameplay
    TILE_SIZE = 20
    LEVEL_SIZE = (48, 27)
    SIZES = {'player': (18, 37), 'enemy': (18, 18), 'changer': (20, 40),
             'switch': (15, 15), 'goal': (20, 40)}
    # movement
    GRAVITY = .8
    AIR_RESISTANCE = (.9, .9)
    FRICTION = (.75, .9)
    MOVE_SPEED = {'player': 1.5, 'enemy': .7}
    MOVE_SPEED_AIR = {'player': .5, 'enemy': .1}
    JUMP_INITIAL = {'player': 4.4, 'enemy': 4}
    JUMP_CONTINUE = {'player': 2.2, 'enemy': 2}
    JUMP_TIME = {'player': 4, 'enemy': 4}
    # AI
    START_SEEK = 200
    STOP_SEEK = 300
    SEEK_TIME = 90
    STOP_RETURN = 5
    # timing/cutscenes
    SWITCH_TIME = 1
    RESTART_TIME = 1
    RESTART_FADE = (False, ((255, 255, 255), 1), ((255, 255, 255), 1.5),
                    (False, 2))

    # levels
    # y positions are the tile beneath the object (what it's standing on)
    LEVELS = [{
        'player': (17, 14),
        'enemies': [(35, 15)],
        'goal': (10, 12),
        'solid': [(0, 15, 48, 13), (0, 14, 23, 1), (0, 12, 15, 2)]
    }, {
        'player': (23, 8),
        'enemies': [(23, 11), (23, 13), (23, 15), (23, 17)],
        'goal': (23, 20),
        'solid': [(0, 0, 48, 5), (0, 5, 15, 22), (32, 5, 16, 22),
                  (16, 8, 15, 2), (16, 10, 1, 2), (16, 13, 1, 3),
                  (16, 17, 1, 3), (30, 11, 1, 3), (30, 15, 1, 5),
                  (23, 11, 1, 1), (17, 13, 9, 1), (23, 15, 1, 1),
                  (17, 17, 9, 1), (18, 24, 11, 1), (15, 25, 17, 1)]
    }, {
        'player': (28, 19),
        'enemies': [(31, 16), (35, 17), (37, 16)],
        'changers': [(27, 16)],
        'goal': (43, 16),
        'solid': [(0, 16, 13, 11), (13, 19, 23, 8), (36, 16, 12, 11),
                  (16, 16, 16, 1), (13, 18, 2, 1), (13, 17, 1, 1),
                  (33, 18, 3, 1), (34, 17, 2, 1), (0, 0, 48, 13),
                  (17, 13, 16, 1)]
    }, {
        'player': (17, 10),
        'enemies': [(18, 7)],
        'changers': [(31, 7)],
        'goal': (30, 20),
        'solid': [(0, 0, 16, 27), (32, 0, 16, 27), (16, 7, 9, 1),
                  (17, 10, 9, 8), (27, 9, 5, 9),
                  (28, 8, 4, 1), (29, 7, 3, 1), (26, 15, 1, 3),
                  (16, 24, 16, 3)]
    }, {
        'player': (15, 10),
        'enemies': [(22, 13), (24, 13)],
        'changers': [(24, 16)],
        'barriers': [(21, 10, 1, 1), (25, 10, 1, 1)],
        'goal': (23, 13),
        'solid': [(0, 0, 10, 27), (38, 0, 10, 27), (10, 10, 10, 4),
                  (20, 10, 1, 1), (22, 10, 3, 1), (26, 10, 1, 1),
                  (21, 13, 5, 1), (27, 10, 2, 4), (29, 11, 2, 3),
                  (31, 12, 2, 2), (33, 13, 2, 1), (10, 16, 28, 1),
                  (23, 14, 1, 2), (36, 15, 2, 1), (37, 14, 1, 1)]
    }, {
        'player': (15, 15),
        'enemies': [(34, 15)],
        'changers': [(11, 15)],
        'barriers': [(22, 13, 1, 2)],
        'switches': [((25, 15), 0)],
        'goal': (36, 15),
        'solid': [(0, 15, 19, 12), (20, 15, 28, 12), (19, 18, 1, 10),
                  (0, 0, 48, 13), (0, 13, 8, 2), (40, 13, 8, 2)]
    }, {
        'player': (27, 10),
        'enemies': [(16, 10), (31, 16), (30, 19)],
        'changers': [],
        'barriers': [(29, 8, 1, 2), (25, 14, 1, 2), (18, 11, 1, 5),
                     (21, 17, 1, 2)],
        'switches': [((27, 15), 1), ((21, 12), 2), ((19, 19), 3)],
        'goal': (31, 19),
        'solid': [(0, 0, 15, 27), (33, 0, 15, 27), (15, 10, 16, 1),
                  (17, 16, 16, 1), (15, 19, 18, 8)]
    }, {
        'player': (16, 11),
        'enemies': [(30, 11)],
        'changers': [(15, 15)],
        'barriers': [(14, 17, 15, 1)],
        'goal': (32, 16),
        'solid': [(0, 0, 14, 27), (34, 0, 14, 27), (14, 18, 20, 9),
                  (14, 11, 4, 1), (21, 11, 13, 1), (14, 15, 4, 1),
                  (20, 15, 4, 1), (25, 15, 4, 1), (29, 12, 1, 2),
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
