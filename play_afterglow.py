import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider, Button
import numpy as np
import afterglowpy as grb
from astropy.cosmology import Planck15 as cosmo
from matplotlib.gridspec import GridSpec

from growth_rewrite.basic_reduction.program_for_stacking import color
plt.rcParams['font.size'] = 14
plt.rcParams['text.color'] = 'black'

# --- Constants ---
z = 0.661
dL = cosmo.luminosity_distance(z).to("cm").value
t = np.geomspace(1e2, 1e6, 200)   # more points for smooth curve
nu_r = 4.811305697319852e14

# --- Initial dictionary ---
init_dict = {
    "jetType": grb.jet.TopHat,
    "specType": grb.jet.SimpleSpec,
    "thetaObs": 0.09,
    "E0": 10**52,
    "thetaCore": 0.05,
    "thetaWing": 0.2,
    "b": 6,
    "n0": 1e-2,
    "p": 2.2,
    "epsilon_e": 0.1,
    "epsilon_B": 1e-3,
    "xi_N": 1,
    "d_L": dL,
    "z": z,
    "L0": 1e47,
    "q": 2,
    "ts": 1e3,
}

# --- Sliders dictionary (log values where appropriate) ---
params_dict = {
    "logE0":   {"name": "E0",         "low": 47.0, "high": 56.0, "init": 52.0},
    "logn0":   {"name": "n0",         "low": -4.0, "high": 3.0,  "init": -2.0},
    "logeps_B":{"name": "epsilon_B", "low": -6.0, "high": -1.0, "init": -3.0},
    "logeps_e":{"name": "epsilon_e", "low": -4.0, "high": 0.0,  "init": -1.0},
    "thc":     {"name": "thetaCore", "low": 1e-4, "high": 0.3,  "init": 0.05},
    "thv":     {"name": "thetaObs",  "low": 0.0,  "high": 0.3,  "init": 0.09},
    "thw":     {"name": "thetaWing", "low": 1e-2, "high": 0.4,  "init": 0.2},
    "p":       {"name": "p",         "low": 2.001,"high": 3.0,  "init": 2.2},
    "b":       {"name": "b",         "low": 2.0,  "high": 7.0,  "init": 6.0},
    "logl0":   {"name": "L0",        "low": 43.0, "high": 51.0, "init": 47.0},
    "logts":   {"name": "ts",        "low": 2.0,  "high": 6.0,  "init": 3.0},
}

# --- Create figure with GridSpec ---
fig = plt.figure(figsize=(12, 8))
gs = GridSpec(3, 3, figure=fig, width_ratios=[1, 0.85, 0.85], height_ratios=[4, 0.4, 0.4])

# Create axes using GridSpec
ax_sliders = fig.add_subplot(gs[:, 0])    # Left column, all rows
ax_plot = fig.add_subplot(gs[0, 1:])      # Top right, spans columns 1-2
ax_jet = fig.add_subplot(gs[1:, 1])        # Middle right, column 1
ax_energy = fig.add_subplot(gs[1:, 2])     # Middle right, column 2
ax_sliders.axis('off')
# ax_jet.axis('off')
# ax_energy.axis('off')
# Adjust layout
plt.subplots_adjust(left=0.1, right=0.95, bottom=0.05, top=0.95, wspace=0.3, hspace=0.4)

# --- Plot setup ---
Fnu = grb.fluxDensity(t, nu_r, **init_dict)
(line,) = ax_plot.loglog(t, Fnu, lw=2)
ax_plot.set_title("Main Plot (updates with controls)")
ax_plot.grid(True, which='both', ls='--', lw=0.3)
ax_plot.set_xlabel("time (s)")
ax_plot.set_ylabel("flux (mJy)")

# --- Make radio buttons for energy injection ---
radio_energy = RadioButtons(ax_energy, ("Enable", "Disable"))
ax_energy.set_title("Energy Injection", fontsize=16, color = 'C0')

# --- Make radio buttons for jet Type ---
radio_jet = RadioButtons(ax_jet, ("TopHat", "Gaussian", "PowerLaw"))
ax_jet.set_title("JetType", fontsize=16, color = 'C1')

# Increase font size for all radio button labels
for label in radio_energy.labels:
    label.set_fontsize(14)
    label.set_color('black')

for label in radio_jet.labels:
    label.set_fontsize(14)
    label.set_color('black')

# --- Make sliders ---
sliders = {}
for i, (key, info) in enumerate(params_dict.items()):
    ypos = 0.90 - 0.08 * i
    ax_slider = fig.add_axes([0.075, ypos, 0.25, 0.03])
    sliders[key] = Slider(
        ax=ax_slider,
        label=key,
        valmin=info["low"],
        valmax=info["high"],
        valinit=info["init"],
    )

energy_enabled = True
current_jet = grb.jet.TopHat

# --- Update function ---
def update(val = None):
    global energy_enabled, current_jet
    new_params = init_dict.copy()

    # Log-scale parameters
    new_params["E0"]        = 10**sliders["logE0"].val
    new_params["n0"]        = 10**sliders["logn0"].val
    new_params["epsilon_B"] = 10**sliders["logeps_B"].val
    new_params["epsilon_e"] = 10**sliders["logeps_e"].val
    new_params["ts"]        = 10**sliders["logts"].val

    # Linear parameters
    new_params["thetaCore"] = sliders["thc"].val
    new_params["thetaObs"]  = sliders["thv"].val
    new_params["thetaWing"] = sliders["thw"].val
    new_params["p"]         = sliders["p"].val
    new_params["b"]         = sliders["b"].val
    
    if energy_enabled:
        new_params["L0"] = 10**sliders["logl0"].val
    else:
        new_params["L0"] = 0.0
        
    new_params["jetType"] = current_jet

    # Recompute and update plot
    line.set_ydata(grb.fluxDensity(t, nu_r, **new_params))
    ax_plot.relim()
    ax_plot.autoscale_view(scaley=True)
    fig.canvas.draw_idle()

# Connect all sliders to update
for s in sliders.values():
    s.on_changed(update)

def energy_callback(label):
    global energy_enabled
    energy_enabled = (label == "Enable")
    update()
    
def jet_callback(label):
    global current_jet
    if label == "TopHat":
        current_jet = grb.jet.TopHat
    elif label == "Gaussian":
        current_jet = grb.jet.Gaussian
    elif label == "PowerLaw":
        current_jet = grb.jet.PowerLaw
    update()

radio_energy.on_clicked(energy_callback)
radio_jet.on_clicked(jet_callback)

# --- Reset button ---
resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, "Reset", color="gold", hovercolor="skyblue")

def resetSlider(event):
    for s in sliders.values():
        s.reset()
    update()

button.on_clicked(resetSlider)

plt.show()