
# import netCDF4 as nc
# import numpy as np
# import plotly.graph_objects as go
# import plotly.io as pio
# import os
# from scipy.ndimage import zoom

# def read_nc_file(file_path, variable_name):
#     """
#     Reads the specified variable from a .nc file.
#     """
#     try:
#         with nc.Dataset(file_path, 'r') as dataset:
#             if variable_name in dataset.variables:
#                 data = dataset.variables[variable_name][:]
#             else:
#                 raise ValueError(f"Variable '{variable_name}' not found in the file.")
#     except Exception as e:
#         raise RuntimeError(f"Error reading {variable_name} from {file_path}: {e}")
    
#     return data

# def downsample_data(data, factor=2):
#     """
#     Downsamples the data by a given factor using interpolation.
#     """
#     return zoom(data, zoom=1/factor)

# def scale_user_input(input_range, factor=2.01):
#     """
#     Scales the user input range to match the downsampled data range.
#     """
#     return (int(input_range[0] / factor), int(input_range[1] / factor))

# def create_3d_contour_plot(data, variable_name, x_coords, y_coords, z_coords, output_html, color_scale=None, x_range=None, y_range=None, z_range=None, opacity=1.0):
#     """
#     Creates a smaller HTML 3D interactive contour plot from the data with user-specified opacity.
#     """
#     # Determine the actual lengths of the data arrays
#     nx, ny, nz = data.shape

#     # Apply slicing based on scaled ranges
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

#     # Slice the data and coordinates
#     x_coords = x_coords[x_min_idx:x_max_idx]
#     y_coords = y_coords[y_min_idx:y_max_idx]
#     z_coords = z_coords[z_min_idx:z_max_idx]
#     data = data[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]

#     # Set isomin and isomax based on the data or a user-defined range
#     isomin = np.min(data) if color_scale is None else color_scale[0]
#     isomax = np.max(data) if color_scale is None else color_scale[1]

#     # Create the 3D plot with user-specified opacity
#     fig = go.Figure(data=go.Isosurface(
#         x=np.repeat(x_coords, len(y_coords) * len(z_coords)),
#         y=np.tile(np.repeat(y_coords, len(z_coords)), len(x_coords)),
#         z=np.tile(z_coords, len(x_coords) * len(y_coords)),
#         value=data.flatten(),
#         isomin=isomin,
#         isomax=isomax,
#         caps=dict(x_show=False, y_show=False, z_show=False),
#         colorscale='Viridis',
#         opacity=opacity / 100,  # Apply user-specified opacity
#         surface_count=5  # Reduce the number of surfaces to save space
#     ))

#     fig.update_layout(
#         scene=dict(
#             xaxis_title='X (Re)',
#             yaxis_title='Y (Re)',
#             zaxis_title='Z (Re)'
#         ),
#         title=f'3D Contour Plot of {variable_name}',
#     )

#     # Save the plot as an HTML file
#     pio.write_html(fig, output_html, include_plotlyjs='cdn', full_html=False)
#     print(f'3D Contour Plot saved as {output_html}')

# if __name__ == "__main__":
#     file_path = "/Users/thomasmurphy/Desktop/GRA/ncReader/data/field00720.nc"
#     variable_name = "Bx"  # Replace with the variable you want to visualize

#     if os.path.exists(file_path):
#         try:
#             # Read in the data and coordinates
#             data = read_nc_file(file_path, variable_name)
#             x_coords = read_nc_file(file_path, 'X')
#             y_coords = read_nc_file(file_path, 'Y')
#             z_coords = read_nc_file(file_path, 'Z')

#             # Downsample data to reduce size
#             data = downsample_data(data, factor=2)
#             x_coords = downsample_data(x_coords, factor=2)
#             y_coords = downsample_data(y_coords, factor=2)
#             z_coords = downsample_data(z_coords, factor=2)

#             # Get user input for x, y, z ranges in the original scale (0 to 201)
#             user_x_range = (0, 201)  # Example input, replace with actual user input
#             user_y_range = (0, 201)  # Example input, replace with actual user input
#             user_z_range = (0, 201)  # Example input, replace with actual user input

#             # Scale the user input to match the downsampled data scale
#             x_range = scale_user_input(user_x_range)
#             y_range = scale_user_input(user_y_range)
#             z_range = scale_user_input(user_z_range)

#             # Adjust color scale range to focus on values near 0
#             color_scale_range = (-1, 1)  # Adjust this range as needed

#             # Set the opacity value (for testing)
#             opacity_value = 50  # Example: 50% opacity, adjust as needed

#             create_3d_contour_plot(data, variable_name, x_coords, y_coords, z_coords, 
#                                    color_scale=color_scale_range, x_range=x_range, 
#                                    y_range=y_range, z_range=z_range, opacity=opacity_value)
#         except Exception as e:
#             print(f"An error occurred: {e}")
#     else:
#         print(f"File not found: {file_path}")













import netCDF4 as nc
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import os
from scipy.ndimage import zoom

def read_nc_file(file_path, variable_name):
    """
    Reads the specified variable from a .nc file.
    """
    try:
        with nc.Dataset(file_path, 'r') as dataset:
            if variable_name in dataset.variables:
                data = dataset.variables[variable_name][:]
            else:
                raise ValueError(f"Variable '{variable_name}' not found in the file.")
    except Exception as e:
        raise RuntimeError(f"Error reading {variable_name} from {file_path}: {e}")
    
    return data

def downsample_data(data, factor=2):
    """
    Downsamples the data by a given factor using interpolation.
    """
    return zoom(data, zoom=1/factor)

def scale_user_input(input_range, factor=2.01):
    """
    Scales the user input range to match the downsampled data range.
    """
    return (int(input_range[0] / factor), int(input_range[1] / factor))

def create_3d_contour_plot(data, variable_name, x_coords, y_coords, z_coords, output_html, color_scale=None, x_range=None, y_range=None, z_range=None, opacity=1.0):
    """
    Creates a smaller HTML 3D interactive contour plot from the data with opacity.
    """
    # Determine the actual lengths of the data arrays
    nx, ny, nz = data.shape

    # Apply slicing based on scaled ranges
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

    # Slice the data and coordinates
    x_coords = x_coords[x_min_idx:x_max_idx]
    y_coords = y_coords[y_min_idx:y_max_idx]
    z_coords = z_coords[z_min_idx:z_max_idx]
    data = data[x_min_idx:x_max_idx, y_min_idx:y_max_idx, z_min_idx:z_max_idx]

    # Set isomin and isomax based on the data or a user-defined range
    isomin = np.min(data) if color_scale is None else color_scale[0]
    isomax = np.max(data) if color_scale is None else color_scale[1]

    fig = go.Figure(data=go.Isosurface(
        x=np.repeat(x_coords, len(y_coords) * len(z_coords)),
        y=np.tile(np.repeat(y_coords, len(z_coords)), len(x_coords)),
        z=np.tile(z_coords, len(x_coords) * len(y_coords)),
        value=data.flatten(),
        isomin=isomin,
        isomax=isomax,
        opacity=opacity / 100,  # Apply user-specified opacity
        caps=dict(x_show=False, y_show=False, z_show=False),
        colorscale='Viridis',
        surface_count=5  # Reduce the number of surfaces to save space
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='X (Re)',
            yaxis_title='Y (Re)',
            zaxis_title='Z (Re)'
        ),
        title=f'3D Contour Plot of {variable_name}',
    )

    # Save the plot as an HTML file
    pio.write_html(fig, output_html, include_plotlyjs='cdn', full_html=False)
    print(f'3D Contour Plot saved as {output_html}')
