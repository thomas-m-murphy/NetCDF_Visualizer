# import netCDF4 as nc
# import numpy as np
# import plotly.graph_objects as go
# import plotly.io as pio
# from scipy.ndimage import zoom
# from scipy.interpolate import RegularGridInterpolator
# from scipy.integrate import solve_ivp

# def read_nc_variables(file_path, variable_names):
#     data = {}
#     try:
#         with nc.Dataset(file_path, 'r') as ds:
#             for varname in variable_names:
#                 if varname in ds.variables:
#                     data[varname] = ds.variables[varname][:]
#                 else:
#                     raise ValueError(f"Variable '{varname}' not found in {file_path}")
#         return data
#     except Exception as e:
#         raise RuntimeError(f"Error reading {variable_names} from {file_path}: {e}")

# def downsample_data_dict(data_dict, factor=2):
#     downsampled_data = {}
#     for key, arr in data_dict.items():
#         if arr.ndim == 1:
#             downsampled_data[key] = zoom(arr, zoom=1/factor)
#         else:
#             zoom_factors = [1/factor]*arr.ndim
#             downsampled_data[key] = zoom(arr, zoom=zoom_factors)
#     return downsampled_data

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
#     Bx_interp=None,
#     By_interp=None,
#     Bz_interp=None
# ):
#     """
#     Creates a 3D interactive contour plot from 'data' with optional integrated 
#     field lines, using a diff eq approach in Cartesian.
#     """
#     nx, ny, nz = data.shape

#     # Index slicing
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
#     data_used = data[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]

#     xv, yv, zv = np.meshgrid(X_used, Y_used, Z_used, indexing='ij')

#     isomin = np.min(data_used) if color_scale is None else color_scale[0]
#     isomax = np.max(data_used) if color_scale is None else color_scale[1]

#     fig = go.Figure()

#     # 1) Add isosurface
#     fig.add_trace(go.Isosurface(
#         x=xv.flatten(),
#         y=yv.flatten(),
#         z=zv.flatten(),
#         value=data_used.flatten(),
#         isomin=isomin,
#         isomax=isomax,
#         opacity=opacity,
#         caps=dict(x_show=False, y_show=False, z_show=False),
#         colorscale='Viridis',
#         surface_count=5,
#         name=f'{variable_name}'
#     ))

#     # 2) Integrate lines, if seeds exist
#     if field_lines and Bx_interp and By_interp and Bz_interp:
#         def field_line_ode(s, pos):
#             px, py, pz = pos
#             try:
#                 Bx_val = Bx_interp((px, py, pz))
#                 By_val = By_interp((px, py, pz))
#                 Bz_val = Bz_interp((px, py, pz))
#             except ValueError:
#                 # Out-of-bounds => zero to stop
#                 return [0,0,0]

#             B_mag = np.sqrt(Bx_val**2 + By_val**2 + Bz_val**2)
#             if B_mag == 0 or np.isnan(B_mag):
#                 return [0,0,0]
#             return [Bx_val/B_mag, By_val/B_mag, Bz_val/B_mag]

#         s_max = 300  
#         step_size = 1  

#         color_list = ['red','orange','blue','purple','green','cyan','magenta','yellow','brown','black']

#         for idx, (sx, sy, sz) in enumerate(field_lines):
#             color = color_list[idx % len(color_list)]

#             try:
#                 # Integrate forward
#                 sol_fwd = solve_ivp(
#                     field_line_ode,
#                     [0, s_max],
#                     [sx, sy, sz],
#                     max_step=step_size,
#                     dense_output=False
#                 )
#                 # Integrate backward
#                 sol_bwd = solve_ivp(
#                     field_line_ode,
#                     [0, -s_max],
#                     [sx, sy, sz],
#                     max_step=step_size,
#                     dense_output=False
#                 )

#             except Exception as e:
#                 print(f"Error integrating line {idx+1} from seed {sx,sy,sz}: {e}")
#                 continue  # skip this line

#             # Combine forward/backward
#             if sol_fwd.success and sol_bwd.success:
#                 x_line = np.concatenate([sol_bwd.y[0][::-1], sol_fwd.y[0]])
#                 y_line = np.concatenate([sol_bwd.y[1][::-1], sol_fwd.y[1]])
#                 z_line = np.concatenate([sol_bwd.y[2][::-1], sol_fwd.y[2]])
#             else:
#                 # If either failed
#                 print(f"Line {idx+1} integration not successful.")
#                 continue

#             # Optionally clip lines to domain
#             x_line = np.clip(x_line, X_used[0], X_used[-1])
#             y_line = np.clip(y_line, Y_used[0], Y_used[-1])
#             z_line = np.clip(z_line, Z_used[0], Z_used[-1])

#             fig.add_trace(go.Scatter3d(
#                 x=x_line,
#                 y=y_line,
#                 z=z_line,
#                 mode='lines',
#                 line=dict(color=color, width=3),
#                 name=f'Field Line {idx+1}'
#             ))

#     # 3) Let Plotly auto-range so lines are visible
#     fig.update_layout(
#         scene=dict(
#             xaxis=dict(title='X', autorange=True),
#             yaxis=dict(title='Y', autorange=True),
#             zaxis=dict(title='Z', autorange=True)
#         ),
#         title=f'3D Contour Plot of {variable_name}'
#     )

#     if output_html:
#         pio.write_html(fig, output_html, include_plotlyjs='cdn', full_html=False)
#         print(f"3D Contour Plot saved as {output_html}")
#     else:
#         return fig.to_dict()


















import netCDF4 as nc
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from scipy.ndimage import zoom

import pyvista as pv


####################################################
# 1) Read NetCDF data
####################################################
def read_nc_variables(file_path, variable_names):
    data = {}
    try:
        with nc.Dataset(file_path, 'r') as ds:
            for varname in variable_names:
                if varname in ds.variables:
                    data[varname] = ds.variables[varname][:]
                else:
                    raise ValueError(f"Variable '{varname}' not found in {file_path}")
        return data
    except Exception as e:
        raise RuntimeError(f"Error reading {variable_names} from {file_path}: {e}")


####################################################
# 2) Downsample by factor=2
####################################################
def downsample_data_dict(data_dict, factor=2):
    """
    Downsample arrays by a given factor. This reduces data size ~8x
    for 3D arrays, speeding up PyVista's streamlines but keeping
    some resolution vs. factor=4.
    """
    downsampled = {}
    for key, arr in data_dict.items():
        if arr.ndim == 1:
            # 1D coords
            downsampled[key] = zoom(arr, zoom=1/factor)
        else:
            # 2D/3D
            zf = [1/factor]*arr.ndim
            downsampled[key] = zoom(arr, zoom=zf)
    return downsampled


####################################################
# 3) Build a PyVista RectilinearGrid
####################################################
def create_pyvista_grid(x_coords, y_coords, z_coords, Bx, By, Bz):
    """
    x_coords, y_coords, z_coords: 1D arrays
    Bx, By, Bz: 3D arrays [nx, ny, nz]
    """
    rgrid = pv.RectilinearGrid(x_coords, y_coords, z_coords)

    vectors = np.stack([
        Bx.ravel(order='C'),
        By.ravel(order='C'),
        Bz.ravel(order='C')
    ], axis=-1)

    rgrid['B'] = vectors
    return rgrid


####################################################
# 4) Compute streamlines with adjusted parameters
####################################################
def compute_streamlines_pyvista(grid, seed_point):
    """
    Uses PyVista's .streamlines(...) method with tuned parameters:
      - max_time=9999
      - initial_step_size=2.0 (larger => fewer steps => faster)
      - n_points=1000 (moderate => won't produce too many points)
      - max_steps=100000 (limit swirling)
      - integrator_type=2 (RK4/5)

    Fallback for older PyVista => only pass max_time=9999.
    """
    try:
        # Newer PyVista (>=0.38) has PointSet
        source = pv.PointSet()
        source.points = np.array([seed_point])
    except AttributeError:
        # older PyVista fallback
        source = pv.PolyData([seed_point])

    if hasattr(grid, "streamlines"):
        # Attempt passing the updated parameters
        try:
            stream = grid.streamlines(
                'B',
                source_center=seed_point,
                max_time=9999,
                initial_step_size=3.0,
                n_points=10000,
                max_steps=100000,
                integrator_type=2
            )
        except TypeError:
            # If old PyVista complains about some args, remove them
            stream = grid.streamlines(
                'B',
                source_center=seed_point,
                max_time=9999,
                integrator_type=2
            )
    else:
        # Very old PyVista => fallback
        stream = grid.streamlines_from_source(
            source,
            'B',
            max_time=9999
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
    return lines


####################################################
# 5) Create the 3D Contour Plot + Streamlines
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
    """
    Creates a 3D Plotly isosurface of 'data' and uses PyVista for
    field lines from seeds in 'field_lines'. The streamline
    parameters are chosen to allow longer lines but faster runtime
    by using a larger step size and moderate n_points.
    """
    nx, ny, nz = data.shape

    # Index slicing
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

    data_used = data[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]

    # Determine color scale
    isomin = np.min(data_used) if color_scale is None else color_scale[0]
    isomax = np.max(data_used) if color_scale is None else color_scale[1]

    xv, yv, zv = np.meshgrid(X_used, Y_used, Z_used, indexing='ij')

    # Plotly figure
    fig = go.Figure()

    # Add isosurface
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

    # Field lines
    if field_lines and len(field_lines) > 0:
        if Bx_array is None or By_array is None or Bz_array is None:
            raise ValueError("Bx, By, Bz arrays not provided for streamlines.")

        # Slice B arrays
        Bx_used = Bx_array[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]
        By_used = By_array[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]
        Bz_used = Bz_array[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]

        # Create PyVista grid
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

    # Layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X', autorange=True),
            yaxis=dict(title='Y', autorange=True),
            zaxis=dict(title='Z', autorange=True)
        ),
        title=f"3D Contour Plot of {variable_name}"
    )

    # Return or save
    if output_html:
        pio.write_html(fig, output_html, include_plotlyjs='cdn', full_html=False)
        print(f"3D Contour Plot saved as {output_html}")
        return None
    else:
        return fig.to_dict()