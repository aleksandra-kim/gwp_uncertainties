Welcome to gsa_framework!
=========================

This package allows computation of uncertainties in GWP and AGWP values for environmental flows with known radiative efficiencies, lifetimes and their respective perturbations.

For the uncertainty calculations we employ a method based on first-order Taylor expansion as suggested in the IPCC Climate Change report from 2013. Given a function :math:`f(x_1,...,x_k)`, the uncertaintty in :math:`f` can be computed as follows:

.. math::
    \\Delta f = \\sqrt{\\sum_i (\\Delta f_i)^2} = \\sqrt{\\sum_i \\big( \\frac{\\partial f}{\\partial x_i} \\Delta x_i  \\big)^2}


that are present in the Life Cycle Assessment method ("IPCC 2013", "climate change") with time horizons of 20 and 100 years.

Uncertainties in AGWP for $CO_2$ were
# Molecular weights taken from https://pubchem.ncbi.nlm.nih.gov/