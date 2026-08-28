# Construit et dessine les parts de camembert 3D (donut/pie en volume)

import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shared.color_utils import hex_to_rgb, darken, lighten
from shared.logging.file_logger import log_error


def build_pie3d_faces(theta1_deg, theta2_deg, color, explode=0.0, r=1.0, h=0.22, n_pts=48):
    verts, colors = [], []
    center = (0.0, 0.0, h / 2)
    try:
        t1 = np.radians(theta1_deg); t2 = np.radians(theta2_deg)
        t_mid = (t1 + t2) / 2
        ex = explode * np.cos(t_mid); ey = explode * np.sin(t_mid)
        theta = np.linspace(t1, t2, n_pts)
        xo = r * np.cos(theta) + ex; yo = r * np.sin(theta) + ey
        c_top  = hex_to_rgb(lighten(color, 1.15))
        c_bot  = hex_to_rgb(darken(color, 0.75))
        c_side = hex_to_rgb(darken(color, 0.82))
        c_flat = hex_to_rgb(darken(color, 0.78))
        verts.append(list(zip(np.concatenate([[ex],xo,[ex]]), np.concatenate([[ey],yo,[ey]]), np.full(n_pts+2, h))))
        colors.append((*c_top, 1.0))
        verts.append(list(zip(np.concatenate([[ex],xo,[ex]]), np.concatenate([[ey],yo,[ey]]), np.zeros(n_pts+2))))
        colors.append((*c_bot, 1.0))
        for k in range(n_pts - 1):
            verts.append([(xo[k],yo[k],0),(xo[k+1],yo[k+1],0),(xo[k+1],yo[k+1],h),(xo[k],yo[k],h)])
            colors.append((*c_side, 1.0))
        for ang in [t1, t2]:
            xs = r*np.cos(ang)+ex; ys = r*np.sin(ang)+ey
            verts.append([(ex,ey,0),(xs,ys,0),(xs,ys,h),(ex,ey,h)])
            colors.append((*c_flat, 1.0))
        # representative point of the wedge, used to order wedges by camera distance
        center = (0.55 * r * np.cos(t_mid) + ex, 0.55 * r * np.sin(t_mid) + ey, h / 2)
    except Exception as e: log_error("Pie3D", e)
    return verts, colors, center


def _camera_direction(ax):
    elev = np.radians(getattr(ax, "elev", 28) or 28)
    azim = np.radians(getattr(ax, "azim", -48) or -48)
    return np.array([np.cos(elev) * np.cos(azim), np.cos(elev) * np.sin(azim), np.sin(elev)])


def draw_pie3d_all(ax, wedges):
    """wedges: iterable of (verts, colors, center) -- one entry per pie/donut wedge.

    Each wedge gets its own Poly3DCollection, drawn back-to-front by distance
    from the camera, so adjacent wedges never bleed into each other the way
    they do when every wedge's faces share a single collection.
    """
    if not wedges: return
    try:
        cam = _camera_direction(ax)
        ordered = sorted(wedges, key=lambda w: np.dot(w[2], cam))
        for verts, colors, _center in ordered:
            if not verts: continue
            p = Poly3DCollection(verts, zsort="average")
            p.set_facecolors(colors)
            p.set_edgecolors([(1, 1, 1, 0.18)] * len(verts))
            p.set_linewidth(0.35)
            ax.add_collection3d(p)
    except Exception as e: log_error("Pie3D", e)


def draw_pie3d_wedge(ax, theta1_deg, theta2_deg, color, explode=0.0, r=1.0, h=0.22, n_pts=48):
    verts, colors, center = build_pie3d_faces(theta1_deg, theta2_deg, color, explode, r, h, n_pts)
    draw_pie3d_all(ax, [(verts, colors, center)])
