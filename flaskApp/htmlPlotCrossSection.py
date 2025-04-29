import plotly.graph_objects as go
import numpy as np

def add_2d_cross_section(fig, data, x_coords, y_coords, z_coords, cross_section_axis, cross_section_value, color_scale=None, opacity=1.0):
    """
    Adds a 2D cross-section to the given 3D plot figure.
    """
    if cross_section_axis == 'x':
        slice_data = data[cross_section_value, :, :]
        x = x_coords[cross_section_value]
        y, z = np.meshgrid(y_coords, z_coords, indexing='ij')
        fig.add_trace(go.Surface(
            z=z,
            x=np.full_like(slice_data, x),
            y=y,
            surfacecolor=slice_data,
            opacity=opacity,
            colorscale='Viridis',
            cmin=color_scale[0],
            cmax=color_scale[1],
            showscale=False
        ))
    elif cross_section_axis == 'y':
        slice_data = data[:, cross_section_value, :]
        y = y_coords[cross_section_value]
        x, z = np.meshgrid(x_coords, z_coords, indexing='ij')
        fig.add_trace(go.Surface(
            z=z,
            x=x,
            y=np.full_like(slice_data, y),
            surfacecolor=slice_data,
            opacity=opacity,
            colorscale='Viridis',
            cmin=color_scale[0],
            cmax=color_scale[1],
            showscale=False
        ))
    elif cross_section_axis == 'z':
        slice_data = data[:, :, cross_section_value]
        z = z_coords[cross_section_value]
        x, y = np.meshgrid(x_coords, y_coords, indexing='ij')
        fig.add_trace(go.Surface(
            z=np.full_like(slice_data, z),
            x=x,
            y=y,
            surfacecolor=slice_data,
            opacity=opacity,
            colorscale='Viridis',
            cmin=color_scale[0],
            cmax=color_scale[1],
            showscale=False
        ))

def plot_multiple_2d_cross_sections_3d(data, x_coords, y_coords, z_coords, cross_sections, cross_section_opacities, color_scale=None, output_html='cross_section_3d.html'):
    """
    Creates a 3D plot with multiple 2D cross-sections from the 3D data.
    """
    fig = go.Figure()

    # Add multiple 2D cross-sections based on user input
    for i, (axis, value) in enumerate(cross_sections):
        opacity = cross_section_opacities[i]  # Use the corresponding opacity for each cross-section
        add_2d_cross_section(fig, data, x_coords, y_coords, z_coords, axis, value, color_scale=color_scale, opacity=opacity)

    # Set consistent axis ranges
    fig.update_layout(
        title='2D Cross Section Plot',
        scene=dict(
            xaxis=dict(title='X (Re)', range=[x_coords[0], x_coords[-1]]),
            yaxis=dict(title='Y (Re)', range=[y_coords[0], y_coords[-1]]),
            zaxis=dict(title='Z (Re)', range=[z_coords[0], z_coords[-1]])
        ),
        autosize=True,
        width=800,
        height=600
    )

    # Save the plot as an HTML file
    fig.write_html(output_html)
    print(f"2D cross-section plot saved as {output_html}")
