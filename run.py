from sys import argv
import os

from pygame import joystick
if os.name == 'nt':
    # for Windows freeze support
    import pygame._view
from game import engine

from game.level import Level as entry_world

if __name__ == '__main__':
    engine.init()

    # initialise all gamepads
    for i in xrange(joystick.get_count()):
        joystick.Joystick(i).init()

    args = []
    if len(argv) > 1:
        # got some command-line arguments
        from optparse import OptionParser
        op = OptionParser(prog = 'run')
        op.add_option('-b', '--debug', action = 'store_true', dest = 'debug')
        op.add_option('-p', '--profile', action = 'store_true')
        op.add_option('-t', '--time', action = 'store', type = 'float',
                      help = 'float seconds to run for')
        op.add_option('-n', '--num-stats', action = 'store', type = 'int',
                      help = 'number of functions to show when profiling; ' \
                      'defaults to 30')
        op.add_option('-f', '--profile-file', action = 'store',
                      type = 'string', help = 'defaults to \'.profile_stats\'')
        op.add_option('-s', '--sort-stats', action = 'store', type = 'string',
                      help = 'profile stats sort mode; defaults to ' \
                      '\'cumulative\' (see pstats.Stats.sort_stats doc)')
        op.set_defaults(debug = False, time = None, num_stats = 30,
                        profile_file = '.profile_stats',
                        sort_stats = 'cumulative')
        options, argv = op.parse_args()
        args.append(int(argv[0]) - 1 if argv else 0)
        # debug
        engine.conf.DEBUG = options.debug
        # construct world args
        # run game
        if options.profile:
            from cProfile import run
            from pstats import Stats
            args = ', '.join(repr(arg) for arg in args)
            if args:
                args += ', '
            code = 'engine.game.run(entry_world, {0}t = options.time)'
            run(code.format(args), options.profile_file, locals())
            Stats(options.profile_file).strip_dirs() \
                .sort_stats(options.sort_stats).print_stats(options.num_stats)
            os.unlink(options.profile_file)
        else:
            engine.game.run(entry_world, *args, t = options.time)
    else:
        args.append(0)
        engine.game.run(entry_world, *args)

    engine.quit()
