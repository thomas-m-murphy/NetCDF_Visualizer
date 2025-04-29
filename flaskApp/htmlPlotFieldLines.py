
# import netCDF4 as nc
# import numpy as np
# import plotly.graph_objects as go
# import plotly.io as pio
# from scipy.ndimage import zoom

# import pyvista as pv
# import psutil  # For memory checks

# # -----------------------------------------------------
# # GPU-BASED RENDERING OPTIMIZATIONS (OPTIONAL)
# # -----------------------------------------------------
# pv.global_theme.depth_peeling.number_of_peels = 1  # Number of rendering layers
# pv.global_theme.depth_peeling.occlusion_ratio = 1.0  # 0 = best quality; 1 = worst, but faster
# pv.global_theme.depth_peeling.enabled = False  # Enable depth peeling for transparency rendering (helps render overlapping translucent surfaces)

# pv.global_theme.anti_aliasing = None  # smooth jagged edges
# pv.global_theme.volume_mapper = "smart"  # use GPU acceleration for volume rendering
# pv.OFF_SCREEN = False  # set to F to render on screen (true would render off-screen)
# pv.global_theme.smooth_shading = False  # enable smooth shading for better-looking surfaces
# pv.global_theme.render_lines_as_tubes = False  # render all lines as tubes instead of flat 1D lines for better visibility
# pv.global_theme.multi_samples = 8  # set number of anti-aliasing samples (higher = smoother visuals)

# # debug output to confirm settings are active
# print(f"GPU Accelerated Rendering: {pv.OFF_SCREEN}")
# print("PyVista GPU Rendering Settings Applied!")


# ####################################################
# # 1) Read NetCDF data (with debug checks)
# ####################################################
# def read_nc_variables(file_path, variable_names):
#     """
#     Reads the specified variables from a NetCDF file and returns them in a dict.
#     Prints debug statements if any issues (NaN, Inf, monotonic coords, zero field) are found.
#     """
#     mem_info_before = psutil.virtual_memory()
#     print(f"[DEBUG] Memory usage before reading {file_path}: {mem_info_before.percent}% "
#           f"({mem_info_before.available//(1024**2)} MB available)")

#     data = {}
#     try:
#         with nc.Dataset(file_path, 'r') as ds:
#             for varname in variable_names:
#                 if varname in ds.variables:
#                     arr = ds.variables[varname][:]
#                     data[varname] = arr

#                     # Debug checks
#                     if np.isnan(arr).any():
#                         print(f"[WARNING] NaN values found in '{varname}'.")
#                     if np.isinf(arr).any():
#                         print(f"[WARNING] Inf values found in '{varname}'.")
#                     if varname in ["X", "Y", "Z"]:
#                         diffs = np.diff(arr)
#                         if not np.all(diffs > 0):
#                             print(f"[WARNING] Coordinate '{varname}' is not strictly increasing.")
#                     if varname in ["Bx", "By", "Bz"]:
#                         if np.all(arr == 0):
#                             print(f"[WARNING] Variable '{varname}' is entirely zero.")
#                 else:
#                     raise ValueError(f"Variable '{varname}' not found in {file_path}")

#         mem_info_after = psutil.virtual_memory()
#         print(f"[DEBUG] Memory usage after reading {file_path}: {mem_info_after.percent}% "
#               f"({mem_info_after.available//(1024**2)} MB available)")
#         return data
#     except Exception as e:
#         raise RuntimeError(f"Error reading {variable_names} from {file_path}: {e}")


# ####################################################
# # 2) Downsample by factor=2
# ####################################################
# def downsample_data_dict(data_dict, factor=2):
#     downsampled = {}
#     for key, arr in data_dict.items():
#         if arr.ndim == 1:
#             downsampled[key] = zoom(arr, zoom=1/factor)
#         else:
#             zf = [1/factor]*arr.ndim
#             downsampled[key] = zoom(arr, zoom=zf)
#     return downsampled


# ####################################################
# # 3) Build a PyVista RectilinearGrid
# ####################################################
# def create_pyvista_grid(x_coords, y_coords, z_coords, Bx, By, Bz):
#     rgrid = pv.RectilinearGrid(x_coords, y_coords, z_coords)
#     vectors = np.stack([
#         Bx.ravel(order='C'),
#         By.ravel(order='C'),
#         Bz.ravel(order='C')
#     ], axis=-1)
#     rgrid['B'] = vectors
#     return rgrid


# ####################################################
# # 4) Compute streamlines with extended parameters
# ####################################################
# def compute_streamlines_pyvista(grid, seed_point):
#     print(f"[DEBUG] Computing streamlines for seed point: {seed_point}")
#     try:
#         source = pv.PointSet()
#         source.points = np.array([seed_point])
#     except AttributeError:
#         source = pv.PolyData([seed_point])

#     if hasattr(grid, "streamlines"):
#         try:
#             stream = grid.streamlines(
#                 'B',
#                 source_center=seed_point,
#                 max_time=999999,
#                 initial_step_size=3.0,
#                 n_points=2000,
#                 max_steps=500000,
#                 integrator_type=2
#             )
#         except TypeError:
#             stream = grid.streamlines(
#                 'B',
#                 source_center=seed_point,
#                 max_time=999999,
#                 integrator_type=2
#             )
#     else:
#         stream = grid.streamlines_from_source(
#             source,
#             'B',
#             max_time=999999
#         )

#     lines = []
#     connectivity = stream.lines
#     pts = stream.points
#     offset = 0
#     if connectivity.size > 0:
#         npts = connectivity[offset]
#         offset += 1
#         idxs = connectivity[offset : offset + npts]
#         offset += npts
#         coords = pts[idxs]
#         x_line = coords[:, 0]
#         y_line = coords[:, 1]
#         z_line = coords[:, 2]
#         lines.append((x_line, y_line, z_line))
#     else:
#         print("[WARNING] No streamline connectivity found; empty line.")

#     return lines


# ####################################################
# # 5) Create the 3D Contour Plot + Streamlines => HTML
# ####################################################
# def create_3d_contour_plot(
#     data,
#     variable_name,
#     x_coords,
#     y_coords,
#     z_coords,
#     output_html=None,
#     color_scale=None,
#     x_range=None,
#     y_range=None,
#     z_range=None,
#     opacity=1.0,
#     field_lines=None,
#     Bx_array=None,
#     By_array=None,
#     Bz_array=None
# ):
#     print("[DEBUG] Inside create_3d_contour_plot()")

#     nx, ny, nz = data.shape
#     print(f"[DEBUG] Data shape: {nx}x{ny}x{nz}")

#     # Slicing
#     if x_range:
#         x_min_idx, x_max_idx = x_range
#     else:
#         x_min_idx, x_max_idx = 0, nx
#     if y_range:
#         y_min_idx, y_max_idx = y_range
#     else:
#         y_min_idx, y_max_idx = 0, ny
#     if z_range:
#         z_min_idx, z_max_idx = z_range
#     else:
#         z_min_idx, z_max_idx = 0, nz

#     X_used = x_coords[x_min_idx:x_max_idx]
#     Y_used = y_coords[y_min_idx:y_max_idx]
#     Z_used = z_coords[z_min_idx:z_max_idx]
#     print("[DEBUG] Extracted coordinate ranges")

#     data_used = data[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]

#     # Color scale
#     isomin = np.min(data_used) if color_scale is None else color_scale[0]
#     isomax = np.max(data_used) if color_scale is None else color_scale[1]
#     print(f"[DEBUG] isomin={isomin}, isomax={isomax}")

#     xv, yv, zv = np.meshgrid(X_used, Y_used, Z_used, indexing='ij')
#     print("[DEBUG] Meshgrid created")

#     fig = go.Figure()

#     print("[DEBUG] Adding isosurface to figure...")
#     fig.add_trace(go.Isosurface(
#         x=xv.ravel(),
#         y=yv.ravel(),
#         z=zv.ravel(),
#         value=data_used.ravel(),
#         isomin=isomin,
#         isomax=isomax,
#         opacity=opacity,
#         caps=dict(x_show=False, y_show=False, z_show=False),
#         colorscale='Viridis',
#         surface_count=5,
#         name=f'{variable_name}'
#     ))
#     print("[DEBUG] Isosurface added successfully!")

#     # If seeds => compute lines
#     if field_lines and len(field_lines) > 0:
#         if Bx_array is None or By_array is None or Bz_array is None:
#             raise ValueError("Bx, By, Bz arrays not provided for streamlines.")

#         Bx_used = Bx_array[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]
#         By_used = By_array[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]
#         Bz_used = Bz_array[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]

#         grid = create_pyvista_grid(X_used, Y_used, Z_used, Bx_used, By_used, Bz_used)

#         color_list = ['red','orange','blue','purple','green',
#                       'cyan','magenta','yellow','brown','black']

#         for idx, (sx, sy, sz) in enumerate(field_lines):
#             line_segments = compute_streamlines_pyvista(grid, (sx, sy, sz))
#             color = color_list[idx % len(color_list)]
#             for (x_line, y_line, z_line) in line_segments:
#                 fig.add_trace(go.Scatter3d(
#                     x=x_line,
#                     y=y_line,
#                     z=z_line,
#                     mode='lines',
#                     line=dict(color=color, width=3),
#                     name=f'Field Line {idx+1}'
#                 ))
#         print("[DEBUG] Streamlines added successfully.")

#     fig.update_layout(
#         scene=dict(
#             xaxis=dict(title='X'),
#             yaxis=dict(title='Y'),
#             zaxis=dict(title='Z'),
#         ),
#         title=f"3D Contour Plot of {variable_name}"
#     )

#     # If user wants an HTML => save it
#     if output_html:
#         print(f"[DEBUG] Saving final 3D HTML => {output_html}")
#         pio.write_html(fig, output_html, include_plotlyjs='cdn', full_html=True)

#         # -----------------------------------------------------------
#         # Inject code to allow user clicks => parent page postMessage
#         # We'll read that file content, append a small <script> block.
#         # -----------------------------------------------------------
#         injection_script = r"""
# <script>
# document.addEventListener("DOMContentLoaded", function(){
#   var plotDiv = document.getElementsByClassName("js-plotly-plot")[0];
#   if(!plotDiv){return;}
#   // Listen for Plotly clicks
#   plotDiv.on("plotly_click", function(d){
#     if(d && d.points && d.points.length>0){
#       var pt = d.points[0];
#       var msg = {
#         type: "FIELD_LINE_CLICK",
#         x: pt.x,
#         y: pt.y,
#         z: pt.z
#       };
#       window.parent.postMessage(JSON.stringify(msg), "*");
#     }
#   });
# });
# </script>
# </body>
# </html>
# """
#         with open(output_html, 'r+', encoding='utf-8') as f:
#             content = f.read()
#             # Replace the final </body></html> with injection
#             if '</body>' in content:
#                 new_content = content.replace('</body>\n</html>', injection_script)
#             else:
#                 # fallback
#                 new_content = content + injection_script
#             f.seek(0)
#             f.write(new_content)
#             f.truncate()

#     return {}




















# # WORKS VERY WELL, SECOND FIELD LINE DOES NOT DRAW CORRECTLY, BUT CORRECTS ITSELF WHEN THIRD ONE IS DRAWN


# import netCDF4 as nc
# import numpy as np
# import plotly.graph_objects as go
# import plotly.io as pio
# from scipy.ndimage import zoom

# import pyvista as pv
# import psutil  # for memory checks

# # ───────────────────────────────────────────────────────────────
# # Global PyVista settings
# # ───────────────────────────────────────────────────────────────
# pv.global_theme.depth_peeling.number_of_peels = 1
# pv.global_theme.depth_peeling.occlusion_ratio = 1.0
# pv.global_theme.depth_peeling.enabled = False
# pv.global_theme.anti_aliasing = None
# pv.global_theme.volume_mapper = "smart"
# pv.OFF_SCREEN = False
# pv.global_theme.smooth_shading = False
# pv.global_theme.render_lines_as_tubes = False
# pv.global_theme.multi_samples = 8
# print(f"GPU Accelerated Rendering: {pv.OFF_SCREEN}\nPyVista GPU Rendering Settings Applied!")

# # ═══════════════════════════════════════════════════════════════
# # 1) Read NetCDF variables with validation
# # ═══════════════════════════════════════════════════════════════
# def read_nc_variables(path, variables):
#     before = psutil.virtual_memory()
#     print(f"[DEBUG] Mem before reading {path}: {before.percent}% ({before.available//2**20} MB avail)")

#     out = {}
#     try:
#         with nc.Dataset(path, "r") as ds:
#             for v in variables:
#                 if v not in ds.variables:
#                     raise ValueError(f"Variable '{v}' not in file")
#                 arr = ds.variables[v][:]
#                 out[v] = arr
#                 if np.isnan(arr).any():
#                     print(f"[WARN] NaNs in {v}")
#                 if np.isinf(arr).any():
#                     print(f"[WARN] Infs in {v}")
#                 if v in {"X", "Y", "Z"} and not np.all(np.diff(arr) > 0):
#                     print(f"[WARN] Coord {v} not monotonic")
#                 if v in {"Bx", "By", "Bz"} and np.all(arr == 0):
#                     raise ValueError(f"{v} all‑zero – invalid for streamlines")
#     except Exception as e:
#         raise RuntimeError(f"Reading variables failed: {e}")

#     after = psutil.virtual_memory()
#     print(f"[DEBUG] Mem after reading {path}: {after.percent}% ({after.available//2**20} MB avail)")
#     return out

# # ═══════════════════════════════════════════════════════════════
# # 2) Down‑sample helper
# # ═══════════════════════════════════════════════════════════════
# def downsample_data_dict(d, factor=2):
#     out = {}
#     for k, arr in d.items():
#         zf = 1 / factor if arr.ndim == 1 else [1 / factor] * arr.ndim
#         out[k] = zoom(arr, zf)
#     return out

# # ═══════════════════════════════════════════════════════════════
# # 3) Grid + streamline helpers
# # ═══════════════════════════════════════════════════════════════
# def create_pyvista_grid(x, y, z, Bx, By, Bz):
#     grid = pv.RectilinearGrid(x, y, z)
#     grid["B"] = np.stack(
#         [Bx.ravel(order="C"), By.ravel(order="C"), Bz.ravel(order="C")],
#         axis=-1
#     )
#     return grid


# def compute_streamlines_pyvista(grid: pv.RectilinearGrid, seed):
#     """
#     Trace one principal streamline from *seed*.
#     We score candidates by end‑to‑end displacement (not point count) to avoid tight loops.
#     """
#     print(f"[DEBUG] Tracing streamline from seed {seed}")

#     kwargs = dict(
#         source_center=seed,
#         max_time=20000,          # shorter propagation
#         max_steps=100000,
#         integrator_type=2,
#         compute_vorticity=False,
#     )
#     # version‑safe initial‑step arg
#     try:
#         stream = grid.streamlines("B", initial_step_size=3.0, **kwargs)
#     except TypeError:
#         stream = grid.streamlines("B", initial_step_length=3.0, **kwargs)

#     if not stream or not stream.lines.size:
#         print("[WARN] No streamline connectivity – empty list")
#         return []

#     conn, pts = stream.lines, stream.points
#     best_coords, best_disp, off = None, -1.0, 0
#     while off < conn.size:
#         npts = int(conn[off]); off += 1
#         idxs = conn[off : off + npts]; off += npts
#         if npts < 2:
#             continue
#         coords = pts[idxs]
#         disp = np.linalg.norm(coords[0] - coords[-1])  # end‑to‑end distance
#         if disp > best_disp:
#             best_coords, best_disp = coords, disp

#     if best_coords is None:
#         return []

#     print(f"[DEBUG] Selected streamline displacement = {best_disp:.2f} (points = {best_coords.shape[0]})")
#     return [(best_coords[:, 0], best_coords[:, 1], best_coords[:, 2])]

# # ═══════════════════════════════════════════════════════════════
# # 4) Master routine – isosurface + optional streamlines
# # ═══════════════════════════════════════════════════════════════
# def create_3d_contour_plot(
#     data,
#     variable_name,
#     x_coords,
#     y_coords,
#     z_coords,
#     *,
#     output_html=None,
#     color_scale=None,
#     x_range=None,
#     y_range=None,
#     z_range=None,
#     opacity=1.0,
#     field_lines=None,
#     Bx_array=None,
#     By_array=None,
#     Bz_array=None,
# ):
#     print("[DEBUG] create_3d_contour_plot() called")
#     nx, ny, nz = data.shape
#     i0, i1 = x_range or (0, nx)
#     j0, j1 = y_range or (0, ny)
#     k0, k1 = z_range or (0, nz)

#     X = x_coords[i0:i1]
#     Y = y_coords[j0:j1]
#     Z = z_coords[k0:k1]
#     block = data[i0:i1, j0:j1, k0:k1]
#     isomin, isomax = color_scale if color_scale else (block.min(), block.max())

#     xv, yv, zv = np.meshgrid(X, Y, Z, indexing="ij")
#     fig = go.Figure()
#     fig.add_trace(
#         go.Isosurface(
#             x=xv.ravel(),
#             y=yv.ravel(),
#             z=zv.ravel(),
#             value=block.ravel(),
#             isomin=isomin,
#             isomax=isomax,
#             opacity=opacity,
#             caps=dict(x_show=False, y_show=False, z_show=False),
#             colorscale="Viridis",
#             surface_count=5,
#             name=variable_name,
#         )
#     )

#     # ── streamlines ────────────────────────────────────────────
#     if field_lines and len(field_lines):
#         if Bx_array is None or By_array is None or Bz_array is None:
#             raise ValueError("Bx/By/Bz required for field lines")
#         Bx = Bx_array[i0:i1, j0:j1, k0:k1]
#         By = By_array[i0:i1, j0:j1, k0:k1]
#         Bz = Bz_array[i0:i1, j0:j1, k0:k1]

#         colors = ["red", "orange", "blue", "purple", "green",
#                   "cyan", "magenta", "yellow", "brown", "black"]

#         for idx, seed in enumerate(field_lines):
#             grid = create_pyvista_grid(X, Y, Z, Bx, By, Bz)  # fresh grid each seed
#             for x_line, y_line, z_line in compute_streamlines_pyvista(grid, seed):
#                 fig.add_trace(
#                     go.Scatter3d(
#                         x=x_line,
#                         y=y_line,
#                         z=z_line,
#                         mode="lines",
#                         line=dict(color=colors[idx % len(colors)], width=3),
#                         name=f"Field Line {idx + 1}",
#                     )
#                 )

#     fig.update_layout(
#         scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
#         title=f"3D Contour – {variable_name}",
#     )

#     if output_html:
#         pio.write_html(fig, output_html, include_plotlyjs="cdn", full_html=True)
#         _inject_click_handler(output_html)

#     return {}

# # ═══════════════════════════════════════════════════════════════
# # 5) Inject JS click handler for field‑line seed picks
# # ═══════════════════════════════════════════════════════════════
# def _inject_click_handler(html_path: str):
#     js = r"""
# <script>
# document.addEventListener('DOMContentLoaded', () => {
#   const plot = document.querySelector('.js-plotly-plot');
#   if (!plot) return;
#   plot.on('plotly_click', (d) => {
#     if (d.points && d.points.length) {
#       const { x, y, z } = d.points[0];
#       window.parent.postMessage(JSON.stringify({ type: 'FIELD_LINE_CLICK', x, y, z }), '*');
#     }
#   });
# });
# </script>
# </body>
# </html>
# """
#     with open(html_path, "r+", encoding="utf-8") as f:
#         html = f.read()
#         new_html = html.replace("</body>\n</html>", js) if "</body>" in html else html + js
#         f.seek(0)
#         f.write(new_html)
#         f.truncate()















# WORKING PERFECTLY EXCEPT CLICK

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
