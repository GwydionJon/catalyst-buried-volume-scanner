import glob
import os
from tempfile import mkdtemp
import shutil
import sys
import numpy as np
import pandas as pd
from collections import defaultdict

class MoleculeScanner:
    """
    Wrapper for the py2sambvca package
    """


    def __init__():
        pass
    
    
    
    
    def run_range(self, r_min, r_max, nstep=50):
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

        # store original input_file and radius values:
        old_radius = self.sphere_radius
        old_input_filee = self.input_file

        dict_total_results = defaultdict(list)

        for r in np.linspace(r_min, r_max, nstep):
            self.input_file = os.path.join(self.tmp_dir, f"py2sambvca_input_r_{r}.inp")
            self.sphere_radius = r
            self.write_input()
            self.calc()
            total_results, quadrant_results, octant_results = self.parse_output()
            if total_results["total_volume"] != 0:
                dict_total_results["r"].append(r)
                [
                    dict_total_results[key].append(value)
                    for key, value in total_results.items()
                ]

        df_total_results = pd.DataFrame(dict_total_results)
        # return original values
        self.sphere_radius = old_radius
        self.input_file = old_input_filee

        return df_total_results
