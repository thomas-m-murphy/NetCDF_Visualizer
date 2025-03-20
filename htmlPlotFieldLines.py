

# import netCDF4 as nc
# import numpy as np
# import plotly.graph_objects as go
# import plotly.io as pio
# from scipy.ndimage import zoom

# import pyvista as pv
# import psutil  # For memory checks


# # -----------------------------------------------------
# #  GPU-BASED RENDERING OPTIMIZATIONS (OPTIONAL)
# # -----------------------------------------------------
# pv.global_theme.depth_peeling.number_of_peels = 4
# pv.global_theme.depth_peeling.occlusion_ratio = 0.0
# pv.global_theme.depth_peeling.enabled = True
# pv.global_theme.anti_aliasing = "fxaa"
# pv.global_theme.volume_mapper = "gpu"
# pv.OFF_SCREEN = False
# pv.global_theme.smooth_shading = True
# pv.global_theme.render_lines_as_tubes = True
# pv.global_theme.multi_samples = 8

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
#                     # Check monotonic coords
#                     if varname in ["X", "Y", "Z"]:
#                         diffs = np.diff(arr)
#                         if not np.all(diffs > 0):
#                             print(f"[WARNING] Coordinate '{varname}' is not strictly increasing.")
#                     # Check zero B
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
#         # fallback if older PyVista
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
#     output_html=None,   # => saved HTML
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

#     # If we have seeds => compute streamlines
#     if field_lines and len(field_lines) > 0:
#         if Bx_array is None or By_array is None or Bz_array is None:
#             raise ValueError("Bx,By,Bz arrays not provided for streamlines.")

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

#     # If the caller wants an HTML file => save it
#     if output_html:
#         print(f"[DEBUG] Saving final 3D HTML => {output_html}")
#         pio.write_html(fig, output_html, include_plotlyjs='cdn', full_html=True)

#     # Return a minimal dict or something if needed
#     return {}
























import netCDF4 as nc
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from scipy.ndimage import zoom

import pyvista as pv
import psutil  # For memory checks

# -----------------------------------------------------
# GPU-BASED RENDERING OPTIMIZATIONS (OPTIONAL)
# -----------------------------------------------------
pv.global_theme.depth_peeling.number_of_peels = 4
pv.global_theme.depth_peeling.occlusion_ratio = 0.0
pv.global_theme.depth_peeling.enabled = True
pv.global_theme.anti_aliasing = "fxaa"
pv.global_theme.volume_mapper = "gpu"
pv.OFF_SCREEN = False
pv.global_theme.smooth_shading = True
pv.global_theme.render_lines_as_tubes = True
pv.global_theme.multi_samples = 8

print(f"GPU Accelerated Rendering: {pv.OFF_SCREEN}")
print("PyVista GPU Rendering Settings Applied!")


####################################################
# 1) Read NetCDF data (with debug checks)
####################################################
def read_nc_variables(file_path, variable_names):
    """
    Reads the specified variables from a NetCDF file and returns them in a dict.
    Prints debug statements if any issues (NaN, Inf, monotonic coords, zero field) are found.
    """
    mem_info_before = psutil.virtual_memory()
    print(f"[DEBUG] Memory usage before reading {file_path}: {mem_info_before.percent}% "
          f"({mem_info_before.available//(1024**2)} MB available)")

    data = {}
    try:
        with nc.Dataset(file_path, 'r') as ds:
            for varname in variable_names:
                if varname in ds.variables:
                    arr = ds.variables[varname][:]
                    data[varname] = arr

                    # Debug checks
                    if np.isnan(arr).any():
                        print(f"[WARNING] NaN values found in '{varname}'.")
                    if np.isinf(arr).any():
                        print(f"[WARNING] Inf values found in '{varname}'.")
                    if varname in ["X", "Y", "Z"]:
                        diffs = np.diff(arr)
                        if not np.all(diffs > 0):
                            print(f"[WARNING] Coordinate '{varname}' is not strictly increasing.")
                    if varname in ["Bx", "By", "Bz"]:
                        if np.all(arr == 0):
                            print(f"[WARNING] Variable '{varname}' is entirely zero.")
                else:
                    raise ValueError(f"Variable '{varname}' not found in {file_path}")

        mem_info_after = psutil.virtual_memory()
        print(f"[DEBUG] Memory usage after reading {file_path}: {mem_info_after.percent}% "
              f"({mem_info_after.available//(1024**2)} MB available)")
        return data
    except Exception as e:
        raise RuntimeError(f"Error reading {variable_names} from {file_path}: {e}")


####################################################
# 2) Downsample by factor=2
####################################################
def downsample_data_dict(data_dict, factor=2):
    downsampled = {}
    for key, arr in data_dict.items():
        if arr.ndim == 1:
            downsampled[key] = zoom(arr, zoom=1/factor)
        else:
            zf = [1/factor]*arr.ndim
            downsampled[key] = zoom(arr, zoom=zf)
    return downsampled


####################################################
# 3) Build a PyVista RectilinearGrid
####################################################
def create_pyvista_grid(x_coords, y_coords, z_coords, Bx, By, Bz):
    rgrid = pv.RectilinearGrid(x_coords, y_coords, z_coords)
    vectors = np.stack([
        Bx.ravel(order='C'),
        By.ravel(order='C'),
        Bz.ravel(order='C')
    ], axis=-1)
    rgrid['B'] = vectors
    return rgrid


####################################################
# 4) Compute streamlines with extended parameters
####################################################
def compute_streamlines_pyvista(grid, seed_point):
    print(f"[DEBUG] Computing streamlines for seed point: {seed_point}")
    try:
        source = pv.PointSet()
        source.points = np.array([seed_point])
    except AttributeError:
        source = pv.PolyData([seed_point])

    if hasattr(grid, "streamlines"):
        try:
            stream = grid.streamlines(
                'B',
                source_center=seed_point,
                max_time=999999,
                initial_step_size=3.0,
                n_points=2000,
                max_steps=500000,
                integrator_type=2
            )
        except TypeError:
            stream = grid.streamlines(
                'B',
                source_center=seed_point,
                max_time=999999,
                integrator_type=2
            )
    else:
        stream = grid.streamlines_from_source(
            source,
            'B',
            max_time=999999
        )

    lines = []
    connectivity = stream.lines
    pts = stream.points
    offset = 0
    if connectivity.size > 0:
        npts = connectivity[offset]
        offset += 1
        idxs = connectivity[offset : offset + npts]
        offset += npts
        coords = pts[idxs]
        x_line = coords[:, 0]
        y_line = coords[:, 1]
        z_line = coords[:, 2]
        lines.append((x_line, y_line, z_line))
    else:
        print("[WARNING] No streamline connectivity found; empty line.")

    return lines


####################################################
# 5) Create the 3D Contour Plot + Streamlines => HTML
####################################################
def create_3d_contour_plot(
    data,
    variable_name,
    x_coords,
    y_coords,
    z_coords,
    output_html=None,
    color_scale=None,
    x_range=None,
    y_range=None,
    z_range=None,
    opacity=1.0,
    field_lines=None,
    Bx_array=None,
    By_array=None,
    Bz_array=None
):
    print("[DEBUG] Inside create_3d_contour_plot()")

    nx, ny, nz = data.shape
    print(f"[DEBUG] Data shape: {nx}x{ny}x{nz}")

    # Slicing
    if x_range:
        x_min_idx, x_max_idx = x_range
    else:
        x_min_idx, x_max_idx = 0, nx
    if y_range:
        y_min_idx, y_max_idx = y_range
    else:
        y_min_idx, y_max_idx = 0, ny
    if z_range:
        z_min_idx, z_max_idx = z_range
    else:
        z_min_idx, z_max_idx = 0, nz

    X_used = x_coords[x_min_idx:x_max_idx]
    Y_used = y_coords[y_min_idx:y_max_idx]
    Z_used = z_coords[z_min_idx:z_max_idx]
    print("[DEBUG] Extracted coordinate ranges")

    data_used = data[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]

    # Color scale
    isomin = np.min(data_used) if color_scale is None else color_scale[0]
    isomax = np.max(data_used) if color_scale is None else color_scale[1]
    print(f"[DEBUG] isomin={isomin}, isomax={isomax}")

    xv, yv, zv = np.meshgrid(X_used, Y_used, Z_used, indexing='ij')
    print("[DEBUG] Meshgrid created")

    fig = go.Figure()

    print("[DEBUG] Adding isosurface to figure...")
    fig.add_trace(go.Isosurface(
        x=xv.ravel(),
        y=yv.ravel(),
        z=zv.ravel(),
        value=data_used.ravel(),
        isomin=isomin,
        isomax=isomax,
        opacity=opacity,
        caps=dict(x_show=False, y_show=False, z_show=False),
        colorscale='Viridis',
        surface_count=5,
        name=f'{variable_name}'
    ))
    print("[DEBUG] Isosurface added successfully!")

    # If seeds => compute lines
    if field_lines and len(field_lines) > 0:
        if Bx_array is None or By_array is None or Bz_array is None:
            raise ValueError("Bx, By, Bz arrays not provided for streamlines.")

        Bx_used = Bx_array[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]
        By_used = By_array[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]
        Bz_used = Bz_array[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]

        grid = create_pyvista_grid(X_used, Y_used, Z_used, Bx_used, By_used, Bz_used)

        color_list = ['red','orange','blue','purple','green',
                      'cyan','magenta','yellow','brown','black']

        for idx, (sx, sy, sz) in enumerate(field_lines):
            line_segments = compute_streamlines_pyvista(grid, (sx, sy, sz))
            color = color_list[idx % len(color_list)]
            for (x_line, y_line, z_line) in line_segments:
                fig.add_trace(go.Scatter3d(
                    x=x_line,
                    y=y_line,
                    z=z_line,
                    mode='lines',
                    line=dict(color=color, width=3),
                    name=f'Field Line {idx+1}'
                ))
        print("[DEBUG] Streamlines added successfully.")

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X'),
            yaxis=dict(title='Y'),
            zaxis=dict(title='Z'),
        ),
        title=f"3D Contour Plot of {variable_name}"
    )

    # If user wants an HTML => save it
    if output_html:
        print(f"[DEBUG] Saving final 3D HTML => {output_html}")
        pio.write_html(fig, output_html, include_plotlyjs='cdn', full_html=True)

        # -----------------------------------------------------------
        # Inject code to allow user clicks => parent page postMessage
        # We'll read that file content, append a small <script> block.
        # -----------------------------------------------------------
        injection_script = r"""
<script>
document.addEventListener("DOMContentLoaded", function(){
  var plotDiv = document.getElementsByClassName("js-plotly-plot")[0];
  if(!plotDiv){return;}
  // Listen for Plotly clicks
  plotDiv.on("plotly_click", function(d){
    if(d && d.points && d.points.length>0){
      var pt = d.points[0];
      var msg = {
        type: "FIELD_LINE_CLICK",
        x: pt.x,
        y: pt.y,
        z: pt.z
      };
      window.parent.postMessage(JSON.stringify(msg), "*");
    }
  });
});
</script>
</body>
</html>
"""
        with open(output_html, 'r+', encoding='utf-8') as f:
            content = f.read()
            # Replace the final </body></html> with injection
            if '</body>' in content:
                new_content = content.replace('</body>\n</html>', injection_script)
            else:
                # fallback
                new_content = content + injection_script
            f.seek(0)
            f.write(new_content)
            f.truncate()

    return {}
