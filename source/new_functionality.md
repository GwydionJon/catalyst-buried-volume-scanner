# Catalyst-buried-volume-scanner User Guide

This software package is designed to provide a rapid overview of how varying sphere radii impact the free buried volume of a given molecule.

Upon successful installation of the Python package, initiate the web GUI by executing the command cbvs_gui.

## Setting up the molecular scanner

Since this work is built upon the original SAMBVCA Fortran code, the initial step involves defining the geometric orientation of the molecule. To obtain the atom IDs, simply select them in the 3D viewer. Below the 3D viewer, input the atom IDs into the respective boxes.

<img src="https://github.com/GwydionJon/catalyst-buried-volume-scanner/blob/main/docs/source/pictures/first_page.png?raw=true"
          style="float: left; margin-right: 10px;" />

Note that when providing multiple IDs, they should be separated by a comma.

For defining the Z-axis, it is recommended to choose the metal ion and one additional atom on the desired axis. To establish the XY-plane, select three IDs that form the intended plane. Lastly, for the masking step, include all atoms whose radius should not be considered in the calculation, which typically involves the metal atom itself and neighboring non-organic ligand atoms.

## Radii scan

<img src="https://github.com/GwydionJon/catalyst-buried-volume-scanner/blob/main/docs/source/pictures/second_page.png?raw=true"
          style="float: left; margin-right: 10px;" />

R-Min and R-Max set the boundaries of the scan range, while Steps determine the number of calculations between these two values. A lower mesh size (e.g., 0.05) increases accuracy slightly but significantly impacts performance. Radius scaling allows you to choose between the default radius, as defined by Cavallo et al. (1.17 times the Van der Waals Radii), and the unaltered VdW-Radii. There is also an option to include H atoms in the calculation.

Please note that the graph may not auto-update initially during the calculation. Simply changing the dropdown menu above the graph should resolve this issue.

# 3D-Image

<img src="https://github.com/GwydionJon/catalyst-buried-volume-scanner/blob/main/docs/source/pictures/third_page.png?raw=true"
          style="float: left; margin-right: 10px;" />

This tab is utilized to view a specific sphere radius in more detail. Lower mesh sizes, such as 0.05, can be employed as the performance impact is less severe when calculating a single radius.

The dropdown menu enables you to choose the visualization perspective.

## References:

- https://chemistry-europe.onlinelibrary.wiley.com/doi/10.1002/ejic.200801160
- https://www.sciencedirect.com/science/article/pii/S0010854506002827?pes=vor
- https://pubs.rsc.org/en/content/articlelanding/2010/cc/b922984a
