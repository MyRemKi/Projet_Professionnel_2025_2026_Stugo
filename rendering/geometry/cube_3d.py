# Construit et dessine les cubes 3D utilises dans les graphiques en barres 3D

import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shared.color_utils import hex_to_rgb, darken, lighten
from shared.logging.file_logger import log_error


def build_cube_faces(x, y, z, dx, dy, dz, hex_color):
    verts, colors = [], []
    if dz <= 0: return verts, colors
    try:
        c_front  = (*hex_to_rgb(hex_color),             1.0)
        c_back   = (*hex_to_rgb(darken(hex_color, 0.60)), 1.0)
        c_side_r = (*hex_to_rgb(darken(hex_color, 0.65)), 1.0)
        c_side_l = (*hex_to_rgb(darken(hex_color, 0.70)), 1.0)
        c_top    = (*hex_to_rgb(lighten(hex_color, 1.22)), 1.0)
        c_bot    = (*hex_to_rgb(darken(hex_color, 0.50)), 1.0)
        v = [(x,y,z),(x+dx,y,z),(x+dx,y+dy,z),(x,y+dy,z),
             (x,y,z+dz),(x+dx,y,z+dz),(x+dx,y+dy,z+dz),(x,y+dy,z+dz)]
        for face, col in [
            ([v[0],v[1],v[5],v[4]], c_front),
            ([v[2],v[3],v[7],v[6]], c_back),
            ([v[1],v[2],v[6],v[5]], c_side_r),
            ([v[0],v[3],v[7],v[4]], c_side_l),
            ([v[4],v[5],v[6],v[7]], c_top),
            ([v[0],v[1],v[2],v[3]], c_bot),
        ]:
            verts.append(face); colors.append(col)
    except Exception as e: log_error("Cube3D", e)
    return verts, colors


def cube_center(x, y, z, dx, dy, dz):
    return (x + dx / 2, y + dy / 2, z + dz / 2)


def _camera_direction(ax):
    # unit vector pointing from the scene toward the camera, given the current elev/azim
    elev = np.radians(getattr(ax, "elev", 28) or 28)
    azim = np.radians(getattr(ax, "azim", -48) or -48)
    return np.array([np.cos(elev) * np.cos(azim), np.cos(elev) * np.sin(azim), np.sin(elev)])


def draw_cubes_batch(ax, cubes, alpha=0.93):
    """cubes: iterable of (verts, colors, center) -- one entry per cube.

    Each cube is added as its own Poly3DCollection, sorted back-to-front by
    distance from the camera. Combining every cube's faces into a single
    collection defeats matplotlib's depth sort and makes cubes visually cut
    into one another; keeping one collection per cube lets matplotlib order
    whole cubes correctly relative to each other, while zsort="average"
    still resolves the (convex, unambiguous) 6 faces within each cube.
    """
    if not cubes: return
    try:
        cam = _camera_direction(ax)
        ordered = sorted(cubes, key=lambda cube: np.dot(cube[2], cam))
        for verts, colors, _center in ordered:
            if not verts: continue
            p = Poly3DCollection(verts, zsort="average")
            p.set_facecolors(colors)
            p.set_edgecolors([(0, 0, 0, 0.20)] * len(verts))
            p.set_linewidth(0.30)
            ax.add_collection3d(p)
    except Exception as e: log_error("Cube3D", e)


def draw_cube(ax, x, y, z, dx, dy, dz, hex_color, alpha=0.93):
    verts, colors = build_cube_faces(x, y, z, dx, dy, dz, hex_color)
    draw_cubes_batch(ax, [(verts, colors, cube_center(x, y, z, dx, dy, dz))], alpha)
