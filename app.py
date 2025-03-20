
# from flask import Flask, render_template, request, jsonify, url_for
# import os
# from werkzeug.utils import secure_filename

# from htmlPlotFieldLines import (
#     read_nc_variables,
#     downsample_data_dict,
#     create_3d_contour_plot
# )
# from htmlPlotCrossSection import plot_multiple_2d_cross_sections_3d
# from plotLineGraph import extract_data, create_multi_plot

# import numpy as np
# import json
# import matplotlib.pyplot as plt

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads'
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# # ---------------------------------------
# # Global Data
# # ---------------------------------------
# global_data = {
#     'file_path': None,
#     'variable_name': None,
#     'data_vars': None,
#     'downsampled_vars': None,
#     'color_scale_range': None,
#     'x_range': None,
#     'y_range': None,
#     'z_range': None,
#     'opacity': None,
#     'x_coords': None,
#     'y_coords': None,
#     'z_coords': None,
#     'field_lines': [],  # list of [x,y,z]
#     'cached_lines': {}  # maps (x,y,z) -> list of line segments
# }


# def scale_user_input(input_range, factor=2):
#     """Convert user X range => downsampled index range."""
#     return (int(input_range[0]/factor), int(input_range[1]/factor))

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/data-visualization')
# def data_visualization():
#     return render_template('linePlot.html')

# # ---------------------------------------
# # 1) Upload => read => 2D cross sec => 3D HTML
# # ---------------------------------------
# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'ncFile' not in request.files:
#         return 'No file uploaded', 400

#     file = request.files['ncFile']
#     if file.filename == '':
#         return 'No selected file', 400

#     filename = secure_filename(file.filename)
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     file.save(file_path)

#     var = request.form['variable']
#     try:
#         min_scale = float(request.form['minScale'])
#         max_scale = float(request.form['maxScale'])
#         opacity = float(request.form['opacity']) / 100
#         x_min = int(request.form['inputField1'])
#         x_max = int(request.form['inputField2'])
#         y_min = int(request.form['inputField3'])
#         y_max = int(request.form['inputField4'])
#         z_min = int(request.form['inputField5'])
#         z_max = int(request.form['inputField6'])
#     except (ValueError, KeyError) as e:
#         return f'Invalid form input: {e}', 400

#     color_scale_range = (min_scale, max_scale)
#     user_x_range = (x_min, x_max)
#     user_y_range = (y_min, y_max)
#     user_z_range = (z_min, z_max)

#     vars_to_read = ['Bx','By','Bz','X','Y','Z', var]
#     try:
#         data_vars = read_nc_variables(file_path, vars_to_read)
#     except Exception as e:
#         return f'Error reading variables: {e}', 400

#     downsampled = downsample_data_dict(data_vars)

#     # Reset global data
#     global_data.update({
#         'file_path': file_path,
#         'variable_name': var,
#         'data_vars': data_vars,
#         'downsampled_vars': downsampled,
#         'color_scale_range': color_scale_range,
#         'x_range': user_x_range,
#         'y_range': user_y_range,
#         'z_range': user_z_range,
#         'opacity': opacity,
#         'x_coords': downsampled['X'],
#         'y_coords': downsampled['Y'],
#         'z_coords': downsampled['Z'],
#         'field_lines': [],
#         'cached_lines': {}
#     })

#     # 2D cross-sections
#     cross_sections = []
#     cross_section_opacities = []
#     cs_axes = request.form.getlist('crossSectionAxis[]')
#     cs_vals = request.form.getlist('crossSectionValue[]')
#     cs_ops = request.form.getlist('crossSectionOpacity[]')

#     for axis, val, opac in zip(cs_axes, cs_vals, cs_ops):
#         try:
#             cross_sections.append((axis, int(val)))
#             cross_section_opacities.append(float(opac)/100)
#         except ValueError as e:
#             return f'Invalid cross-section input: {e}', 400

#     cross_html = 'static/multiple_cross_section_3d.html'
#     try:
#         plot_multiple_2d_cross_sections_3d(
#             downsampled[var],
#             downsampled['X'],
#             downsampled['Y'],
#             downsampled['Z'],
#             cross_sections,
#             cross_section_opacities,
#             color_scale=color_scale_range,
#             output_html=cross_html
#         )
#     except Exception as e:
#         return f'Error generating cross-section plot: {e}', 500

#     # 3D => no seeds yet
#     three_d_html = "static/3d_contour_plot.html"
#     create_3d_contour_plot(
#         data=downsampled[var],
#         variable_name=var,
#         x_coords=downsampled['X'],
#         y_coords=downsampled['Y'],
#         z_coords=downsampled['Z'],
#         output_html=three_d_html,
#         color_scale=color_scale_range,
#         x_range=scale_user_input(user_x_range),
#         y_range=scale_user_input(user_y_range),
#         z_range=scale_user_input(user_z_range),
#         opacity=opacity,
#         field_lines=[],
#         Bx_array=downsampled['Bx'],
#         By_array=downsampled['By'],
#         Bz_array=downsampled['Bz']
#     )

#     return jsonify({
#         'plot_html_url':  url_for('static', filename='3d_contour_plot.html'),
#         'plot2_url':      url_for('static', filename='multiple_cross_section_3d.html')
#     })

# # ---------------------------------------
# # 2) Add a field line => regenerate 3D
# # ---------------------------------------
# @app.route('/field-line', methods=['POST'])
# def field_line():
#     """
#     Accepts JSON: { x: <float>, y: <float>, z: <float> }
#     Adds a new seed => regenerates 3d_contour_plot.html with all seeds.
#     Returns JSON => { 'plot_html': <URL to 3D HTML>, 'field_lines': [list] }
#     """
#     data = request.get_json()
#     if not data:
#         return jsonify({'error': 'No JSON data'}), 400

#     try:
#         sx = float(data['x'])
#         sy = float(data['y'])
#         sz = float(data['z'])
#     except (KeyError, ValueError):
#         return jsonify({'error': 'Invalid coords'}), 400

#     # Basic checks
#     x_coords = global_data['x_coords']
#     y_coords = global_data['y_coords']
#     z_coords = global_data['z_coords']
#     if x_coords is None or y_coords is None or z_coords is None:
#         return jsonify({'error': 'Global data missing. Re-upload .nc file.'}), 400

#     # Domain check
#     if not(x_coords[0] <= sx <= x_coords[-1] and
#            y_coords[0] <= sy <= y_coords[-1] and
#            z_coords[0] <= sz <= z_coords[-1]):
#         return jsonify({'error':'Seed out of domain'}), 400

#     # B not zero
#     ix = (np.abs(x_coords - sx)).argmin()
#     iy = (np.abs(y_coords - sy)).argmin()
#     iz = (np.abs(z_coords - sz)).argmin()
#     Bx_val = global_data['downsampled_vars']['Bx'][ix, iy, iz]
#     By_val = global_data['downsampled_vars']['By'][ix, iy, iz]
#     Bz_val = global_data['downsampled_vars']['Bz'][ix, iy, iz]
#     B_mag0 = np.sqrt(Bx_val**2 + By_val**2 + Bz_val**2)
#     if B_mag0 == 0 or np.isnan(B_mag0):
#         return jsonify({'error': 'Mag field zero/NaN at seed'}), 400

#     new_seed = (sx, sy, sz)
#     if new_seed not in global_data['cached_lines']:
#         global_data['cached_lines'][new_seed] = []  # We'll generate below

#     # Add to global_data['field_lines'] if not present
#     if list(new_seed) not in global_data['field_lines']:
#         global_data['field_lines'].append([sx, sy, sz])

#     # Rebuild the 3D HTML with all seeds
#     _rebuild_3d_html()

#     # Return current lines
#     fl_list = []
#     for idx, arr in enumerate(global_data['field_lines']):
#         fl_list.append({
#             'index': idx,
#             'coordinates': {
#                 'x': arr[0],
#                 'y': arr[1],
#                 'z': arr[2]
#             }
#         })

#     return jsonify({
#         'plot_html': url_for('static', filename='3d_contour_plot.html'),
#         'field_lines': fl_list
#     })


# # ---------------------------------------
# # 3) Delete a field line => regen 3D
# # ---------------------------------------
# @app.route('/delete-field-line', methods=['POST'])
# def delete_field_line():
#     data = request.get_json()
#     if not data:
#         return jsonify({'error': 'No JSON data'}), 400

#     try:
#         idx = int(data['line_index'])
#     except (KeyError, ValueError):
#         return jsonify({'error': 'Invalid line index'}), 400

#     lines = global_data['field_lines']
#     if 0 <= idx < len(lines):
#         seed_tuple = tuple(lines[idx])
#         # remove from cached_lines if present
#         if seed_tuple in global_data['cached_lines']:
#             del global_data['cached_lines'][seed_tuple]
#         del lines[idx]
#     else:
#         return jsonify({'error': 'Index out of range'}), 400

#     # Rebuild the 3D HTML again
#     _rebuild_3d_html()

#     # Return new list
#     fl_list = []
#     for i, arr in enumerate(global_data['field_lines']):
#         fl_list.append({
#             'index': i,
#             'coordinates': {
#                 'x': arr[0],
#                 'y': arr[1],
#                 'z': arr[2]
#             }
#         })

#     return jsonify({
#         'plot_html': url_for('static', filename='3d_contour_plot.html'),
#         'field_lines': fl_list
#     })


# # ---------------------------------------
# # Utility to rebuild "3d_contour_plot.html" with seeds
# # ---------------------------------------
# def _rebuild_3d_html():
#     gd = global_data
#     var = gd['variable_name']
#     color_scale_range = gd['color_scale_range']
#     opacity = gd['opacity']

#     # build seeds as tuples => we pass to create_3d_contour_plot
#     seeds = []
#     for arr in gd['field_lines']:
#         seeds.append( (arr[0], arr[1], arr[2]) )

#     # If user gave 201 => factor=2 => index up to 100
#     x_range = scale_user_input(gd['x_range'])
#     y_range = scale_user_input(gd['y_range'])
#     z_range = scale_user_input(gd['z_range'])

#     html_path = "static/3d_contour_plot.html"

#     # We'll generate new line segments each time
#     create_3d_contour_plot(
#         data=gd['downsampled_vars'][var],
#         variable_name=var,
#         x_coords=gd['x_coords'],
#         y_coords=gd['y_coords'],
#         z_coords=gd['z_coords'],
#         output_html=html_path,
#         color_scale=color_scale_range,
#         x_range=x_range,
#         y_range=y_range,
#         z_range=z_range,
#         opacity=opacity,
#         field_lines=seeds,
#         Bx_array=gd['downsampled_vars']['Bx'],
#         By_array=gd['downsampled_vars']['By'],
#         Bz_array=gd['downsampled_vars']['Bz']
#     )


# # ---------------------------------------
# # 4) /generate-line-plot => linePlot
# # ---------------------------------------
# @app.route('/generate-line-plot', methods=['POST'])
# def generate_line_plot():
#     data = request.get_json()
#     if not data:
#         return jsonify({'error':'No JSON data received'}), 400

#     folder_path = data.get('folderPath')
#     selected_vars = data.get('selectedVariables')
#     coord = data.get('coordinate')

#     if not folder_path or not selected_vars or not coord:
#         return jsonify({'error':'Missing input parameters'}), 400

#     try:
#         x, y, z = coord
#         data_dict = extract_data(folder_path, selected_vars, x, y, z)
#         if not any(data_dict.values()):
#             return jsonify({'error':'No data points extracted.'}), 400

#         create_multi_plot(data_dict, selected_vars, (x,y,z))
#         return jsonify({'plot_url': url_for('static', filename='multi_variable_line_graph.png')})
#     except Exception as e:
#         return jsonify({'error':f'Error generating line plot: {e}'}), 500


# if __name__=="__main__":
#     app.run(debug=True)




















from flask import Flask, render_template, request, jsonify, url_for
import os
from werkzeug.utils import secure_filename

from htmlPlotFieldLines import (
    read_nc_variables,
    downsample_data_dict,
    create_3d_contour_plot
)
from htmlPlotCrossSection import plot_multiple_2d_cross_sections_3d
from plotLineGraph import extract_data, create_multi_plot

import numpy as np
import json
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global data
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
    'x_coords': None,
    'y_coords': None,
    'z_coords': None,
    'field_lines': [],  # list of [x,y,z]
    'cached_lines': {}  # maps (x,y,z) -> line segments
}

def scale_user_input(rng, factor=2):
    return (int(rng[0]/factor), int(rng[1]/factor))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data-visualization')
def data_visualization():
    return render_template('linePlot.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'ncFile' not in request.files:
        return 'No file uploaded', 400

    f = request.files['ncFile']
    if f.filename == '':
        return 'No selected file', 400

    filename = secure_filename(f.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(path)

    var = request.form['variable']
    try:
        min_scale = float(request.form['minScale'])
        max_scale = float(request.form['maxScale'])
        opac = float(request.form['opacity']) / 100
        x_min = int(request.form['inputField1'])
        x_max = int(request.form['inputField2'])
        y_min = int(request.form['inputField3'])
        y_max = int(request.form['inputField4'])
        z_min = int(request.form['inputField5'])
        z_max = int(request.form['inputField6'])
    except (ValueError, KeyError) as e:
        return f'Invalid form input: {e}', 400

    c_range = (min_scale, max_scale)
    u_x_range = (x_min, x_max)
    u_y_range = (y_min, y_max)
    u_z_range = (z_min, z_max)

    read_vars = ['Bx','By','Bz','X','Y','Z', var]
    try:
        data_vars = read_nc_variables(path, read_vars)
    except Exception as e:
        return f'Error reading variables: {e}', 400

    dvars = downsample_data_dict(data_vars)

    global_data.update({
        'file_path': path,
        'variable_name': var,
        'data_vars': data_vars,
        'downsampled_vars': dvars,
        'color_scale_range': c_range,
        'x_range': u_x_range,
        'y_range': u_y_range,
        'z_range': u_z_range,
        'opacity': opac,
        'x_coords': dvars['X'],
        'y_coords': dvars['Y'],
        'z_coords': dvars['Z'],
        'field_lines': [],
        'cached_lines': {}
    })

    # cross-sections
    cross_sections = []
    cross_section_opacities = []
    cs_axes = request.form.getlist('crossSectionAxis[]')
    cs_vals = request.form.getlist('crossSectionValue[]')
    cs_ops = request.form.getlist('crossSectionOpacity[]')
    for axis, val, op_ in zip(cs_axes, cs_vals, cs_ops):
        try:
            cross_sections.append((axis, int(val)))
            cross_section_opacities.append(float(op_)/100)
        except ValueError as e:
            return f'Invalid cross-section input: {e}', 400

    cross_html = "static/multiple_cross_section_3d.html"
    try:
        plot_multiple_2d_cross_sections_3d(
            dvars[var],
            dvars['X'],
            dvars['Y'],
            dvars['Z'],
            cross_sections,
            cross_section_opacities,
            color_scale=c_range,
            output_html=cross_html
        )
    except Exception as e:
        return f'Error generating cross-section plot: {e}', 500

    # 3D => no seeds yet
    three_d_html = "static/3d_contour_plot.html"
    create_3d_contour_plot(
        data=dvars[var],
        variable_name=var,
        x_coords=dvars['X'],
        y_coords=dvars['Y'],
        z_coords=dvars['Z'],
        output_html=three_d_html,
        color_scale=c_range,
        x_range=scale_user_input(u_x_range),
        y_range=scale_user_input(u_y_range),
        z_range=scale_user_input(u_z_range),
        opacity=opac,
        field_lines=[],  # none yet
        Bx_array=dvars['Bx'],
        By_array=dvars['By'],
        Bz_array=dvars['Bz']
    )

    return jsonify({
        'plot_html_url': url_for('static', filename='3d_contour_plot.html'),
        'plot2_url':     url_for('static', filename='multiple_cross_section_3d.html')
    })


# -- Add a field line via manual or clicked coords => re-generate
@app.route('/field-line', methods=['POST'])
def field_line():
    data = request.get_json()
    if not data:
        return jsonify({'error':'No JSON data'}), 400

    try:
        sx = float(data['x'])
        sy = float(data['y'])
        sz = float(data['z'])
    except (KeyError, ValueError):
        return jsonify({'error':'Invalid coords'}), 400

    xcs = global_data['x_coords']
    ycs = global_data['y_coords']
    zcs = global_data['z_coords']
    if xcs is None or ycs is None or zcs is None:
        return jsonify({'error':'Global data missing'}), 400

    # Domain check
    if not(xcs[0]<=sx<=xcs[-1] and ycs[0]<=sy<=ycs[-1] and zcs[0]<=sz<=zcs[-1]):
        return jsonify({'error':'Seed out of domain'}), 400

    # B not zero
    ix = (np.abs(xcs - sx)).argmin()
    iy = (np.abs(ycs - sy)).argmin()
    iz = (np.abs(zcs - sz)).argmin()
    Bx_val = global_data['downsampled_vars']['Bx'][ix, iy, iz]
    By_val = global_data['downsampled_vars']['By'][ix, iy, iz]
    Bz_val = global_data['downsampled_vars']['Bz'][ix, iy, iz]
    B_mag = np.sqrt(Bx_val**2 + By_val**2 + Bz_val**2)
    if B_mag==0 or np.isnan(B_mag):
        return jsonify({'error':'Mag field zero/NaN'}), 400

    new_seed = (sx, sy, sz)
    if list(new_seed) not in global_data['field_lines']:
        global_data['field_lines'].append([sx, sy, sz])

    # rebuild 3d with seeds
    _rebuild_3d_html()

    # Return lines
    fl_list = []
    for i, arr in enumerate(global_data['field_lines']):
        fl_list.append({
            'index': i,
            'coordinates': {
                'x':arr[0], 'y':arr[1], 'z':arr[2]
            }
        })
    return jsonify({
        'plot_html': url_for('static', filename='3d_contour_plot.html'),
        'field_lines': fl_list
    })


@app.route('/delete-field-line', methods=['POST'])
def delete_field_line():
    data = request.get_json()
    if not data:
        return jsonify({'error':'No JSON data'}), 400

    try:
        idx = int(data['line_index'])
    except (KeyError, ValueError):
        return jsonify({'error':'Invalid line index'}), 400

    lines = global_data['field_lines']
    if 0<=idx<len(lines):
        # remove from cached_lines if needed
        seed_tuple = tuple(lines[idx])
        if seed_tuple in global_data['cached_lines']:
            del global_data['cached_lines'][seed_tuple]
        del lines[idx]
    else:
        return jsonify({'error':'Index out of range'}),400

    _rebuild_3d_html()

    fl_list = []
    for i, arr in enumerate(global_data['field_lines']):
        fl_list.append({
            'index': i,
            'coordinates': {
                'x':arr[0], 'y':arr[1], 'z':arr[2]
            }
        })
    return jsonify({
        'plot_html': url_for('static', filename='3d_contour_plot.html'),
        'field_lines': fl_list
    })


def _rebuild_3d_html():
    gd = global_data
    var = gd['variable_name']
    c_range = gd['color_scale_range']
    opac = gd['opacity']

    seeds = []
    for arr in gd['field_lines']:
        seeds.append((arr[0], arr[1], arr[2]))

    x_rng = scale_user_input(gd['x_range'])
    y_rng = scale_user_input(gd['y_range'])
    z_rng = scale_user_input(gd['z_range'])

    out_html = "static/3d_contour_plot.html"
    create_3d_contour_plot(
        data=gd['downsampled_vars'][var],
        variable_name=var,
        x_coords=gd['x_coords'],
        y_coords=gd['y_coords'],
        z_coords=gd['z_coords'],
        output_html=out_html,
        color_scale=c_range,
        x_range=x_rng,
        y_range=y_rng,
        z_range=z_rng,
        opacity=opac,
        field_lines=seeds,
        Bx_array=gd['downsampled_vars']['Bx'],
        By_array=gd['downsampled_vars']['By'],
        Bz_array=gd['downsampled_vars']['Bz']
    )


@app.route('/generate-line-plot', methods=['POST'])
def generate_line_plot():
    data = request.get_json()
    if not data:
        return jsonify({'error':'No JSON data received'}),400

    folder_path = data.get('folderPath')
    selected_vars = data.get('selectedVariables')
    coord = data.get('coordinate')

    if not folder_path or not selected_vars or not coord:
        return jsonify({'error':'Missing input parameters'}),400

    try:
        x,y,z = coord
        dd = extract_data(folder_path, selected_vars, x,y,z)
        if not any(dd.values()):
            return jsonify({'error':'No data extracted'}),400

        create_multi_plot(dd, selected_vars, (x,y,z))
        return jsonify({'plot_url': url_for('static', filename='multi_variable_line_graph.png')})
    except Exception as e:
        return jsonify({'error':f'Error generating line plot: {e}'}),500


if __name__=="__main__":
    app.run(debug=True)
