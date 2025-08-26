import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider
import numpy as np
import afterglowpy as grb
from astropy.cosmology import Planck15 as cosmo

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

# --- Plot setup ---
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.35, left=0.45)
Fnu = grb.fluxDensity(t, nu_r, **init_dict)
l, = ax.loglog(t, Fnu, color='k')
ax.grid(True, which='both', ls='--', lw=0.3)
ax.set_xlabel("time (s)")
ax.set_ylabel("flux (mJy)")

# --- Make sliders ---
sliders = {}
for i, (key, info) in enumerate(params_dict.items()):
    ypos = 0.95 - 0.07 * i
    ax_slider = plt.axes([0.05, ypos, 0.30, 0.03])
    sliders[key] = Slider(
        ax=ax_slider,
        label=key,
        valmin=info["low"],
        valmax=info["high"],
        valinit=info["init"],
    )

# --- Update function ---
def update(val):
    new_params = init_dict.copy()

    # Log-scale parameters
    new_params["E0"]        = 10**sliders["logE0"].val
    new_params["n0"]        = 10**sliders["logn0"].val
    new_params["epsilon_B"] = 10**sliders["logeps_B"].val
    new_params["epsilon_e"] = 10**sliders["logeps_e"].val
    new_params["L0"]        = 10**sliders["logl0"].val
    new_params["ts"]        = 10**sliders["logts"].val

    # Linear parameters
    new_params["thetaCore"] = sliders["thc"].val
    new_params["thetaObs"]  = sliders["thv"].val
    new_params["thetaWing"] = sliders["thw"].val
    new_params["p"]         = sliders["p"].val
    new_params["b"]         = sliders["b"].val

    # Recompute and update plot
    l.set_ydata(grb.fluxDensity(t, nu_r, **new_params))
    ax.relim()
    ax.autoscale_view(scaley=True)
    fig.canvas.draw_idle()

# Connect all sliders to update
for s in sliders.values():
    s.on_changed(update)

# --- Reset button ---
resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, "Reset", color="gold", hovercolor="skyblue")

def resetSlider(event):
    for s in sliders.values():
        s.reset()
button.on_clicked(resetSlider)

plt.show()