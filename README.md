
# NetCDF Visualizer

NetCDF Visualizer is a web-based tool that allows users to upload NetCDF (`.nc`) files and visualize **3D contour plots** with **field line tracing functionality**. Users can also generate **2D cross-sections** and **time-series line plots** of selected variables.

## Features
- ✔ Upload and visualize NetCDF files as interactive **3D contour plots**  
- ✔ Click on the plot **or** manually enter coordinates to trace **field lines**  
- ✔ Generate **2D cross-sections** of the dataset  
- ✔ Create **line plots** of time-series data  
- ✔ Export plots as **HTML** for easy sharing  
- ✔ Built with **Flask and Plotly** for interactivity  

---

## Installation

### Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### Setting Up the Virtual Environment
Run the following commands in your terminal:

#### Windows:
```sh
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux:
```sh
python -m venv venv
source venv/bin/activate
```

### Installing Dependencies
After activating the virtual environment, install all required dependencies:

```sh
pip install flask numpy scipy matplotlib plotly netCDF4 pyvista psutil vtk
```

### Running the Application
Once all dependencies are installed, start the Flask application by running:

```sh
python app.py
```

Then, open your browser and navigate to:

```
http://127.0.0.1:5000
```

## Usage Instructions
1️⃣ Upload a NetCDF (`.nc`) file.  
2️⃣ Select the variable to visualize.  
3️⃣ Adjust the color scale and opacity.  
4️⃣ Click **Plot** to generate the **3D contour plot**.  
5️⃣ Click on the plot or manually enter X, Y, Z coordinates to trace **field lines**.  
6️⃣ View and manage active **field lines**.  
7️⃣ Optionally, generate and view **2D cross-sections**.  
8️⃣ Export and share visualizations as **HTML**.  

## File Structure
```
NetCDF_Visualizer/
│── static/               # Static files (CSS, JS, images, plots)
│── templates/            # HTML templates
│── uploads/              # Uploaded .nc files (ignored in Git)
│── app.py                # Main Flask application
│── htmlPlotFieldLines.py # Field line visualization logic
│── htmlPlotCrossSection.py # 2D cross-section visualization
│── htmlPlotGenerator3D.py  # 3D plot generation
│── plotLineGraph.py      # Line plot visualization
│── README.md             # Documentation
│── venv/                 # Virtual environment (ignored in Git)
```

## Contributing
We welcome contributions! If you find a bug, have a feature request, or want to improve the code, feel free to open an issue or submit a pull request. 🚀

## License
This project is open-source under the **MIT License**.

## Credits
This project was developed as part of a research effort at **Auburn University**, incorporating **Python, Flask, Plotly, and PyVista** to create an interactive visualization tool.

