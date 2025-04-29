# `flaskApp` – Application Core

This directory contains the Flask server and all plotting/data‑handling modules for **NetCDF Visualizer**.

```text
flaskApp/
├── app.py
├── htmlPlotFieldLines.py
├── htmlPlotCrossSection.py
├── htmlPlotGenerator3D.py
├── plotLineGraph.py
├── templates/
│   ├── index.html
│   ├── linePlot.html
│   └── … (other Jinja2 pages)
├── static/
│   ├── 3d_contour_plot.html            # generated on‑the‑fly
│   ├── multiple_cross_section_3d.html  # generated on‑the‑fly
│   └── multi_variable_line_graph.png   # generated on‑the‑fly
├── uploads/     # user‑uploaded .nc files   (ignored by Git)
└── fldData/     # cached/processed data     (ignored by Git)
```

---

## 1. Entry point

| File | Purpose |
|------|---------|
| **`app.py`** | The main Flask application.<br>Routes:<br>• `/` – file upload UI.<br>• `/upload` – processes the uploaded NetCDF file and builds the initial 3‑D plot.<br>• `/field-line` – add a new seed and rebuild plot with streamlines.<br>• `/delete-field-line` – remove a seed.<br>• `/generate-line-plot` – create multi‑variable time‑series graphs. |

---

## 2. Plotting & Data Modules

| Module | Key functions | Notes |
|--------|---------------|-------|
| **`htmlPlotFieldLines.py`** | `create_3d_contour_plot`, `compute_streamlines_pyvista` | Builds the 3‑D isosurface (Plotly) and traces magnetic field lines (PyVista/VTK). |
| **`htmlPlotCrossSection.py`** | `plot_multiple_2d_cross_sections_3d` | Renders up to three orthogonal slices in a single HTML file. |
| **`htmlPlotGenerator3D.py`** | Low‑level helper used by `htmlPlotFieldLines` for isosurface generation. |
| **`plotLineGraph.py`** | `extract_data`, `create_multi_plot` | Extracts variable time series at a given coordinate and saves a PNG line graph. |

---

## 3. Templates

*Stored in `templates/` and rendered by Flask using Jinja2.*

| Template | Purpose |
|----------|---------|
| `index.html`     | Main dashboard: upload form, variable controls, plot iframe. |
| `linePlot.html`  | Displays multi‑variable line graph for selected coordinate. |

---

## 4. Runtime Directories (Git‑ignored)

| Folder | Description |
|--------|-------------|
| **`uploads/`** | Holds user‑uploaded NetCDF files for the current session. |
| **`fldData/`** | Optional cache of processed NumPy arrays to speed reloads. |

Both paths are excluded in the root `.gitignore`.

---

## 5. Adding New Functionality

1. Create a new helper module (e.g., `htmlPlotVolume.py`).
2. Import it in `app.py` and call it from the appropriate route.
3. Add any new HTML pages to `templates/` and assets to `static/`.
4. Update this README so future contributors know where it fits.

---

## 6. Developer Tips

* **Hot reload** – run `set FLASK_ENV=development` on Windows (or `export FLASK_ENV=development` on Unix) before `python app.py` to enable auto‑reload.
* **Large data** – keep test `.nc` files in `uploads/` (ignored) so they don’t bloat the repo.
* **PyVista debug** – set `pv.OFF_SCREEN = True` if the server has no display.

---

*Last updated: 2025‑04‑29*

