import glob
import os
from tempfile import mkdtemp
import shutil
import sys
import numpy as np
import pandas as pd
from collections import defaultdict
from py2sambvca import p2s
from hashlib import sha256

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
        self.xyz_filepath = xyz_filepath
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

        sambvcax_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "executables"
        )
        if sys.platform == "win32":
            self.sambvca21_path = os.path.join(sambvcax_dir, "sambvca21.exe")
        else:
            self.sambvca21_path = os.path.join(sambvcax_dir, "sambvca21.x")

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
    ):
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
        return nhc_p2s.parse_output()

    def run_range(
        self,
        r_min,
        r_max,
        nstep=50,
        displacement=0.0,
        mesh_size=0.10,
        remove_H=True,
        orient_z=True,
        write_surf_files=True,
    ):
        """
        This function is designed to scan a range of sphere_radii.
        The results are stores in a pandas dataframe.
        Note: If the given radius is too big or too small no output will be stored for this radius.
        Args:
            r_min (number): minimum radius
            r_max (number): maximum radius
            nstep (int, optional): Number of steps. Defaults to 50.

        Returns:
            pandas.DataFrame: A DateFrame object for easy accsess to the results.
        """

        dict_total_results = defaultdict(list)

        for r in np.linspace(r_min, r_max, nstep):

            total_results, quadrant_results, octant_results = self.run_single(
                sphere_radius=r,
                displacement=displacement,
                mesh_size=mesh_size,
                remove_H=remove_H,
                orient_z=orient_z,
                write_surf_files=write_surf_files,
            )

            if total_results["total_volume"] != 0:
                dict_total_results["r"].append(r)
                [
                    dict_total_results[key].append(value)
                    for key, value in total_results.items()
                ]

        df_total_results = pd.DataFrame(dict_total_results)
        # return original values

        return df_total_results
