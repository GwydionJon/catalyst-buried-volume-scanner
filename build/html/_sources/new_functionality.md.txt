# Catalyst-buried-volume-scanner User Guide

This package is intended to quickly get an overview of how different sphere radii affect the free buried volume of a given molecule.

After installing the python package simply call `cbvs_gui` to launch the web gui.

Here you can first select a xyz-file of the desired molecule.

## Setting up the molecular scanner

As this work is based on the original sambvca fortran code we need to first define the geometric orientation of our molecule.

To get the atom ids, simply select them in the 3d-viewer.
Below the 3d-viwer you can enter the atom ids into the corresponding input boxes.

<img src="/home/gwydion/Uni/oc_forschi/OC-Forschi/docs/source/pictures/first_page.png"
          style="float: left; margin-right: 10px;" />

Note that IDs have to be seperated with a comma when multiple IDs are given.

For defining the Z-axis it is best to choose the metal ion and one additional atom that is on the desired axis.
For the xy-plane choose three IDs that form the desired plane.
Lastly for the masking step choose all atoms whose radius you don't want to include into the calculation. This most likely includes the metal atom itself, as well as neighboring non organic-ligand atoms.

## Radii scan

<img src="/home/gwydion/Uni/oc_forschi/OC-Forschi/docs/source/pictures/second_page.png"
          style="float: left; margin-right: 10px;" />

All default values can be changed.
R-Min and R-Max set the boundaries of the scan range, while Steps is the number of calculations to perform between these two values.
A lower mesh size (eg: 0.05) will increase the accuracy slightly but has a large impact on performance.
Radius scaling lets you choose between the default radius as defined by Cavallo et al. as 1.17\* the Van der Vaals Radii and the unaltered VdW-Radii
The is also the option to include H atoms in the calculation.

Note that the graph might not auto update when first starting the calculation, simply changing the dropdown menu above the graph should fix this problem.

# 3D-Image

<img src="/home/gwydion/Uni/oc_forschi/OC-Forschi/docs/source/pictures/second_page.png"
          style="float: left; margin-right: 10px;" />

This tab is used to view a specific sphere radius in a bit more detail.
Here lower mesh sizes like 0.05 can be used, as the performance impact isn't as severe when only calculating a single radius.

The Dropdown menu let's you choose which view to visualize.

## References:

- https://chemistry-europe.onlinelibrary.wiley.com/doi/10.1002/ejic.200801160
- https://www.sciencedirect.com/science/article/pii/S0010854506002827?pes=vor
- https://pubs.rsc.org/en/content/articlelanding/2010/cc/b922984a
