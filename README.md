# py2sambvca

[![Documentation Status](https://readthedocs.org/projects/py2sambvca/badge/)](https://py2sambvca.readthedocs.io/en/latest/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/GwydionJon/OC-Forschi/main?urlpath=https%3A%2F%2Fgithub.com%2FGwydionJon%2FOC-Forschi%2Ftree%2Fmain%2Fnotebooks)

## Disclaimer

This work uses the `py2sambvca` package by Burns, J. figshare. 2020, DOI:10.6084/m9.figshare.12846707.
(https://github.com/JacksonBurns/py2sambvca)

This work also includes the `sambvca` source code from Falivene, L. et al. Nat. Chem. 2019, DOI:10.1038/s41557-019-0319-5.

## Installation

As of now this package is not on PyPi but can be installed via:

```python
pip install git+https://github.com/GwydionJon/py2sambvca
```

## License

`py2sambvca` is available under the GNU GPLv3 in accordance with the base Fortran code which is available under the same license and can be retreieved here: https://www.molnac.unisa.it/OMtools/sambvca2.1/download/download.html

The original fortran program (`sambvca21.f`) is also included in the `molecule_scaner/excecutable` directory. It is still under the same terms of the GNU license:

- This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.
- This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
- The results obtained from using the source code shall be used for scientific purposes only, excluding industrial or commercial purposes. To use the SambVca suite for industrial or commercial purposes, contact lcavallo|@|unisa.it.
- Proper acknowledgement shall be made to the author of the source code in publications resulting from the use of it in its original form or modified.
- The results from using the source code are provided "AS IS" without warranty of any kind.

## Citation

Please cite the `SambVca` base fortran tool as: Falivene, L. et al. Nat. Chem. 2019, DOI:10.1038/s41557-019-0319-5

`py2sambvca` has been uploaded to Figshare and may be cited as: Burns, J. figshare. 2020, DOI:10.6084/m9.figshare.12846707
