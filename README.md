# NetCDF Visualizer

NetCDF Visualizer is a web‑based tool that lets you upload NetCDF (`.nc`) files and interactively explore them as **3‑D contour plots** with **magnetic‑field‑line tracing**. You can also create **2‑D cross‑sections** and **time‑series line plots** for any variable.

## Features
- Upload NetCDF files and render interactive **3‑D isosurfaces**
- Trace field lines by **clicking** on the plot or entering coordinates
- Generate **2‑D cross‑sections** of the data cube
- Produce **time‑series line plots** at selected points
- Export plots as standalone **HTML**
- Built with **Flask · Plotly · PyVista** for rich interactivity

---

## Installation

### Prerequisites
*Python 3.8+*

### 1 · Create & activate a virtual environment

<details><summary>Windows (cmd / PowerShell)</summary>

```sh
python -m venv plotGen
plotGen\Scripts\activate
```
</details>

<details><summary>macOS / Linux</summary>

```sh
python -m venv plotGen
source plotGen/bin/activate
```
</details>

### 2 · Install dependencies

```sh
pip install flask numpy scipy matplotlib plotly netCDF4 pyvista psutil vtk
```

---

## Running the app

```sh
cd flaskApp
python app.py
```
Then visit **http://127.0.0.1:5000** in your browser.

---

## Quick start workflow
1. Upload a `.nc` file  
2. Choose a variable and plot options  
3. Click **Plot** → interactive 3‑D contour displays  
4. Click anywhere (or enter X Y Z) to add a **field line**  
5. Manage / delete lines from the sidebar  
6. Add **2‑D cross‑sections** or **line graphs** as needed  
7. Download the generated HTML/PNG for sharing

---

## Project tree

```
NetCDF_Visualizer/
├── flaskApp/
│   ├── app.py                    # Flask entry point
│   ├── htmlPlotFieldLines.py     # 3‑D plots + field‑line tracing
│   ├── htmlPlotCrossSection.py   # 2‑D cross‑sections
│   ├── htmlPlotGenerator3D.py    # Isosurface helper
│   ├── plotLineGraph.py          # Time‑series graphs
│   ├── templates/                # Jinja2 templates
│   ├── static/                   # Generated HTML/PNG assets
│   ├── uploads/                  # Uploaded .nc files   (ignored by Git)
│   └── fldData/                  # Cached field data    (ignored by Git)
│
├── plotGen/                      # Python virtual‑env    (ignored by Git)
├── ncFileSize.py                 # Utility: quick dataset probe
├── database_structure.md         # Design notes
├── project_requirements.txt      # Requirement pins
├── .gitignore                    # Git exclusions
└── README.md                     # You are here
```

> `uploads/` and `fldData/` are excluded via **.gitignore** so large user data never enters version control.

---

## Contributing
Pull requests are welcome!  
Open an issue for bugs or feature ideas.

---

## License
**MIT** – do what you want, just keep the notice.

---

## Credits
Developed at **Auburn University** using Python, Flask, Plotly, PyVista, and the NetCDF4 ecosystem.
