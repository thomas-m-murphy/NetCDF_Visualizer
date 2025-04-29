# import pyvista as pv
# import vtk

# # Enable GPU rendering features
# pv.global_theme.smooth_shading = True
# pv.global_theme.depth_peeling.enabled = True

# # Print rendering settings
# print("Using depth peeling:")
# print(f"    Number               : {pv.global_theme.depth_peeling.number_of_peels}")
# print(f"    Occlusion ratio      : {pv.global_theme.depth_peeling.occlusion_ratio}")
# print(f"    Enabled              : {pv.global_theme.depth_peeling.enabled}")
# print(f"Using anti-aliasing: {pv.global_theme.anti_aliasing}")
# print(f"Lighting settings: {pv.global_theme.lighting}")
# print(f"Shading settings: {pv.global_theme.smooth_shading}")

# # Check VTK OpenGL info (confirms if GPU is used)
# ren_win = vtk.vtkRenderWindow()
# ren_win.Render()
# info = ren_win.ReportCapabilities()

# print("\nVTK OpenGL Information:")
# print(info)






import pyvista as pv
import numpy as np

# Create a simple volume dataset
grid = pv.UniformGrid()
grid.dimensions = (50, 50, 50)
grid.spacing = (1, 1, 1)
grid.point_data["values"] = np.random.rand(50 * 50 * 50)

# Set up the plotter
plotter = pv.Plotter()
plotter.add_volume(grid, mapper="gpu", opacity="sigmoid")
plotter.show()



# import vtk
# print(f"VTK GPU Vendor: {vtk.vtkGraphicsFactory().GetOpenGLRenderer()}")
# print(f"VTK GPU Version: {vtk.vtkVersion.GetVTKSourceVersion()}")
