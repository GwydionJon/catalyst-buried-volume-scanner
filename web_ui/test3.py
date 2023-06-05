import dash
import dash_bio as dashbio
from dash import html
from dash_bio.utils import create_mol3d_style
import chemcoord as cc
import pandas as pd
from dash.dependencies import Input, Output


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


filename = "test/data/mad25_p.xyz"

# get coordinates and atom labels
cartesion_xyz = cc.Cartesian.read_xyz(filename, start_index=1)
df_atoms = pd.DataFrame()
for column in cartesion_xyz.columns:
    df_atoms[column] = cartesion_xyz[column]
df_atoms = df_atoms.reset_index()

# get bonds
df_bonds = pd.DataFrame()
z_matrix = cartesion_xyz.get_zmat()[1:]
z_matrix["b"] = z_matrix["b"].astype(int)
df_bonds = z_matrix[["b", "bond"]].loc[z_matrix["bond"] < 3].reset_index()

# transform to dash bio data
data = {"atoms": [], "bonds": []}
for atom in df_atoms.values:
    new_atom = {
        "serial": atom[0],
        "name": atom[1],
        "elem": atom[1],
        "positions": [atom[2], atom[3], atom[4]],
    }
    data["atoms"].append(new_atom)

for bond in df_bonds.values:
    new_bond = {"atom1_index": bond[0], "atom2_index": bond[1], "bond_order": 1}
    data["bonds"].append(new_bond)

# set style
styles = create_mol3d_style(
    data["atoms"],
    visualization_type="stick",
    color_element="atom",
    color_scheme=_get_3d_color_map(),
)

app = dash.Dash(__name__)


app.layout = html.Div(
    [
        dashbio.Molecule3dViewer(
            id="dashbio-default-molecule3d",
            #  modelData=data,
            #    styles=styles,
            backgroundColor="#4E0707",
            backgroundOpacity=1,
        ),
        html.Hr(),
        html.Div(id="default-molecule3d-output"),
    ]
)


@app.callback(
    Output("default-molecule3d-output", "children"),
    Input("dashbio-default-molecule3d", "selectedAtomIds"),
)
def show_selected_atoms(atom_ids):
    if atom_ids is None or len(atom_ids) == 0:
        return "No atom has been selected. Click somewhere on the molecular \
        structure to select an atom."
    return [
        html.Div(
            [
                html.Div("Element: {}".format(data["atoms"][atm]["name"])),
                html.Div("Serial: {}".format(data["atoms"][atm]["serial"])),
                html.Br(),
            ]
        )
        for atm in atom_ids
    ]


if __name__ == "__main__":

    app.run_server(debug=True, port=8086)
