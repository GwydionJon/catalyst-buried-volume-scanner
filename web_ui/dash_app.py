from dash import dcc, html, Dash, dash_table
from dash.dependencies import Input, Output, State
from molecule_scanner import *
import os
import base64
from tempfile import mkdtemp
import plotly.graph_objects as go
import numpy as np
import dash_bio as dashbio
import pandas as pd
from dash_bio.utils import create_mol3d_style
import xyz_py as xyzp


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
app.molecule_scanner = None


@app.callback(
    Output("upload-data", "children"),
    Output("3dmol_div", "children"),
    Input("upload-data", "filename"),
    Input("upload-data", "contents"),
    prevent_initial_call=True,
)
def update_upload_label(filename, file_content):
    data = file_content.encode("utf8").split(b";base64,")[1]
    filename_complete = os.path.join(working_dir, filename)
    with open(filename_complete, "wb") as fp:
        fp.write(base64.decodebytes(data))

    viwer_3d_entries = create_3d_viewer(os.path.join(working_dir, filename_complete))
    return (
        html.Div([f"Loaded {filename}.  Upload new ", html.A("File")]),
        viwer_3d_entries,
    )


def create_3d_viewer(filename):
    def _get_3d_color_map():

        ATOM_COLORS = {
            "C": "#c8c8c8",
            "H": "#ffffff",
            "N": "#8f8fff",
            "S": "#ffc832",
            "O": "#f00000",
            "F": "#ffff00",
            "P": "#ffa500",
            "K": "#42f4ee",
            "G": "#3f3f3f",
            "Au": "#ffd700",
            "Cl": "#008000",
        }

        return ATOM_COLORS

    # get coordinates and atom labels
    atom_list_indices, atom_coords = xyzp.load_xyz(
        "./test/data/nhc.xyz", add_indices=True
    )
    atom_list_no_indices = xyzp.load_xyz("./test/data/nhc.xyz", add_indices=False)[0]

    # get bonds

    bonds_list = xyzp.find_bonds(atom_list_indices, atom_coords, style="indices")[0]

    # transform to dash bio data
    data_3d = {"atoms": [], "bonds": []}
    for i, (atom_ind, atom_label, atom_coord) in enumerate(
        zip(atom_list_indices, atom_list_no_indices, atom_coords)
    ):
        new_atom = {
            "serial": i,
            "name": atom_label,
            "elem": atom_label,
            "positions": [atom_coord[0], atom_coord[1], atom_coord[2]],
        }
        data_3d["atoms"].append(new_atom)

    for bond in bonds_list:
        new_bond = {"atom1_index": bond[0], "atom2_index": bond[1], "bond_order": 1}
        data_3d["bonds"].append(new_bond)

    # set style
    styles = create_mol3d_style(
        data_3d["atoms"],
        visualization_type="stick",
        color_element="atom",
        color_scheme=_get_3d_color_map(),
    )

    output = [
        dashbio.Molecule3dViewer(
            id="molecule3d-viewer",
            modelData=data_3d,
            styles=styles,
            backgroundColor="#4E0707",
            backgroundOpacity=1,
        ),
        html.Hr(),
        html.Div(
            id="molecule3d-selected-names",
            style={"display": "inline-block"},
        ),
    ]
    return output


@app.callback(
    Output("molecule3d-selected-names", "children"),
    Input("molecule3d-viewer", "selectedAtomIds"),
    State("molecule3d-viewer", "modelData"),
    prevent_initial_call=True,
)
def show_selected_atoms(atom_ids, modelData):
    if atom_ids is None or len(atom_ids) == 0:
        return "No atom has been selected. Click somewhere on the molecular \
        structure to select an atom."

    return [
        html.Div(
            [
                html.Div("Element: {} \t   ".format(modelData["atoms"][atm]["name"])),
                html.Div("Serial: {}".format(modelData["atoms"][atm]["serial"])),
                html.Br(),
            ],
            style={"width": 100, "display": "inline-block"},
        )
        for atm in atom_ids
    ]


def create_main_page():
    tab_main_page = html.Div(
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
            html.Div(children=[], id="3dmol_div"),
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
                html.Button(
                    id="init_button", n_clicks=0, children="Initialize molecule"
                )
            ),
            html.Div(id="setup_config"),
        ],
        id="main_page",
    )
    return tab_main_page


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
                                dcc.Dropdown(
                                    id="input_radii_scale",
                                    options=["default", "vdw"],
                                    value="default",
                                    placeholder="Enter radii type",
                                    style={"width": "40%"},
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
                        id="loading_scan2d",
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
                        id="loading_scan3d",
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
    Output("setup_config", "children"),
    Input("init_button", "n_clicks"),
    State("upload-data", "filename"),
    State("input_sphere_center_atom_ids", "value"),
    State("input_z_ax_atom_ids", "value"),
    State("input_xz_plane_atoms_ids", "value"),
    State("input_atoms_to_delete_ids", "value"),
    prevent_initial_call=True,
)
def start_init(n_clicks, filename, center_id, z_id, xz_id, del_id):

    if n_clicks and filename and center_id and z_id and xz_id and del_id:
        # setup molecule scanner as part of the app object
        try:
            # split comma separated strings into list of int
            # we need to add 1 to all atom ids, because the molecule scanner expects indexing starting on 1 but the chemical convention is starting at 0
            sphere_atom_ids = np.asarray(list(map(int, center_id.split(",")))) + 1
            z_ax_atom_ids = np.asarray(list(map(int, z_id.split(",")))) + 1
            xz_plane_atoms_ids = np.asarray(list(map(int, xz_id.split(",")))) + 1
            atoms_to_delete_ids = np.asarray(list(map(int, del_id.split(",")))) + 1

            app.molecule_scanner = msc(
                xyz_filepath=os.path.join(working_dir, filename),
                sphere_center_atom_ids=sphere_atom_ids,
                z_ax_atom_ids=z_ax_atom_ids,
                xz_plane_atoms_ids=xz_plane_atoms_ids,
                atoms_to_delete_ids=atoms_to_delete_ids,
            )
        except ValueError as e:
            if "invalid literal for int() with base 10" in str(e):
                return html.Div(
                    "Please make sure you have separated all values with commas and not dots."
                )
            else:
                return html.Div(str(e))
        return html.Div(
            [
                html.Div("Initializing:"),
                html.Div(f"File: {filename}"),
                html.Div(f"center_id: {center_id}"),
                html.Div(f"z_id: {z_id}"),
                html.Div(f"xz_id: {xz_id}"),
                html.Div(f"del_id: {del_id}"),
                # add 3d visualization tool
            ]
        )

        # add all tabs

    elif n_clicks:
        return html.Div("Please enter all setup parameters.")


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
def run_scan(n_clicks, r_min, r_max, nsteps, mesh_size, remove_h, radii_table):
    # generate table

    if app.molecule_scanner is None:
        return html.Div("Please finish the setup first.")

    app.df_scan = app.molecule_scanner.run_range(
        r_min=r_min,
        r_max=r_max,
        nsteps=nsteps,
        mesh_size=mesh_size,
        remove_H=bool(remove_h),
        write_surf_files=False,
        radii_table=radii_table,
    )

    if app.df_scan is None:
        return html.Div(
            "No results found, please check that all your given indices are correct."
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


@app.callback(
    Output("graph", "figure"),
    Input("dropdown", "value"),
    prevent_initial_call=True,
)
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
)
def visualize_cavity(n_clicks, radius, mesh_size, remove_H):
    if app.molecule_scanner is None:
        return html.Div("")

    app.df_cavity = app.molecule_scanner.generate_cavity(radius, mesh_size)

    mesh_names = ["Top", "Bottom", "Top+Bottom", "3D"]

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
                id="dropdown_3d", options=mesh_names, value="Bottom", clearable=False
            ),
            dcc.Graph(id="graph_3d", config=config),
        ],
        style={"width": "40%", "marginTop": "20px"},
    )
    return results_display_3d


@app.callback(
    Output("graph_3d", "figure"),
    Input("dropdown_3d", "value"),
    # prevent_initial_call=True,
)
def display_mesh(name):

    margin = dict(l=65, r=50, b=65, t=90, pad=10)

    contours_coloring = "heatmap"
    contours_dict = {"size": 0.1}
    width = 500
    height = 500
    fontsize = 18
    line_smoothing = 0

    X, Y, Z_top, Z_bottom, Z_both = app.molecule_scanner.reshape_data(app.df_cavity)

    if name == "Top":

        fig = go.Figure(
            data=go.Contour(
                z=Z_top,
                x=np.unique(X),
                y=np.unique(Y),
                line_smoothing=line_smoothing,
                contours=contours_dict,
                contours_coloring=contours_coloring,
            ),
        )

    elif name == "Bottom":
        fig = go.Figure(
            data=go.Contour(
                z=Z_bottom,
                x=np.unique(X),
                y=np.unique(Y),
                line_smoothing=line_smoothing,
                contours=contours_dict,
                contours_coloring=contours_coloring,
            )
        )
    elif name == "Top+Bottom":
        fig = go.Figure(
            data=go.Contour(
                z=Z_both,
                x=np.unique(X),
                y=np.unique(Y),
                line_smoothing=line_smoothing,
                contours=contours_dict,
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


app.layout = html.Div(
    [
        dcc.Tabs(
            children=[
                dcc.Tab(create_main_page(), id="main_tab", label="Setup"),
                dcc.Tab(label="2D-Scan", children=create_2d_tab()),
                # setup the 3d page
                dcc.Tab(label="3D-Image", children=create_3d_tab()),
            ],
            id="main_tabs",
        ),
    ],
    id="layout",
)


if __name__ == "__main__":
    app.run_server(debug=True, port=8012)
