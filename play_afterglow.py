import numpy as np
import afterglowpy as grb
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

time = np.linspace(1e1,1e6,30)

bands = {
    'r': 485448262349447.2,
    'g': 637517188729399.1,
    'i': 400258022050793.1,
    'R': 468671768303359.1,
    'I': 378163424193228.9,
    'V': 556239404189155.8,
    'B': 684457666666666.5,
    'z': 328443179329975.9,
    '10keV': 2.417990504024E+18,
    '1254.6 GHz': 1254600000000,
    '647.8 GHz': 647800000000
}

params = {
    'jetType': grb.jet.TopHat,
    'specType': 0,
    'thetaObs': 0.05,
    'E0': 1e53,
    'thetaCore': 0.1,
    'thetaWing': 0.4,
    'b': 6.0,
    'n0': 1e-3,
    'p': 2.2,
    'epsilon_e': 0.1,
    'epsilon_B': 0.01,
    'xi_N': 1.0,
    'd_L': 1e28,
    'z': 0.5
}

# slider_defs = [
#     ('thetaObs', 0.0, 0.8, params['thetaObs']),
#     ('log10_E0', 50.0, 60.0, np.log10(params['E0'])),
#     ('thetaCore', 0.01, 0.8, params['thetaCore']),
#     ('thetaWing', params['thetaCore']*1.1, 2.0, params['thetaWing']),
#     ('b', 0.0, 10.0, params['b']),
#     ('n0', 1e-5, 1.0, params['n0']),
#     ('p', 2.0, 3.0, params['p']),
#     ('epsilon_e', 1e-3, 0.5, params['epsilon_e']),
#     ('epsilon_B', 1e-6, 0.1, params['epsilon_B']),
#     ('xi_N', 0.1, 1.0, params['xi_N']),
#     ('z', 0.01, 5.0, params['z'])
# ]

# ('TopHat', 'Gaussian', 'PowerLawCore', 'GaussianCore', 'Spherical', 'PowerLaw')
nu  = bands['r']

flux = grb.fluxDensity(time, nu, **params)
fig, ax = plt.subplots(figsize = (8,6))
fig.subplots_adjust(left=0.05, bottom=0.25)
ax.loglog(time, flux)
ax.grid(True, linestyle = '-', linewidth = 0.3, which = 'both')
plt.show()