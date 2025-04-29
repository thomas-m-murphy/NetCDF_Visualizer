# import os
# import numpy as np

# # Force Matplotlib to use the 'Agg' backend for non-GUI environments
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt

# from netCDF4 import Dataset

# def extract_data(folder_path, variables, x, y, z):
#     data_dict = {var: [] for var in variables}
#     file_list = sorted([f for f in os.listdir(folder_path) if f.endswith('.nc')])

#     for file_name in file_list:
#         file_path = os.path.join(folder_path, file_name)
#         with Dataset(file_path, 'r') as nc_file:
#             for var in variables:
#                 if var in nc_file.variables:
#                     var_data = nc_file.variables[var][:]
#                     data_dict[var].append(var_data[x, y, z])
#                 else:
#                     print(f"Variable '{var}' not found in {file_name}. Skipping this file.")
#     return data_dict

# def create_multi_plot(data_dict, variables, point):
#     """
#     Creates one subplot per variable, each showing a time-series line.
#     Removes the large title on each subplot, but keeps a small legend
#     indicating something like "Bx at (50, 50, 50)". Also moves the
#     subplots closer together vertically.
#     """
#     num_vars = len(variables)
#     # Make the figure a bit less tall per subplot
#     fig, axes = plt.subplots(num_vars, 1, figsize=(10, 4 * num_vars), sharex=True)

#     if num_vars == 1:
#         axes = [axes]

#     for ax, var in zip(axes, variables):
#         # Plot with a legend label like "Bx at (50, 50, 50)"
#         ax.plot(data_dict[var], marker='o', linestyle='-', label=f"{var} at {point}")
#         # Remove the old top title line:
#         # ax.set_title(f"Time Series of {var} at Point {point}")
#         ax.set_ylabel(var)
#         ax.grid(True)
#         # Keep the small legend so the user sees which variable/point
#         ax.legend()

#     # Label the bottom axis with "Time Step"
#     axes[-1].set_xlabel("Time Step")

#     # Move subplots closer (less vertical spacing)
#     fig.tight_layout()
#     # Alternatively: fig.subplots_adjust(hspace=0.3)

#     output_path = "static/multi_variable_line_graph.png"
#     plt.savefig(output_path)
#     print(f"Multi-variable line graph saved as {output_path}")
#     plt.close()









import os
import numpy as np

# Force Matplotlib to use the 'Agg' backend for non-GUI environments
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from netCDF4 import Dataset

def extract_data(folder_path, variables, user_x, user_y, user_z):
    """
    Extracts data for the closest (X, Y, Z) coordinates based on user input.
    Assumes X, Y, Z hold coordinates in the range [-30, 30].
    Finds the closest index for each coordinate.
    """
    data_dict = {var: [] for var in variables}
    file_list = sorted([f for f in os.listdir(folder_path) if f.endswith('.nc')])

    first_print = True  # Ensure we only print closest indices once

    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        with Dataset(file_path, 'r') as nc_file:
            # Read X, Y, Z coordinate arrays
            X = nc_file.variables['X'][:]
            Y = nc_file.variables['Y'][:]
            Z = nc_file.variables['Z'][:]

            # Find closest indices in X, Y, Z
            index_x = np.abs(X - user_x).argmin()
            index_y = np.abs(Y - user_y).argmin()
            index_z = np.abs(Z - user_z).argmin()

            # Print only once
            if first_print:
                print(f"Closest indices found: X[{index_x}] ≈ {X[index_x]}, "
                      f"Y[{index_y}] ≈ {Y[index_y]}, Z[{index_z}] ≈ {Z[index_z]}")
                first_print = False  # Prevent further prints

            # Extract data for each selected variable
            for var in variables:
                if var in nc_file.variables:
                    var_data = nc_file.variables[var][:]
                    data_dict[var].append(var_data[index_x, index_y, index_z])
                else:
                    print(f"Variable '{var}' not found in {file_name}. Skipping.")

    return data_dict

def create_multi_plot(data_dict, variables, point):
    """
    Creates one subplot per variable, each showing a time-series line.
    Removes the large title on each subplot, but keeps a small legend
    indicating something like "Bx at (50, 50, 50)". Also moves the
    subplots closer together vertically.
    """
    num_vars = len(variables)
    # Make the figure a bit less tall per subplot
    fig, axes = plt.subplots(num_vars, 1, figsize=(10, 4 * num_vars), sharex=True)

    if num_vars == 1:
        axes = [axes]

    for ax, var in zip(axes, variables):
        # Plot with a legend label like "Bx at (50, 50, 50)"
        ax.plot(data_dict[var], marker='o', linestyle='-', label=f"{var} at {point}")
        # Remove the old top title line:
        # ax.set_title(f"Time Series of {var} at Point {point}")
        ax.set_ylabel(var)
        ax.grid(True)
        # Keep the small legend so the user sees which variable/point
        ax.legend()

    # Label the bottom axis with "Time Step"
    axes[-1].set_xlabel("Time Step")

    # Move subplots closer (less vertical spacing)
    fig.tight_layout()
    # Alternatively: fig.subplots_adjust(hspace=0.3)

    output_path = "static/multi_variable_line_graph.png"
    plt.savefig(output_path)
    print(f"Multi-variable line graph saved as {output_path}")
    plt.close()
