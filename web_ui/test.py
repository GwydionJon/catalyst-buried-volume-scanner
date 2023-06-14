import urllib.request as urlreq
import dash
from dash.dependencies import Input, Output, State
import dash_bio as dashbio
from dash import html, dcc
from dash_bio.utils import xyz_reader

app = dash.Dash(__name__)


data_file = "D:\SynologyDrive\Master\Forschungspraktikum\Martin\OC-Forschi\molecule_scanner\example_data\mad25_p.xyz"

from openeye import oechem

ifs = oechem.oemolistream()
ofs = oechem.oemolostream()


ifs.open(data_file)
ofs.open("output.pdb")
for mol in ifs.GetOEGraphMols():
    oechem.OEWriteMolecule(ofs, mol)


# with open(data_file, 'r', encoding='utf-8') as f:
#             lines = f.readlines()

# lines = '\n'.join(lines[2:])


# data = xyz_reader.read_xyz(datapath_or_datastring=lines, is_datafile=False)

# app.layout = html.Div([
#     dcc.Dropdown(
#         id='default-speck-preset-views',
#         options=[
#             {'label': 'Default', 'value': 'default'},
#             {'label': 'Ball and stick', 'value': 'stickball'}
#         ],
#         value='default'
#     ),
#     dashbio.Speck(
#         id='default-speck',
#         data=data
#     ),
# ])

# @app.callback(
#     Output('default-speck', 'presetView'),
#     Input('default-speck-preset-views', 'value'),
#     State("default-speck","view")
# )
# def update_preset_view(preset_name, view):
#     print(view)
#     return preset_name


# if __name__ == '__main__':
#     app.run_server(debug=True)
