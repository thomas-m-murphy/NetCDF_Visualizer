# FlaskApp - NetCDF Visualization Tool

## Overview
This project is a **Flask-based web application** that allows users to **visualize NetCDF (.nc) files** with 3D plots, field lines, and cross-sections. It provides an interactive interface for selecting variables, adjusting rendering settings, and analyzing scientific data.

## Features
- **Upload and Process NetCDF Files**
- **3D Data Visualization**
- **Field Line Tracing**
- **Cross-Sectional Plotting**
- **Real-Time Rendering Options**
- **GPU-Accelerated Rendering (PyVista + VTK)**

---

## Installation and Setup
### 1️⃣ Clone the Repository
```sh
# Replace with your GitHub repo link
git clone https://github.com/your-username/flaskapp.git
cd flaskapp
```

### 2️⃣ Install Dependencies

#### **Windows (Recommended: Anaconda)**
```powershell
# Create and activate a virtual environment
conda create --name plotGen python=3.12
conda activate plotGen

# Install required dependencies
pip install -r project_requirements.txt
```

#### **macOS**
```sh
# Create and activate a virtual environment
python3 -m venv plotGen
source plotGen/bin/activate

# Install required dependencies
pip install -r project_requirements.txt
```

### 3️⃣ Run the Flask Application
```sh
python app.py
```
By default, the application will start on `http://127.0.0.1:5000/`.

---

## GPU Acceleration (Optional)
To **enable GPU-accelerated rendering**, modify `htmlPlotFieldLines.py` and add:
```python
import os
os.environ["VTK_OPENGL_BACKEND"] = "2"  # Force OpenGL 2 backend
```

To verify GPU usage, run:
```sh
python testGPU.py
```

If **GPU acceleration is OFF**, try updating your **graphics drivers** and ensuring you have an **NVIDIA GPU with OpenGL support**.

---

## File Descriptions
### **Main Files**
- **`app.py`** - Main Flask application, handles routing, file uploads, and rendering requests.
- **`htmlPlotFieldLines.py`** - Generates and visualizes field lines using PyVista.
- **`htmlPlotGenerator3D.py`** - Processes 3D NetCDF data and generates plots.
- **`htmlPlotCrossSection.py`** - Generates 2D cross-sections of NetCDF data.
- **`plotLineGraph.py`** - Creates line graphs from extracted data points.
- **`psipyTest.py`** - Test script for PsiPy and field line calculations.

### **Supporting Files**
- **`static/`** - Contains static assets (CSS, JavaScript, images).
- **`templates/`** - Contains HTML templates for Flask's front-end.
- **`uploads/`** - Stores uploaded NetCDF files temporarily.
- **`plotGen/`** - Directory for processed plot files.
- **`__pycache__/`** - Auto-generated Python cache files (safe to ignore).

### **Backup Files**
- **`app_OLD.py`** - Previous version of `app.py` (legacy code).
- **`htmlPlotFieldLines_OLD.py`** - Older version of `htmlPlotFieldLines.py`.

---

## Troubleshooting
### **Common Errors & Fixes**
#### `ModuleNotFoundError: No module named 'netCDF4'`
Run:
```sh
pip install netCDF4
```

#### `TypeError: Configuration type must be '_DepthPeelingConfig'`
Modify `htmlPlotFieldLines.py`:
```python
pv.global_theme.depth_peeling.enabled = True
pv.global_theme.depth_peeling.number_of_peels = 4
pv.global_theme.depth_peeling.occlusion_ratio = 0.0
```

#### GPU Not Used in Rendering
- Ensure you installed **NVIDIA GPU drivers**.
- Run `nvidia-smi` (Windows) or `system_profiler SPDisplaysDataType` (macOS) to check GPU availability.
- Modify environment variables as described above.

---

## Future Maintenance
This project will soon be **handed over to a new maintainer**. Future updates and improvements should be documented within this repository.

If you encounter issues, **create a GitHub issue** or refer to the documentation inside each script.

---

## License
This project is licensed under the **MIT License**.

