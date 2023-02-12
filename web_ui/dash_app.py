from dash import dcc, html, Dash, dash_table
from dash.dependencies import Input, Output, State
from molecule_scanner import *
import os
import base64
from tempfile import mkdtemp
import plotly.graph_objects as go
import numpy as np
import dash_bio as dashbio

from dash_bio.utils import PdbParser, create_mol3d_style

# https://github.com/DouwMarx/dash_by_exe


# global variables
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
working_dir = mkdtemp()


# Create the app
app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=False,
)


app.layout = html.Div(
    [
        # xyz-file upload
        html.Div(
            [
                html.H5("Here you can configure your buried volume calculation."),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                    style={
                        "width": "35%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px",
                    },
                    # Allow multiple files to be uploaded
                    multiple=False,
                ),
            ]
        ),
        html.H5(children="Enter the basic setup parameters:"),
        html.Div(
            [
                html.P(children="Seperate IDs with comma"),
                dcc.Input(
                    id="input_sphere_center_atom_ids",
                    type="text",
                    placeholder="Sphere center atom ID",
                ),
                dcc.Input(
                    id="input_z_ax_atom_ids",
                    type="text",
                    placeholder="IDs for Z-ax definition ",
                ),
                dcc.Input(
                    id="input_xz_plane_atoms_ids",
                    type="text",
                    placeholder="IDs for xz-ax definition ",
                ),
                dcc.Input(
                    id="input_atoms_to_delete_ids",
                    type="text",
                    placeholder="IDs for deletion",
                ),
            ],
            style={"display": "inline-block"},
        ),
        # scan parameter
        html.Div(
            html.Button(id="init_button", n_clicks=0, children="Initialize molecule")
        ),
    ],
    id="layout",
)


@app.callback(
    Output("upload-data", "children"),
    Input("upload-data", "filename"),
    Input("upload-data", "contents"),
    prevent_initial_call=True,
)
def update_upload_label(filename, file_content):
    data = file_content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(working_dir, filename), "wb") as fp:
        fp.write(base64.decodebytes(data))
    return html.Div([f"Loaded {filename}.  Upload new ", html.A("File")])


def create_2d_tab():
    tab_2d = (
        html.Div(
            [
                html.Div(
                    [
                        html.H5(
                            children="Enter the desired scan parameters",
                            style={"marginTop": "20px"},
                        ),
                        # rmin
                        html.Div(
                            [
                                html.P("R-Min", style={"width": "5%"}),
                                dcc.Input(
                                    id="input_r_min",
                                    value=1.3,
                                    type="number",
                                    placeholder="Enter R-min",
                                    style={"width": "20%"},
                                    min=0,
                                    max=100,
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flex-direction": "row",
                            },
                        ),
                        # r_max
                        html.Div(
                            [
                                html.P("R-Max", style={"width": "5%"}),
                                dcc.Input(
                                    id="input_r_max",
                                    value=7,
                                    type="number",
                                    placeholder="Enter R-max",
                                    style={"width": "20%"},
                                    min=0,
                                    max=100,
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flex-direction": "row",
                            },
                        ),
                        # steps
                        html.Div(
                            [
                                html.P("Steps", style={"width": "5%"}),
                                dcc.Input(
                                    id="input_n_step",
                                    value=50,
                                    type="number",
                                    placeholder="Enter number of steps",
                                    style={"width": "20%"},
                                    min=0,
                                    max=100000,
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flex-direction": "row",
                            },
                        ),
                        # resolution
                        html.Div(
                            [
                                html.P(
                                    "mesh size",
                                    style={"width": "5%"},
                                ),
                                dcc.Input(
                                    id="input_mesh_size",
                                    value=0.1,
                                    type="number",
                                    placeholder="Enter mesh size",
                                    style={"width": "20%"},
                                    min=0,
                                    max=1,
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flex-direction": "row",
                            },
                        ),
                        # scaling
                        html.Div(
                            [
                                html.P(
                                    "radius scaling",
                                    style={"width": "5%"},
                                ),
                                dcc.Input(
                                    id="input_radii_scale",
                                    value=1,
                                    type="number",
                                    placeholder="Enter scale value",
                                    style={"width": "20%"},
                                    min=0,
                                    max=10,
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flex-direction": "row",
                            },
                        ),
                        # checklist remove h
                        html.Div(
                            dcc.Checklist(
                                ["remove H atoms"],
                                ["remove H atoms"],
                                id="input_remove_h",
                            )
                        ),
                    ]
                ),
                # start 2d calculation
                html.Div(
                    dcc.Loading(
                        id="loading_scan",
                        children=html.Div(
                            [
                                html.Button(
                                    id="scan_start_button",
                                    n_clicks=0,
                                    children="Start Scan",
                                ),
                                html.Div(id="scan_plot_div"),
                            ]
                        ),
                    ),
                ),
            ]
        ),
    )
    return tab_2d


def create_3d_tab():
    tab_3d = (
        html.Div(
            [
                html.H5(
                    children="Enter the desired cavity parameters",
                    style={"marginTop": "20px"},
                ),
                html.Div(
                    [
                        html.P("Sphere radius:", style={"width": "5%"}),
                        dcc.Input(
                            id="input_sphere_radius_3d",
                            value=2.7,
                            type="number",
                            placeholder="Enter sphere radius",
                            style={"width": "20%"},
                            min=0,
                            max=100,
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flex-direction": "row",
                    },
                ),
                # resolution 3d
                html.Div(
                    [
                        html.P("mesh size:", style={"width": "5%"}),
                        dcc.Input(
                            id="input_mesh_size_3d",
                            value=0.1,
                            type="number",
                            placeholder="Enter mesh size",
                            style={"width": "20%"},
                            min=0,
                            max=1,
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flex-direction": "row",
                    },
                ),
                # checklist remove h
                html.Div(
                    dcc.Checklist(
                        ["remove H atoms"],
                        ["remove H atoms"],
                        id="input_remove_h_3d",
                    )
                ),
                # start 3d calculation
                html.Div(
                    dcc.Loading(
                        id="loading_scan",
                        children=html.Div(
                            [
                                html.Button(
                                    id="3d_start_button",
                                    n_clicks=0,
                                    children="Calculate Cavity",
                                ),
                                html.Div(id="3d_plot_div"),
                            ]
                        ),
                    )
                ),
            ]
        ),
    )
    return tab_3d


@app.callback(
    Output("layout", "children"),
    Input("init_button", "n_clicks"),
    State("layout", "children"),
    State("upload-data", "filename"),
    State("input_sphere_center_atom_ids", "value"),
    State("input_z_ax_atom_ids", "value"),
    State("input_xz_plane_atoms_ids", "value"),
    State("input_atoms_to_delete_ids", "value"),
    prevent_initial_call=True,
)
def start_init(n_clicks, orig_layout, filename, center_id, z_id, xz_id, del_id):
    if n_clicks > 1:
        orig_layout = orig_layout[0:-1]

    if n_clicks and filename and center_id and z_id and xz_id and del_id:
        # setup molecule scanner as part of the app object
        app.molecule_scanner = msc(
            xyz_filepath=os.path.join(working_dir, filename),
            # split comma separated strings into list of int
            sphere_center_atom_ids=list(map(int, center_id.split(","))),
            z_ax_atom_ids=list(map(int, z_id.split(","))),
            xz_plane_atoms_ids=list(map(int, xz_id.split(","))),
            atoms_to_delete_ids=list(map(int, del_id.split(","))),
            # working_dir="*/",
        )

        orig_layout.append(
            html.Div(
                [
                    html.Div(f"Initializing:"),
                    html.Div(f"File: {filename}"),
                    html.Div(f"center_id: {center_id}"),
                    html.Div(f"z_id: {z_id}"),
                    html.Div(f"xz_id: {xz_id}"),
                    html.Div(f"del_id: {del_id}"),
                    # add 3d visualization tool
                ]
            )
        )
        parser = PdbParser("https://git.io/4K8X.pdb")
        data = parser.mol3d_data()

        print(data)

        # add all tabs
        layout = html.Div(
            [
                dcc.Tabs(
                    [
                        dcc.Tab(label="setup", children=orig_layout),
                        # setup the 2d page
                        dcc.Tab(label="2D-Scan", children=create_2d_tab()),
                        # setup the 3d page
                        dcc.Tab(label="3D-Image", children=create_3d_tab()),
                    ]
                )
            ]
        )
        return layout

    elif n_clicks:
        orig_layout.append(html.Div(f"Please enter all setup parameters."))
        return orig_layout
    else:
        return orig_layout


@app.callback(
    Output("scan_plot_div", "children"),
    Input("scan_start_button", "n_clicks"),
    State("input_r_min", "value"),
    State("input_r_max", "value"),
    State("input_n_step", "value"),
    State("input_mesh_size", "value"),
    State("input_remove_h", "value"),
    State("input_radii_scale", "value"),
    prevent_initial_call=True,
)
def run_scan(n_clicks, r_min, r_max, nsteps, mesh_size, remove_h, radii_scale):
    # generate table

    app.df_scan = app.molecule_scanner.run_range(
        r_min=r_min,
        r_max=r_max,
        nsteps=nsteps,
        mesh_size=mesh_size,
        remove_H=bool(remove_h),
        write_surf_files=False,
        radii_scale=radii_scale,
    )
    # plot config
    plot_names = list(app.df_scan.keys())
    plot_names.remove("r")

    margin = dict(l=65, r=50, b=65, t=90, pad=10)

    width = 1000
    height = 500
    fontsize = 18
    config = {
        "toImageButtonOptions": {
            "format": "png",  # one of png, svg, jpeg, webp
            "filename": "Plot_Image",
            "height": height * 4,
            "width": width * 4,
            "scale": 5,  # Multiply title/legend/axis/canvas sizes by this factor
        }
    }

    scan_result_display = html.Div(
        [
            dash_table.DataTable(
                data=app.df_scan.round(4).to_dict("records"),
                page_size=10,
                export_format="csv",
                export_headers="display",
            ),
            html.H4("PLY Object Explorer"),
            html.P("Choose a feature to plot over r"),
            dcc.Dropdown(
                id="dropdown",
                options=plot_names,
                value="percent_buried_volume",
                clearable=False,
            ),
            dcc.Graph(id="graph", config=config),
        ],
        style={"width": "40%", "marginTop": "20px"},
    )

    return scan_result_display


@app.callback(Output("graph", "figure"), Input("dropdown", "value"))
def display_plot(name):
    margin = dict(l=65, r=50, b=65, t=90, pad=10)

    width = 1000
    height = 500
    fontsize = 18

    fig = go.Figure(
        data=go.Scatter(
            x=app.df_scan["r"].values,
            y=app.df_scan[name].values,
            mode="lines",
            name=name,
        )
    )

    fig.update_layout(
        autosize=True,
        width=width,
        height=height,
        margin=margin,
        yaxis=dict(
            ticksuffix="   ",
            tickfont_size=fontsize,
            title_text=name.replace("_", " "),
        ),
        xaxis=dict(
            ticksuffix="   ", tickfont_size=fontsize, title_text="Sphere radius"
        ),
    )
    return fig


@app.callback(
    Output("3d_plot_div", "children"),
    Input("3d_start_button", "n_clicks"),
    State("input_sphere_radius_3d", "value"),
    State("input_mesh_size_3d", "value"),
    State("input_remove_h_3d", "value"),
    prevent_initial_call=True,
)
def visualize_cavity(n_clicks, radius, mesh_size, remove_H):
    app.df_cavity = app.molecule_scanner.generate_cavity(radius, mesh_size)

    mesh_names = ["Top", "Bottom", "3D"]

    # this changes the save properties
    config = {
        "toImageButtonOptions": {
            "format": "png",  # one of png, svg, jpeg, webp
            "filename": "custom_image",
            "height": 2000,
            "width": 2000,
            "scale": 5,  # Multiply title/legend/axis/canvas sizes by this factor
        }
    }

    results_display_3d = html.Div(
        [
            html.H4("PLY Object Explorer"),
            html.P("Choose a cavity visualization:"),
            dcc.Dropdown(
                id="dropdown_3d", options=mesh_names, value="Top", clearable=False
            ),
            dcc.Graph(id="graph_3d", config=config),
        ],
        style={"width": "40%", "marginTop": "20px"},
    )
    return results_display_3d


@app.callback(Output("graph_3d", "figure"), Input("dropdown_3d", "value"))
def display_mesh(name):

    margin = dict(l=65, r=50, b=65, t=90, pad=10)

    contours_coloring = "heatmap"
    width = 500
    height = 500
    fontsize = 18
    X, Y, Z_top, Z_bottom = app.molecule_scanner.reshape_data(app.df_cavity)

    if name == "Top":

        fig = go.Figure(
            data=go.Contour(
                z=Z_top,
                x=np.unique(X),
                y=np.unique(Y),
                line_smoothing=1,
                contours_coloring=contours_coloring,
            ),
        )

    elif name == "Bottom":
        fig = go.Figure(
            data=go.Contour(
                z=Z_bottom,
                x=np.unique(X),
                y=np.unique(Y),
                line_smoothing=1,
                contours_coloring=contours_coloring,
            )
        )

    elif name == "3D":
        fig = go.Figure(
            data=[
                go.Surface(z=Z_top, x=X, y=Y),
                go.Surface(z=Z_bottom, x=X, y=Y, showscale=False),
            ]
        )

    fig.update_layout(
        autosize=True,
        width=width,
        height=height,
        margin=margin,
        yaxis=dict(ticksuffix="   ", tickfont_size=fontsize),
        xaxis=dict(ticksuffix="   ", tickfont_size=fontsize),
    )
    return fig
