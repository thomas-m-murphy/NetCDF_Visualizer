# Project Structure: NetCDF Visualizer

This document explains the directory structure and the purpose of each file in the **NetCDF Visualizer** project.

---

## 📁 Directory Overview

### `/static/`
- Contains generated HTML and image files used for embedding visualizations into the webpage.
- Includes:
  - `3d_contour_plot.html`: Interactable 3D Plotly visualization of the selected variable.
  - `multiple_cross_section_3d.html`: 2D cross-sectional slices embedded in the interface.
  - `multi_variable_line_graph.png`: Time-series line plot (if generated).

### `/templates/`
- Contains HTML templates rendered by Flask.
- Includes:
  - `index.html`: Main web interface for uploading `.nc` files and visualizing data.
  - `linePlot.html`: Secondary interface for generating multi-variable line plots.

### `/uploads/`
- Temporary folder used to store uploaded `.nc` files.
- **Excluded from GitHub** via `.gitignore` to avoid uploading large files.

---

## 📄 Python Code Files

### `app.py`
- The main Flask application that:
  - Handles file uploads and form submissions.
  - Parses data and generates plots.
  - Manages field line generation and deletion.
  - Serves all frontend and backend logic for both 3D and time-series visualizations.

### `htmlPlotFieldLines.py`
- Generates 3D contour plots using Plotly.
- Traces magnetic field lines based on user input (either manual or click-based).
- Uses `Bx`, `By`, and `Bz` to calculate streamlines.
- Saves the rendered plot as an HTML file.

### `htmlPlotCrossSection.py`
- Generates 2D cross-section visualizations embedded into the main app.
- Supports slicing along X, Y, or Z axes with specified opacity and location.

### `plotLineGraph.py`
- Extracts data across multiple `.nc` files for a given (x, y, z) coordinate.
- Plots a line graph comparing multiple variables over time.

### `htmlPlotGenerator3D.py` (Legacy)
- Original prototype for generating 3D plots; now largely replaced by `htmlPlotFieldLines.py`.

### `psipyTest.py` (Experimental/Testing)
- Used to test compatibility with the `psipy` library or external tools.

---

## 🗂 Other Files

### `.gitignore`
- Ensures large or unnecessary files (like the `uploads/` folder) are not committed to the repository.

### `README.md`
- Provides installation instructions, usage information, and overview of project capabilities.

### `project_requirements.txt` (Optional / Legacy)
- Was previously used for environment setup. Now superseded by manually installing dependencies via `pip install`.

---

## 💡 Additional Notes

- The app supports both **manual input** and **clickable interactions** for placing field line seeds.
- All plots are interactive and can be explored via mouse drag, zoom, and rotation.
- This project is designed for NetCDF datasets containing 3D vector fields and spatial coordinates (`X`, `Y`, `Z`, `Bx`, `By`, `Bz`, etc.).

---

