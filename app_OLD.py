from flask import Flask, render_template, request, jsonify, url_for, Response
import os
from werkzeug.utils import secure_filename
from htmlPlotFieldLines import (
    read_nc_variables,
    downsample_data_dict,
    create_3d_contour_plot
)
from htmlPlotCrossSection import plot_multiple_2d_cross_sections_3d

from scipy.interpolate import RegularGridInterpolator
import numpy as np
import json
import plotly
import plotly.io as pio

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

global_data = {
    'file_path': None,
    'variable_name': None,
    'data_vars': None,
    'downsampled_vars': None,
    'color_scale_range': None,
    'x_range': None,
    'y_range': None,
    'z_range': None,
    'opacity': None,
    'interpolators': None,
    'x_coords': None,
    'y_coords': None,
    'z_coords': None,
    'field_lines': []  # seeds
}

def scale_user_input(input_range, factor=2):
    return (int(input_range[0] / factor), int(input_range[1] / factor))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'ncFile' not in request.files:
        return 'No file uploaded', 400

    file = request.files['ncFile']
    if file.filename == '':
        return 'No selected file', 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    variable_name = request.form['variable']
    try:
        min_scale = float(request.form['minScale'])
        max_scale = float(request.form['maxScale'])
        opacity = float(request.form['opacity']) / 100
        x_min = int(request.form['inputField1'])
        x_max = int(request.form['inputField2'])
        y_min = int(request.form['inputField3'])
        y_max = int(request.form['inputField4'])
        z_min = int(request.form['inputField5'])
        z_max = int(request.form['inputField6'])
    except (ValueError, KeyError) as e:
        return f'Invalid form input: {e}', 400

    color_scale_range = (min_scale, max_scale)
    user_x_range = (x_min, x_max)
    user_y_range = (y_min, y_max)
    user_z_range = (z_min, z_max)

    variables_to_read = ['Bx', 'By', 'Bz', 'X', 'Y', 'Z', variable_name]
    try:
        data_vars = read_nc_variables(file_path, variables_to_read)
    except Exception as e:
        return f'Error reading variables: {e}', 400

    downsampled_vars = downsample_data_dict(data_vars)

    global_data.update({
        'file_path': file_path,
        'variable_name': variable_name,
        'data_vars': data_vars,
        'downsampled_vars': downsampled_vars,
        'color_scale_range': color_scale_range,
        'x_range': user_x_range,
        'y_range': user_y_range,
        'z_range': user_z_range,
        'opacity': opacity,
        'x_coords': downsampled_vars['X'],
        'y_coords': downsampled_vars['Y'],
        'z_coords': downsampled_vars['Z'],
        'field_lines': []
    })

    # Build interpolators
    try:
        global_data['interpolators'] = {
            'Bx_interp': RegularGridInterpolator(
                (downsampled_vars['X'], downsampled_vars['Y'], downsampled_vars['Z']),
                downsampled_vars['Bx'],
                bounds_error=False,
                fill_value=None
            ),
            'By_interp': RegularGridInterpolator(
                (downsampled_vars['X'], downsampled_vars['Y'], downsampled_vars['Z']),
                downsampled_vars['By'],
                bounds_error=False,
                fill_value=None
            ),
            'Bz_interp': RegularGridInterpolator(
                (downsampled_vars['X'], downsampled_vars['Y'], downsampled_vars['Z']),
                downsampled_vars['Bz'],
                bounds_error=False,
                fill_value=None
            )
        }
    except Exception as e:
        return f'Error creating interpolators: {e}', 500

    # Cross-sections
    cross_sections = []
    cross_section_opacities = []
    cross_section_axes = request.form.getlist('crossSectionAxis[]')
    cross_section_values = request.form.getlist('crossSectionValue[]')
    cross_section_opacity_values = request.form.getlist('crossSectionOpacity[]')

    for axis, val, cs_op in zip(cross_section_axes, cross_section_values, cross_section_opacity_values):
        try:
            cross_sections.append((axis, int(val)))
            cross_section_opacities.append(float(cs_op)/100)
        except ValueError as e:
            return f'Invalid cross-section input: {e}', 400

    output_html_cross_section = 'static/multiple_cross_section_3d.html'
    try:
        plot_multiple_2d_cross_sections_3d(
            downsampled_vars[variable_name],
            downsampled_vars['X'],
            downsampled_vars['Y'],
            downsampled_vars['Z'],
            cross_sections,
            cross_section_opacities,
            color_scale=color_scale_range,
            output_html=output_html_cross_section
        )
    except Exception as e:
        return f'Error generating cross-section plot: {e}', 500

    return jsonify({
        'plot_data_url': url_for('get_plot_data'),
        'plot2_url': url_for('static', filename='multiple_cross_section_3d.html')
    })

@app.route('/get_plot_data')
def get_plot_data():
    try:
        plot_data = generate_plot_with_field_lines()
    except Exception as e:
        return jsonify({'error': f'Error generating plot: {e}'}), 500

    return Response(
        json.dumps(plot_data, cls=plotly.utils.PlotlyJSONEncoder),
        mimetype='application/json'
    )

def generate_plot_with_field_lines():
    var_name = global_data['variable_name']
    color_scale_range = global_data['color_scale_range']
    opacity = global_data['opacity']

    x_range = scale_user_input(global_data['x_range'], factor=2)
    y_range = scale_user_input(global_data['y_range'], factor=2)
    z_range = scale_user_input(global_data['z_range'], factor=2)

    Bx_i = global_data['interpolators']['Bx_interp']
    By_i = global_data['interpolators']['By_interp']
    Bz_i = global_data['interpolators']['Bz_interp']

    # This calls create_3d_contour_plot from htmlPlotFieldLines
    plot_data = create_3d_contour_plot(
        data=global_data['downsampled_vars'][var_name],
        variable_name=var_name,
        x_coords=global_data['x_coords'],
        y_coords=global_data['y_coords'],
        z_coords=global_data['z_coords'],
        output_html=None,
        color_scale=color_scale_range,
        x_range=x_range,
        y_range=y_range,
        z_range=z_range,
        opacity=opacity,
        field_lines=global_data['field_lines'],
        Bx_interp=Bx_i,
        By_interp=By_i,
        Bz_interp=Bz_i
    )
    return plot_data

@app.route('/field-line', methods=['POST'])
def field_line():
    data = request.get_json()
    try:
        clicked_x = float(data['x'])
        clicked_y = float(data['y'])
        clicked_z = float(data['z'])
    except (KeyError, ValueError):
        return jsonify({'error': 'Invalid input coords'}), 400

    print(f"Clicked coords: x={clicked_x}, y={clicked_y}, z={clicked_z}")

    x_coords = global_data['x_coords']
    y_coords = global_data['y_coords']
    z_coords = global_data['z_coords']

    x_min, x_max = x_coords[0], x_coords[-1]
    y_min, y_max = y_coords[0], y_coords[-1]
    z_min, z_max = z_coords[0], z_coords[-1]

    if not(x_min <= clicked_x <= x_max and y_min <= clicked_y <= y_max and z_min <= clicked_z <= z_max):
        return jsonify({'error': 'Clicked seed out of domain'}), 400

    # Check B field
    Bx_val = global_data['interpolators']['Bx_interp']((clicked_x, clicked_y, clicked_z))
    By_val = global_data['interpolators']['By_interp']((clicked_x, clicked_y, clicked_z))
    Bz_val = global_data['interpolators']['Bz_interp']((clicked_x, clicked_y, clicked_z))
    B_mag0 = np.sqrt(Bx_val**2 + By_val**2 + Bz_val**2)
    if B_mag0 == 0 or np.isnan(B_mag0):
        return jsonify({'error': 'Mag field zero/NaN at seed'}), 400

    # Add seed
    global_data['field_lines'].append([clicked_x, clicked_y, clicked_z])
    print("Seeds: ", global_data['field_lines'])

    # Generate
    try:
        plot_data = generate_plot_with_field_lines()
    except Exception as e:
        print(f"Error generating line plot: {e}")
        return jsonify({'error': f'Error generating line plot: {e}'}), 500

    # Build field-line list
    fl_list = []
    for idx, pt in enumerate(global_data['field_lines']):
        fl_list.append({
            'index': idx,
            'coordinates': {'x': pt[0], 'y': pt[1], 'z': pt[2]}
        })

    resp_data = {
        'plot_data': plot_data,
        'field_lines': fl_list
    }
    return Response(
        json.dumps(resp_data, cls=plotly.utils.PlotlyJSONEncoder),
        mimetype='application/json'
    )

@app.route('/delete-field-line', methods=['POST'])
def delete_field_line():
    data = request.get_json()
    try:
        line_index = int(data['line_index'])
    except (KeyError, ValueError):
        return jsonify({'error': 'Invalid index'}), 400

    lines = global_data['field_lines']
    if 0 <= line_index < len(lines):
        del lines[line_index]
    else:
        return jsonify({'error': 'Index out of range'}), 400

    try:
        plot_data = generate_plot_with_field_lines()
    except Exception as e:
        return jsonify({'error': f'Error after delete: {e}'}), 500

    fl_list = []
    for idx, pt in enumerate(global_data['field_lines']):
        fl_list.append({
            'index': idx,
            'coordinates': {'x': pt[0], 'y': pt[1], 'z': pt[2]}
        })

    resp_data = {
        'plot_data': plot_data,
        'field_lines': fl_list
    }
    return Response(
        json.dumps(resp_data, cls=plotly.utils.PlotlyJSONEncoder),
        mimetype='application/json'
    )

if __name__ == "__main__":
    app.run(debug=True)


