import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, CheckButtons, Button
from astropy.cosmology import Planck15 as cosmo
import afterglowpy as grb

# ==========================
# Defaults
# ==========================
z = 0.661
dl = cosmo.luminosity_distance(z).to("cm").value

params_default = {
    "jetType": grb.jet.TopHat,
    "specType": grb.jet.SimpleSpec,
    "thetaObs": 0.05,
    "E0": 1e51,
    "thetaCore": 0.06,
    "n0": 1e-3,
    "p": 2.2,
    "epsilon_e": 0.1,
    "epsilon_B": 0.01,
    "xi_N": 1.0,
    "d_L": dl,
    "L0": 1e47,
    "q": 2.0,
    "ts": 5e4,
    "z": z,
}

freqs = {
    "i": 393170436721311.5,
    "z": 328215960148894.2,
    "r": 481130569731985.2,
    "J": 240000000000000.0,
    "g": 628495719077568.1,
    "R": 468671768303359.2,
    "radio(6GHz)": 6e9,
    "radio(10GHz)": 1e10,
    "radio(1.3GHz)": 1.3e9,
    "X-ray": 2.42e18
}

style_map = {
    "optical": "-",
    "xray": "--",
    "radio": ":"
}

# Assign bands to groups
band_group = {
    "i": "optical",
    "z": "optical",
    "r": "optical",
    "J": "optical",
    "g": "optical",
    "R": "optical",
    "X-ray": "xray",
    "radio(6GHz)": "radio",
    "radio(10GHz)": "radio",
    "radio(1.3GHz)": "radio"
}

time = np.logspace(1, 6, 30)

# ==========================
# Plot setup
# ==========================
fig, ax = plt.subplots(figsize=(8,6))
plt.subplots_adjust(left=0.35, right=0.95, bottom=0.35)
lines = {}  # store Line2D objects for each freq

# Initial plot
for band, nu in freqs.items():
    group = band_group[band]
    linestyle = style_map[group]
    flux = grb.fluxDensity(time, nu, **params_default)
    line, = ax.loglog(time, flux, linestyle=linestyle, label=band)
    lines[band] = line

ax.legend(fontsize=8)
ax.grid(True, which='both', ls='--', lw=0.3)

# ==========================
# Sliders (log where needed)
# ==========================
slider_defs = [
    ('log10_E0', 48, 55, np.log10(params_default['E0'])),
    ('thetaObs', 0.0, 0.8, params_default['thetaObs']),
    ('thetaCore', 0.001, 0.8, params_default['thetaCore']),
    ('log10_n0', -5, 3, np.log10(params_default['n0'])),
    ('p', 2.0, 3.0, params_default['p']),
    ('log10_eps_e', -3, -0.3, np.log10(params_default['epsilon_e'])),
    ('log10_eps_B', -6, -1, np.log10(params_default['epsilon_B'])),
    ('log10_L0', 45, 55, np.log10(params_default['L0'])),
    ('log10_ts', 2, 7, np.log10(params_default['ts']))
]

sliders = {}
for i, (label, vmin, vmax, vinit) in enumerate(slider_defs):
    ax_slider = plt.axes([0.35, 0.28 - i*0.025, 0.55, 0.015])
    sliders[label] = Slider(ax_slider, label, vmin, vmax, valinit=vinit, valstep=0.01)

# ==========================
# Radio Buttons
# ==========================
jet_options = {
    'TopHat': grb.jet.TopHat,
    'Cone': grb.jet.Cone,
    'Gaussian': grb.jet.Gaussian,
    'PowerLaw': grb.jet.PowerLaw,
    'GaussianCore': grb.jet.GaussianCore,
    'PowerLawCore': grb.jet.PowerLawCore,
    'Spherical': grb.jet.Spherical
}
ax_radio_jet = plt.axes([0.05, 0.6, 0.25, 0.25])
radio_jet = RadioButtons(ax_radio_jet, list(jet_options.keys()), active=0)

spec_options = {
    'SimpleSpec': grb.jet.SimpleSpec,
    'DeepNewtonian': grb.jet.DeepNewtonian,
    'EpsEBar': grb.jet.EpsEBar,
    'ICCooling': grb.jet.ICCooling
}
ax_radio_spec = plt.axes([0.05, 0.35, 0.25, 0.2])
radio_spec = RadioButtons(ax_radio_spec, list(spec_options.keys()), active=0)

# ==========================
# Frequency Check Buttons
# ==========================
freq_labels = list(freqs.keys())
visibility = [True]*len(freqs)
ax_check = plt.axes([0.05, 0.05, 0.25, 0.25])
check = CheckButtons(ax_check, freq_labels, visibility)

# ==========================
# Update function
# ==========================
def update(val):
    params = params_default.copy()
    params['jetType'] = jet_options[radio_jet.value_selected]
    params['specType'] = spec_options[radio_spec.value_selected]
    params['E0'] = 10**sliders['log10_E0'].val
    params['thetaObs'] = sliders['thetaObs'].val
    params['thetaCore'] = sliders['thetaCore'].val
    params['n0'] = 10**sliders['log10_n0'].val
    params['p'] = sliders['p'].val
    params['epsilon_e'] = 10**sliders['log10_eps_e'].val
    params['epsilon_B'] = 10**sliders['log10_eps_B'].val
    params['L0'] = 10**sliders['log10_L0'].val
    params['ts'] = 10**sliders['log10_ts'].val
    
    for band, nu in freqs.items():
        lines[band].set_ydata(grb.fluxDensity(time, nu, **params))
    
    ax.relim()
    ax.autoscale(axis='y')
    fig.canvas.draw_idle()

# Connect sliders & radios
for s in sliders.values():
    s.on_changed(update)
radio_jet.on_clicked(update)
radio_spec.on_clicked(update)

# Checkbox to toggle bands
def toggle_band(label):
    line = lines[label]
    line.set_visible(not line.get_visible())
    fig.canvas.draw_idle()
check.on_clicked(toggle_band)

# ==========================
# Reset button
# ==========================
ax_reset = plt.axes([0.8, 0.02, 0.1, 0.04])
btn_reset = Button(ax_reset, 'Reset')
def reset(event):
    for name, slider in sliders.items():
        slider.reset()
    radio_jet.set_active(0)
    radio_spec.set_active(0)
    for i, label in enumerate(freq_labels):
        if not lines[label].get_visible():
            lines[label].set_visible(True)
    fig.canvas.draw_idle()
btn_reset.on_clicked(reset)

plt.show()
