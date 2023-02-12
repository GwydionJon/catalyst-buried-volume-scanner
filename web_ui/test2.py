import dash
import dash_bio as dashbio
from dash import html
from dash_bio.utils import PdbParser, create_mol3d_style
from dash.dependencies import Input, Output
from collections import defaultdict

app = dash.Dash(__name__)

# parser = PdbParser("test/data/GC1.pdb")
# parser = PdbParser("https://git.io/4K8X.pdb")

data = {"atoms": [], "bonds": []}

filename = "test/data/benzene.pdb"


bonds_dict = defaultdict(lambda: 0)
with open(filename, encoding="utf-8") as file:
    for line in file.readlines():
        split_line = " ".join(line.split()).split()

        if "HETATM" in split_line:
            data["atoms"].append(
                {
                    "serial": int(split_line[1]),
                    "name": split_line[2],
                    "elem": split_line[3],
                    "positions": [
                        float(split_line[4]),
                        float(split_line[5]),
                        float(split_line[6]),
                    ],
                }
            )
        elif "CONECT" in split_line:
            for i in range(2, len(split_line)):
                bonds_dict[(split_line[1], split_line[i])] += 1

                data["bonds"].append(
                    {"atom1_index": 1, "atom2_index": 2, "bond_order": 2.0}
                )
                data["bonds"].append(
                    {"atom1_index": 1, "atom2_index": 11, "bond_order": 2.0}
                )
    # for keys, value in bonds_dict.items():
    #     data["bonds"].append(
    #         {
    #             "atom1_index": int(keys[0])-1,
    #             "atom2_index": int(keys[1])-1,
    #             "bond_order": float(value),
    #         }
    #     )


print(data)
# data = {"atoms":[{'serial': 0, 'name': 'C', 'elem': 'C', 'positions': [1.177, 31.824, -35.755], 'mass_magnitude': 32.065, 'residue_index': 0, 'residue_name': 'CYS', 'chain': 'A'},
#  {'serial': 1, 'name': 'N', 'elem': 'N', 'positions': [0.029, 32.203, -34.096], 'mass_magnitude': 32.065, 'residue_index': 1, 'residue_name': 'CYS', 'chain': 'A'},
#  {'serial': 2, 'name': 'H', 'elem': 'H', 'positions': [0.029, 32.203, -38.096], 'mass_magnitude': 32.065, 'residue_index': 1, 'residue_name': 'CYS', 'chain': 'A'}],
#                 "bonds":[{'atom1_index': 0, 'atom2_index': 1, 'bond_order': 1.0}]}

# print(data)

styles = create_mol3d_style(
    data["atoms"], visualization_type="stick", color_element="atom"
)

app.layout = html.Div(
    [
        dashbio.Molecule3dViewer(
            id="dashbio-default-molecule3d",
            modelData=data,
            styles=styles,
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

    app.run_server(
        debug=True,
    )
