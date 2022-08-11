from dash import dcc, html, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from molecule_scanner import *

# https://github.com/DouwMarx/dash_by_exe

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


# Create the app
app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    [
        # xyz-file upload
        html.Div(
            [
                html.H5("Here you can configure your burried volume calculation."),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                    style={
                        "width": "20%",
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
            [
                html.H5(
                    children="Enter the desired scan parameter",
                    style={"marginTop": "20px"},
                ),
                html.Div(
                    [
                        html.P("R-Min", style={"width": "5%"}),
                        dcc.Input(
                            id="input_r_min",
                            value=1.3,
                            type="number",
                            placeholder="Enter R-min",
                            style={"width": "20%"},
                        ),
                    ],style={'display': 'flex', 'flex-direction': 'row'}
                ),
            ]
        ),
        html.Button(id="init_button", n_clicks=0, children='Initilize molecule'),

    ], id="layout"
)


@app.callback( 
                Output("layout","children"),

                Input("init_button","n_clicks"),
                State("layout","children"),
                State("upload-data","filename"),
                State("input_sphere_center_atom_ids", "value"),
                State("input_z_ax_atom_ids", "value"),
                State("input_xz_plane_atoms_ids", "value"),
                State("input_atoms_to_delete_ids", "value"),

            )
def start_init(n_clicks,orig_layout, filename,center_id, z_id, xz_id, del_id):
    if n_clicks>1:
        orig_layout = orig_layout[0:-1]

    if n_clicks and filename and center_id:


        orig_layout.append(
            html.Div([
                html.Div(f"Initilizing:"),
                html.Div(f"File: {filename}"),
                html.Div(f"center_id: {center_id}"),
                html.Div(f"z_id: {z_id}"),
                html.Div(f"xz_id: {xz_id}"),
                html.Div(f"del_id: {del_id}"),
                ])
            )
        



        return orig_layout
    elif n_clicks:
        orig_layout.append(html.Div(f"Please enter all setup parameters."))
        return orig_layout
    else:
        return orig_layout


app.run_server(debug=True, use_reloader=True, port=8051)
