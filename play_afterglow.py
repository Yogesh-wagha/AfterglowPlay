import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons
import afterglowpy as grb

fig, ax = plt.subplots(figsize=(12, 12))
plt.subplots_adjust(left=0.25, bottom=0.4, right=0.75)

time = np.geomspace(1e1, 1e6, 30)

bands = {
    'r': 485448262349447.2,
    'g': 637517188729399.1,
    'i': 400258022050793.1,
    'R': 468671768303359.1,
    'I': 378163424193228.9,
    'TKEV': 12.417990504024E+18,
    'RA': 1254600000000
}
band_lines = {}
#initial params
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

def plot_bands():
    ax.clear()
    for band, freq in bands.items():
        if check.get_status()[list(bands).index(band)]:
            Fnu = grb.fluxDensity(time, np.full_like(time, freq), **params)
            line, = ax.loglog(time, Fnu, label=f'{band}-band (ν={freq:.1e} Hz)')
            band_lines[band] = line
    ax.legend()
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Flux density (mJy)')
    fig.canvas.draw_idle()

slider_defs = [
    ('thetaObs', 0.0, 0.3, params['thetaObs']),
    ('log10_E0', 45.0, 60.0, np.log10(params['E0'])),
    ('thetaCore', 0.001, 0.3, params['thetaCore']),
    ('thetaWing', params['thetaCore']*1.1, 2.0, params['thetaWing']),
    ('b', 0.0, 10.0, params['b']),
    ('n0', 1e-5, 1.0, params['n0']),
    ('p', 2.0, 3.0, params['p']),
    ('epsilon_e', 1e-3, 0.5, params['epsilon_e']),
    ('epsilon_B', 1e-6, 0.1, params['epsilon_B']),
    ('xi_N', 0.1, 1.0, params['xi_N']),
    ('z', 0.01, 10.0, params['z'])
]
sliders = {}
for i, (key, vmin, vmax, init) in enumerate(slider_defs):
    axsl = plt.axes([0.25, 0.30 - i*0.025, 0.65, 0.02])
    sliders[key] = Slider(axsl, key, valmin=vmin, valmax=vmax, valinit=init)

rax = plt.axes([0.8, 0.65, 0.15, 0.25])
radio = RadioButtons(rax, ('TopHat', 'Gaussian', 'PowerLawCore', 'GaussianCore', 'Spherical', 'PowerLaw'))
jet_map = {
    'TopHat': grb.jet.TopHat,
    'Gaussian': grb.jet.Gaussian,
    'PowerLawCore': grb.jet.PowerLawCore,
    'GaussianCore': grb.jet.GaussianCore,
    'Spherical': grb.jet.Spherical,
    'PowerLaw': grb.jet.PowerLaw
}

cax = plt.axes([0.8, 0.45, 0.15, 0.2])
check = CheckButtons(cax, list(bands.keys()), [True]*len(bands))

def update(val):
    for key, slider in sliders.items():
        if key == 'log10_E0':
            params['E0'] = 10 ** slider.val
        else:
            params[key] = slider.val
    plot_bands()

for slider in sliders.values():
    slider.on_changed(update)

def on_jet(label):
    params['jetType'] = jet_map[label]
    update(None)
radio.on_clicked(on_jet)

def on_check(label):
    update(None)
check.on_clicked(on_check)

resetax = plt.axes([0.8, 0.33, 0.1, 0.04])
button = Button(resetax, 'Reset', hovercolor='skyblue')
def reset(event):
    for key, slider in sliders.items():
        slider.reset()
    radio.set_active(0)
    for _, chk in enumerate(check.get_rectangles()):
        pass
    update(None)
button.on_clicked(reset)

plot_bands()
plt.show()
