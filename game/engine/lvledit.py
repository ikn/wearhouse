"""

 - is a World
 - has pos, size which match up with input (mouse) and graphics
 - expose input config for adding extra control methods (eg. gamepad)
 - define how to draw the background
 - restrict drawing to an interval in the continuum of layers, and expose this
 - undo/redo (u, z, ctrl-z / ctrl-r, y, ctrl-shift-z)
 - scrolling and boundaries
    - ctrl-arrows, space-click-drag, space-middle-click for autoscroll
    - snap to global grid unless hold shift
    - if level smaller than viewing area, centre it
        - if UIs are permanent, take those into account
 - zooming? (ctrl-scrollwheel, +/-; ctrl-0, 0, / to reset)
 - can set snap to grid (global is also for cursor, something else I forget)
 - can disallow overlapping ('disjoint')
    - True, False or list of sets of identifiers, either groups or types
 - select/deselect all: ctrl-(shift-)a
 - modes:
    - paint (p)
    - rect (r)
    - polygon (g)
    - circle (c)
    - one-size object (i)
    - edit (e, esc to go back to previous mode)
 - choose mode by pressing a key (shown, or 123..., or alt-up/down) or clicking icon
    - type is remembered within each mode
 - define different types of rects/objects
    - define per-type properties, eg.
        - how to draw them (including icons)
        - layer to draw in
        - minimum/maximum number of objects of this type
        - (inherit) whether can overlap, and with what
        - (inherit) grid
        - rect: minimum size
        - one-size: size
    - select type by alt-left/right or ctrl-(shift-)tab or clicking icon
 - filters to restrict view to certain object types
    - can choose multiple
    - define how to hide other types through tint colour
 - place things by left-click
 - on place, resize rects/circles with left-click drag
 - show current cursor co-ordinates somewhere
    - option for if/how to display them
 - UI options
    - where to put it (top/bottom)
    - whether have to press a key for it to pop up (enter, esc to dismiss)
 - can define extra UIs
 - edit mode:
    - click to select object (draws border)
    - ctrl-click to add to selection
    - click-drag out of selection/ctrl-click-drag to select multiple
    - click-drag/arrows to move object(s) (careful if overlapping not allowed)
    - right-click-drag to resize (rects only, only if one selected) (or have resize handles?)
    - delete/d/middle-click to remove object(s) (middle-click works in any mode)
    - (shift-)tab to select next (previous) object (only if one selected)
    - hold shift to ignore snapping to grid
    - hold alt to snap cursor to grid
 - have .load(fn_or_data[, transform_fn]), .save([fn_else_returns_data][, transform_fn])
 - objects have modifiable properties
    - object args can be functions to filter by current properties
        - change what they affect when properties change
    - generated level output contains properties
    - have 'modifier' objects that modify an object you click on
        - define a function that takes the clicked object's properties and alters it in-place to modify the object

args:
 - object types
    - how to draw (many are like Tilemap's tile_graphic, but can be a function to generate different ones each time)
    - layer
    - grid
    - minimum/maximum number of objects of this type
    - one-size: size; how to position within grid tiles (eg. centre)
    - rect: minimum size

settable properties:
 - grid, and can retrieve and change the grid (plus non-global grids?)
 - UI
    - location
    - hidden
    - co-ords display
    - bg colour
 - filtering tint
 - zoom level
 - position within the level
 - colour outside level

"""

from .game import World
from . import evt, gfx


class LevelEditor (World):
    """A running level editor (:class:`World <engine.game.World>` subclass)."""

    def init (self, objects=None, grid=1, bdy=None,
              disjoint=(('paint', 'paint'), ('', ''))):
        """Initialisation function.

init(objects={}, grid=1[, bdy], disjoint=(('paint', 'paint'), ('', '')))

:arg objects: definitions for types of objects that can be added to the level.
    This is ``{group: types}``, where ``group`` is an identifier giving which
    sort of object this is, and ``types`` is a list of ``{ident: object}``
    ``dict``s defining a new object type for ``ident`` not ``None``.

    ``object`` in each case is a ``dict`` of arguments.  Those available for
    all groups are:

        - ``'graphic'``: how to draw the object.  The form of this differs
          between groups.
        - ``'layer'``: the layer to draw the object in.  This is a purely
          relative number, lower being nearer to the 'front'.  The default
          depends on the group.
        - ``'grid'``: as the global ``grid`` argument, to apply just for this
          object type.  If omitted, the global grid is used.

    The available groups, and arguments specific to each group:

        - ``'paint'``: an object that can be painted over an arbitrary area,
                       defined by the tiles it is painted in.
        - ``'rect'``: a rectangle.
        - ``'poly'``: 
        - ``'circle'``: 
        - ``''``: 

:arg grid: grid to snap objects to (and various other actions).  This is an
           :class:`gfx.InfiniteGrid <engine.gfx.graphics.InfiniteGrid>`
           instance, or the ``tile_size`` argument taken by
           :class:`util.InfiniteGrid <engine.util.InfiniteGrid>` for a grid
           that isn't drawn.  The grid's ``gap`` only affects drawing, not
           behaviour.
:arg bdy: the boundaries of the level, as a Pygame-style rect; if not given,
          the level is unbounded.
:arg disjoint: whether objects placed in the level may overlap.  If  ``True``,
               any objects may overlap; if ``False``, no objects may overlap.
               Otherwise, this can be a sequence of sets of object identifiers,
               defining sets of objects that may overlap.  An identifier is one
               of the object groups (``'paint'``, ``'rect'``, ...) or a defined
               type in ``objects``.

"""
        pass
