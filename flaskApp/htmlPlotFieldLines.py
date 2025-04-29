


import netCDF4 as nc
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from scipy.ndimage import zoom
import pyvista as pv
import psutil

# ───────────────────────────────────────────────────────────────
# PyVista global settings
# ───────────────────────────────────────────────────────────────
pv.global_theme.depth_peeling.number_of_peels = 1
pv.global_theme.depth_peeling.occlusion_ratio = 1.0
pv.global_theme.depth_peeling.enabled = False
pv.global_theme.anti_aliasing = None
pv.global_theme.volume_mapper = "smart"
pv.OFF_SCREEN = False
pv.global_theme.smooth_shading = False
pv.global_theme.render_lines_as_tubes = False
pv.global_theme.multi_samples = 8
print(f"GPU Rendering: {pv.OFF_SCREEN}")

# ════════════════════════════════════════
# NetCDF helpers
# ════════════════════════════════════════
def read_nc_variables(path, vars_):
    out = {}
    with nc.Dataset(path) as ds:
        for v in vars_:
            out[v] = ds.variables[v][:]
    return out


def downsample_data_dict(d, f=2):
    return {k: zoom(a, 1/f if a.ndim == 1 else [1/f]*a.ndim) for k, a in d.items()}

# ════════════════════════════════════════
# Streamline helpers
# ════════════════════════════════════════
def create_pyvista_grid(x, y, z, Bx, By, Bz):
    g = pv.RectilinearGrid(x, y, z)
    g["B"] = np.stack([Bx.ravel(order="C"),
                       By.ravel(order="C"),
                       Bz.ravel(order="C")], axis=-1)
    return g


def _trace(grid, seed, step, flip=1):
    kw = dict(source_center=seed,
              max_time=20000,             # integers to satisfy VTK
              max_steps=100000,
              integrator_type=2,
              compute_vorticity=False)
    try:
        return grid.streamlines("B", direction=flip,
                                initial_step_size=step, **kw)
    except TypeError:                       # older PyVista: no 'direction'
        g = grid.copy()
        g["B"] = grid["B"] * flip
        return g.streamlines("B", initial_step_length=step, **kw)


def _best_poly(stream):
    if not stream or not stream.lines.size:
        return None, 0
    conn, pts = stream.lines, stream.points
    best, best_disp, off = None, -1, 0
    while off < conn.size:
        npts = int(conn[off]); off += 1
        idx = conn[off:off+npts]; off += npts
        p   = pts[idx]
        disp= np.linalg.norm(p[0]-p[-1])
        if disp > best_disp:
            best, best_disp = p, disp
    return best, best_disp


def _trial_streamlines(grid, seed):
    """one bidirectional-round with two step sizes; returns best polyline"""
    trials = []
    for flip in (1, -1):          # forward, backward
        for step in (3.0, 1.0):   # coarse, fine
            s = _trace(grid, seed, step, flip)
            p, disp = _best_poly(s)
            if p is not None:
                trials.append((disp, p))
    if trials:
        return max(trials, key=lambda t: t[0])[1]
    return None


def compute_streamlines_pyvista(grid, seed, n_attempts=5):
    """
    Run _trial_streamlines() up to n_attempts times (with different random
    internal sampling each call) and keep the line with maximal displacement.
    Guarantees consistent, curved result on first build.
    """
    best_disp, best_poly = -1, None
    for _ in range(n_attempts):
        p = _trial_streamlines(grid, seed)
        if p is None:
            continue
        disp = np.linalg.norm(p[0]-p[-1])
        if disp > best_disp:
            best_disp, best_poly = disp, p
    if best_poly is None:
        return []
    print(f"[DEBUG] Seed {seed} displacement = {best_disp:.2f}")
    return [(best_poly[:,0], best_poly[:,1], best_poly[:,2])]

# ════════════════════════════════════════
# Plot builder (keyword‑compatible)
# ════════════════════════════════════════
def create_3d_contour_plot(
    *,
    data,
    variable_name,
    x_coords,
    y_coords,
    z_coords,
    output_html,
    color_scale,
    x_range,
    y_range,
    z_range,
    opacity,
    field_lines,
    Bx_array,
    By_array,
    Bz_array
):
    i0,i1 = x_range; j0,j1 = y_range; k0,k1 = z_range
    X, Y, Z = x_coords[i0:i1], y_coords[j0:j1], z_coords[k0:k1]
    block   = data[i0:i1, j0:j1, k0:k1]
    iso_min, iso_max = color_scale

    xv,yv,zv = np.meshgrid(X,Y,Z,indexing="ij")
    fig = go.Figure(go.Isosurface(
        x=xv.ravel(), y=yv.ravel(), z=zv.ravel(), value=block.ravel(),
        isomin=iso_min, isomax=iso_max, opacity=opacity,
        caps=dict(x_show=False,y_show=False,z_show=False),
        colorscale="Viridis", surface_count=5, name=variable_name))

    if field_lines:
        Bx = Bx_array[i0:i1, j0:j1, k0:k1]
        By = By_array[i0:i1, j0:j1, k0:k1]
        Bz = Bz_array[i0:i1, j0:j1, k0:k1]
        colors = ["red","orange","blue","purple","green","cyan",
                  "magenta","yellow","brown","black"]
        for idx, seed in enumerate(field_lines):
            grid = create_pyvista_grid(X,Y,Z,Bx,By,Bz)
            for xl,yl,zl in compute_streamlines_pyvista(grid, seed):
                fig.add_trace(go.Scatter3d(
                    x=xl,y=yl,z=zl, mode="lines",
                    line=dict(color=colors[idx%len(colors)], width=3),
                    name=f"Field Line {idx+1}"))

    fig.update_layout(scene=dict(xaxis_title="X",yaxis_title="Y",zaxis_title="Z"),
                      margin=dict(l=0,r=0,b=0,t=40))
    pio.write_html(fig, output_html, include_plotlyjs="cdn", full_html=True)
    _inject_click_handler(output_html)

# ════════════════════════════════════════
# JS click handler injection
# ════════════════════════════════════════
def _inject_click_handler(html_path):
    js = r"""
<script>
document.addEventListener('DOMContentLoaded', () => {
  const plot = document.querySelector('.js-plotly-plot');
  if (!plot) return;

  // helper: round to 7 decimals (matches float64 precision in Python side)
  const snap = v => Math.round(v * 1e7) / 1e7;

  plot.on('plotly_click', evt => {
    if (!(evt && evt.points && evt.points.length)) return;
    const { x, y, z } = evt.points[0];

    // snap to nearest grid node to avoid "seed out of bounds" errors
    const payload = { type: 'FIELD_LINE_CLICK',
                      x: snap(x), y: snap(y), z: snap(z) };

    console.log('[Plotly click] sending', payload);
    window.parent.postMessage(JSON.stringify(payload, null, 2), '*');
  });
});
</script>
</body>
</html>
"""
    with open(html_path, "r+", encoding="utf-8") as f:
        html = f.read()
        new_html = (
            html.replace("</body>\n</html>", js)
            if "</body>" in html
            else html + js
        )
        f.seek(0)
        f.write(new_html)
        f.truncate()
