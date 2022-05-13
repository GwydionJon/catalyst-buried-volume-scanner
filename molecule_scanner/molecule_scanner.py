import glob
import os
from tempfile import mkdtemp
import shutil
import numpy as np
import pandas as pd
from collections import defaultdict
from py2sambvca import p2s
from hashlib import sha256
from joblib import Parallel, delayed
from molecule_scanner import paths
from dash import dcc, html, Input, Output
from jupyter_dash import JupyterDash
import plotly.graph_objects as go

"""
displacement (float): Displacement of oriented molecule from sphere center in Angstrom (default 0.0)
        mesh_size (float): Mesh size for numerical integration (default 0.10)
        remove_H (int): 0/1 Do not remove/remove H atoms from Vbur calculation (default 1)
        orient_z (int): 0/1 Molecule oriented along negative/positive Z-axis (default 1)
        write_surf_files (int): 0/1 Do not write/write files for top and bottom surfaces (default 1)
        """


class MoleculeScanner:
    """
    Wrapper for the py2sambvca package
    """

    def __init__(
        self,
        xyz_filepath,
        sphere_center_atom_ids,
        z_ax_atom_ids,
        xz_plane_atoms_ids,
        atoms_to_delete_ids=None,
        # sphere_radius=3.5,
        # displacement=0.0,
        # mesh_size=0.10,
        # remove_H=1,
        # orient_z=1,
        # write_surf_files=1,
        working_dir=None,
        verbose=1,
    ):
        """
        This class serves as an intermediate between the py2sambvca package and the user.
        It enables the scanning of multiple sphere radii as well as plotting of the surface files.


        Args:
        xyz_filepath (str): Location of .xyz molecular coordinates file for writing input data
        sphere_center_atom_ids (list): ID of atoms defining the sphere center
        z_ax_atom_ids (list): ID of atoms for z-axis
        xz_plane_atoms_ids (list): ID of atoms for xz-plane
        atoms_to_delete_ids (list): ID of atoms to be deleted (default None)

        verbose (int): 0 for no output, 1 for some output, 2 for the most output
        """
        self.xyz_filepath = paths.locate_file(xyz_filepath)
        if atoms_to_delete_ids is not None:
            self.n_atoms_to_delete = len(atoms_to_delete_ids)
            self.atoms_to_delete_ids = atoms_to_delete_ids
        else:  # otherwise, set to none to avoid bad writes in the future
            self.n_atoms_to_delete = None
            self.atoms_to_delete_ids = None
        # various other parameters
        self.sphere_center_atom_ids = sphere_center_atom_ids
        self.n_sphere_center_atoms = len(sphere_center_atom_ids)
        self.z_ax_atom_ids = z_ax_atom_ids
        self.n_z_atoms = len(z_ax_atom_ids)
        self.xz_plane_atoms_ids = xz_plane_atoms_ids
        self.n_xz_plane_atoms = len(xz_plane_atoms_ids)
        self.sambvca21_path = paths.load_executable()

        if working_dir is None:
            self.working_dir = mkdtemp()
        else:
            self.working_dir = working_dir

    def run_single(
        self,
        sphere_radius,
        displacement=0.0,
        mesh_size=0.10,
        remove_H=True,
        orient_z=True,
        write_surf_files=True,
        return_surface_files=False,
    ):

        """Calculates the results for a single radius.

        Args:
        sphere_radius (float): The radius of the sphere.
        displacement (float): Displacement of oriented molecule from sphere center in Angstrom (default 0.0)
        mesh_size (float): Mesh size for numerical integration (default 0.10)

        remove_H (bool): True/False Do not remove/remove H atoms from Vbur calculation (default True)

        orient_z (bool): True/False Molecule oriented along negative/positive Z-axis (default True)

        write_surf_files (bool): True/False Do not write/write files for top and bottom surfaces (default True)
        return_surface_files (bool): only for internal use. Parses .dat files to generate cavity function.

        Returns:
            list: a list of the three dictionaries for the total result, quadrant results and octant results.
        """
        dir_name = str(
            os.path.join(
                self.working_dir,
                str(
                    abs(
                        hash(
                            (
                                sphere_radius,
                                displacement,
                                mesh_size,
                                remove_H,
                                orient_z,
                                write_surf_files,
                            )
                        )
                    )
                ),
            )
        )
        if not os.path.isdir:
            os.mkdir(dir_name)

        nhc_p2s = p2s(
            xyz_filepath=self.xyz_filepath,
            sphere_center_atom_ids=self.sphere_center_atom_ids,
            z_ax_atom_ids=self.z_ax_atom_ids,
            xz_plane_atoms_ids=self.xz_plane_atoms_ids,
            atoms_to_delete_ids=self.atoms_to_delete_ids,
            sphere_radius=sphere_radius,
            displacement=displacement,
            mesh_size=mesh_size,
            remove_H=int(remove_H),
            orient_z=int(orient_z),
            write_surf_files=int(write_surf_files),
            path_to_sambvcax=self.sambvca21_path,
            working_dir=dir_name,
        )
        nhc_p2s.write_input()
        nhc_p2s.calc()
        test_m = nhc_p2s.get_regex(
            r"^[ ]{5,6}(\d*\.\d*)[ ]{5,6}(\d*\.\d*)[ ]{5,6}(\d*\.\d*)[ ]{5,6}(\d*\.\d*)$"
        )

        if return_surface_files == True:
            return os.path.join(
                dir_name, "py2sambvca_input-TopSurface.dat"
            ), os.path.join(dir_name, "py2sambvca_input-BotSurface.dat")

        if test_m is not None:
            return nhc_p2s.parse_output()
        else:
            print(
                f"No volume could be found for r = {sphere_radius}, skipping output gathering."
            )
            return None, None, None

    def run_range(
        self,
        r_min,
        r_max,
        nsteps=50,
        displacement=0.0,
        mesh_size=0.10,
        remove_H=True,
        orient_z=True,
        write_surf_files=True,
        n_threads=-1,
    ):
        """
        This function is designed to scan a range of sphere_radii.
        The results are stores in a pandas dataframe.
        Note: If the given radius is too big or too small no output will be stored for this radius.
        Args:
            r_min (number): minimum radius
            r_max (number): maximum radius
            nsteps (int, optional): Number of steps. Defaults to 50.
            sphere_radius (float): The radius of the sphere.
            displacement (float): Displacement of oriented molecule from sphere center in Angstrom (default 0.0)
            mesh_size (float): Mesh size for numerical integration (default 0.10)

            remove_H (bool): True/False Do not remove/remove H atoms from Vbur calculation (default True)

            orient_z (bool): True/False Molecule oriented along negative/positive Z-axis (default True)

            write_surf_files (bool): True/False Do not write/write files for top and bottom surfaces (default True)

            n_threads (int): Sets the number of parallel threads used for calculation. -1 for unlimited. (default -1)
        Returns:
            pandas.DataFrame: A DateFrame object for easy access to the results.
        """

        def _run_job(r_current):
            total_results, quadrant_results, octant_results = self.run_single(
                sphere_radius=r_current,
                displacement=displacement,
                mesh_size=mesh_size,
                remove_H=remove_H,
                orient_z=orient_z,
                write_surf_files=write_surf_files,
            )

            if total_results is not None:
                dict_total_results["r"].append(r_current)
                [
                    dict_total_results[key].append(value)
                    for key, value in total_results.items()
                ]

        dict_total_results = defaultdict(list)

        #:
        Parallel(n_jobs=n_threads, prefer="threads", require="sharedmem")(
            delayed(_run_job)(r) for r in np.linspace(r_min, r_max, nsteps)
        )

        df_total_results = (
            pd.DataFrame(dict_total_results)
            .reset_index(drop=True)
            .sort_values(by=["r"])
        )
        # return original values

        return df_total_results

    def plot_graph(self, df):
        """Generate an interactive widget to plot the resulting cavity data against the sphere radius.

        :param df: A DataFrame object generated by the `run_range` function.
        :type df: pandas.DataFrame

        """
        # parameter setup
        plot_names = list(df.keys())
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

        # app setup
        app = JupyterDash(__name__)

        app.layout = html.Div(
            [
                html.H4("PLY Object Explorer"),
                html.P("Choose a feature to plot over r"),
                dcc.Dropdown(
                    id="dropdown",
                    options=plot_names,
                    value="percent_buried_volume",
                    clearable=False,
                ),
                dcc.Graph(id="graph", config=config),
            ]
        )

        # plot setup
        @app.callback(Output("graph", "figure"), Input("dropdown", "value"))
        def display_plot(name):
            fig = go.Figure(
                data=go.Scatter(
                    x=df["r"].values, y=df[name].values, mode="lines", name=name
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

        # run server in jupyter notebook cell
        app.run_server(
            mode="inline",
            port=8091,
            dev_tools_ui=False,  # debug=True,
            dev_tools_hot_reload=False,
            threaded=True,
        )

    # Plotting the cavity

    def generate_cavity(self, sphere_radius, mesh_size, **args):
        """
        Calculates and returns the cavity file data.
        uses same arguments as run_single.
        """
        top_file, bottom_file = self.run_single(
            sphere_radius=sphere_radius,
            mesh_size=mesh_size,
            return_surface_files=True,
            **args,
        )
        df_top = pd.read_table(top_file, sep="\s+", usecols=[0, 1, 2], header=None)
        df_bottom = pd.read_table(
            bottom_file, sep="\s+", usecols=[0, 1, 2], header=None
        )
        df_cavity = df_top[[0, 1]]
        df_cavity["top"] = df_top[2]
        df_cavity["bottom"] = df_bottom[2]
        df_cavity["top"] = df_cavity["top"].replace(-7.0, np.nan)
        df_cavity["bottom"] = df_cavity["bottom"].replace(7.0, np.nan)

        return df_cavity

    def reshape_data(self, df_cavity):
        x_y_len = len(np.unique(df_cavity[0]))
        x = df_cavity[0].values
        y = df_cavity[1].values
        z_top = df_cavity["top"].values
        z_bottom = df_cavity["bottom"].values
        X = x.reshape((x_y_len, -1))
        Y = y.reshape((x_y_len, -1))
        Z_top = z_top.reshape((x_y_len, -1))
        Z_bottom = z_bottom.reshape((x_y_len, -1))

        return X, Y, Z_top, Z_bottom

    def visualize_cavity(self, sphere_radius, mesh_size, **args):
        """
        Generate a Top, Bottom and 3D view of the cavity.
        when saving the resolution is 4 times higher than in the notebook.

        :param df_cavity: _description_
        :type df_cavity: _type_
        :return: _description_
        :rtype: _type_
        """

        df_cavity = self.generate_cavity(sphere_radius, mesh_size, **args)
        X, Y, Z_top, Z_bottom = self.reshape_data(df_cavity)

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

        app = JupyterDash(__name__)

        app.layout = html.Div(
            [
                html.H4("PLY Object Explorer"),
                html.P("Choose a cavity visualisation:"),
                dcc.Dropdown(
                    id="dropdown", options=mesh_names, value="Top", clearable=False
                ),
                dcc.Graph(id="graph", config=config),
            ]
        )

        margin = dict(l=65, r=50, b=65, t=90, pad=10)

        contours_coloring = "heatmap"
        width = 500
        height = 500
        fontsize = 18

        # create the three different objects
        @app.callback(Output("graph", "figure"), Input("dropdown", "value"))
        def display_mesh(name):
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

        # run server in jupyter notebook cell
        app.run_server(
            mode="inline",
            port=8090,
            dev_tools_ui=False,  # debug=True,
            dev_tools_hot_reload=False,
            threaded=True,
        )
