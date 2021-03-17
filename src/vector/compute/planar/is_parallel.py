# Copyright (c) 2019-2021, Jonas Eschle, Jim Pivarski, Eduardo Rodrigues, and Henry Schreiner.
#
# Distributed under the 3-clause BSD license, see accompanying file LICENSE
# or https://github.com/scikit-hep/vector for details.

import numpy

from vector.compute.planar import dot, rho
from vector.methods import AzimuthalRhoPhi, AzimuthalXY, _aztype

dispatch_map = {}


def make_function(azimuthal1, azimuthal2):
    dot_function, _ = dot.dispatch_map[azimuthal1, azimuthal2]
    rho1_function, _ = rho.dispatch_map[
        azimuthal1,
    ]
    rho2_function, _ = rho.dispatch_map[
        azimuthal2,
    ]

    def f(lib, tolerance, coord11, coord12, coord21, coord22):
        return dot_function(lib, coord11, coord12, coord21, coord22) > (
            1 - lib.absolute(tolerance)
        ) * rho1_function(lib, coord11, coord12) * rho2_function(lib, coord21, coord22)

    dispatch_map[azimuthal1, azimuthal2] = (f, bool)


for azimuthal1 in (AzimuthalXY, AzimuthalRhoPhi):
    for azimuthal2 in (AzimuthalXY, AzimuthalRhoPhi):
        make_function(azimuthal1, azimuthal2)


def dispatch(tolerance, v1, v2):
    if v1.lib is not v2.lib:
        raise TypeError(
            f"cannot use {v1} (requires {v1.lib}) and {v2} (requires {v1.lib}) together"
        )
    function, *returns = dispatch_map[
        _aztype(v1),
        _aztype(v2),
    ]
    with numpy.errstate(all="ignore"):
        return v1._wrap_result(
            function(
                v1.lib,
                tolerance,
                *v1.azimuthal.elements,
                *v2.azimuthal.elements,
            ),
            returns,
        )
