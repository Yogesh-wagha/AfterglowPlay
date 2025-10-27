import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, Button, CheckButtons
import numpy as np
import afterglowpy as grb
from astropy.cosmology import Planck15 as cosmo
import matplotlib.gridspec as gridspec

plt.rcParams['font.size'] = 13
plt.rcParams['text.color'] = 'black'

# --- Constants ---
z = 0.661
dL = cosmo.luminosity_distance(z).to("cm").value
t = np.geomspace(1e2, 1e6, 200)
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

params_dict = {
    "logE0": {"name": "E0", "low": 47.0, "high": 56.0, "init": 52.0, "label": r'$\log(E_0)$'},
    "logn0": {"name": "n0", "low": -4.0, "high": 3.0, "init": -2.0, "label": r'$\log(n_0)$'},
    "logeps_B":{"name": "epsilon_B","low": -6.0,"high": -1.0,"init": -3.0, "label": r'$\log(\epsilon_B)$'},
    "logeps_e":{"name": "epsilon_e","low": -4.0,"high": 0.0,"init": -1.0, "label": r'$\log(\epsilon_e)$'},
    "thc":   {"name": "thetaCore","low": 1e-4,"high": 0.3,"init": 0.05, "label": r'$\theta_c$'},
    "thv":   {"name": "thetaObs","low": 0.0,"high": 0.3,"init": 0.09, "label": r'$\theta_v$'},
    "thw":   {"name": "thetaWing","low": 1e-2,"high": 0.4,"init": 0.2, "label": r'$\theta_w$'},
    "p":     {"name": "p","low": 2.001,"high": 3.0,"init": 2.2, "label": r'$p$'},
    "b":     {"name": "b","low": 2.0,"high": 7.0,"init": 6.0, "label": r'$b$'},
    "logl0": {"name": "L0","low": 43.0,"high": 51.0,"init": 47.0, "label": r'$\log(L_0)$'},
    "logts": {"name": "ts","low": 2.0,"high": 6.0,"init": 3.0, "label": r'$\log(t_s)$'},
}
fig = plt.figure(figsize=(12, 7))
gs = gridspec.GridSpec(
    3, 5,
    height_ratios=[6.5, 2.2, 0.7],  # first row big, last row very small
    width_ratios=[4, 1.5, 1.5, 1.5, 1.5],
    wspace=0.3,
    hspace=0.47,
    figure=fig
)

# --- Slider panel inside GridSpec cell ---
ax_slider_panel = fig.add_subplot(gs[0, 0])
ax_slider_panel.axis("off")
sliders = {}

# Instead of figure-wide coordinates, use panel-relative coords
slider_y_start = 0.95
slider_spacing = 0.1
for i, (key, info) in enumerate(params_dict.items()):
    # place slider inside ax_slider_panel coordinate system
    ax_slider = ax_slider_panel.inset_axes([0.1, slider_y_start - i*slider_spacing, 
                                            0.55, 0.05])  
    sliders[key] = Slider(ax=ax_slider, label=info["label"],
                        valmin=info["low"], valmax=info["high"], valinit=info["init"])

# --- Plot area ---
ax_plot = fig.add_subplot(gs[0, 1:])
Fnu = grb.fluxDensity(t, nu_r, **init_dict)
(line,) = ax_plot.loglog(t, Fnu, lw=2)
ax_plot.set_title("GRB Afterglow Model", fontsize=16, pad=10)
ax_plot.set_xlabel("time (s)", labelpad=8)
ax_plot.set_ylabel("flux (mJy)", labelpad=8)
ax_plot.grid(True, which='both', ls='--', lw=0.3)

# --- Filters ---
ax_check = fig.add_subplot(gs[1, 0])
ax_check.set_title("Filters", fontsize=13, pad=5)
check = CheckButtons(ax_check, ["u", "g", "r", "i", "z"], [True]*5)

# --- Radio buttons ---
radio_titles = ["Jet Type", "Energy", "q_value", "Spread"]
radio_options = [
    ("TopHat", "Gaussian", "PowerLaw"),
    ("Enable", "Disable"),
    ("q=0", "q=1", "q=2"),
    ("True", "False")
]
radio_widgets = []
for i, (title, opts) in enumerate(zip(radio_titles, radio_options), start=1):
    ax_r = fig.add_subplot(gs[1, i])
    ax_r.set_title(title, fontsize=13, pad=5)
    radio_widgets.append(RadioButtons(ax_r, opts))

radio_jet, radio_energy, radio_q, radio_spread = radio_widgets

# --- Reset button inside its own grid cell ---
ax_reset = fig.add_subplot(gs[2, :])
ax_reset.axis("off")
# Button fills almost entire row height, well centered
reset_button_ax = ax_reset.inset_axes([0.45, 0.15, 0.1, 0.7])
button = Button(reset_button_ax, "Reset", color="gold", hovercolor="skyblue")


# --- Interactivity ---
energy_enabled = True
current_jet = grb.jet.TopHat
q_val = 2
spread_enabled = True

def update(val=None):
    global energy_enabled, current_jet, q_val, spread_enabled
    new_params = init_dict.copy()
    new_params["E0"] = 10**sliders["logE0"].val
    new_params["n0"] = 10**sliders["logn0"].val
    new_params["epsilon_B"] = 10**sliders["logeps_B"].val
    new_params["epsilon_e"] = 10**sliders["logeps_e"].val
    new_params["ts"] = 10**sliders["logts"].val
    new_params["thetaCore"] = sliders["thc"].val
    new_params["thetaObs"] = sliders["thv"].val
    new_params["thetaWing"] = sliders["thw"].val
    new_params["p"] = sliders["p"].val
    new_params["b"] = sliders["b"].val
    new_params["L0"] = 10**sliders["logl0"].val if energy_enabled else 0.0
    new_params["jetType"] = current_jet
    new_params["q"] = q_val
    new_params["spread"] = spread_enabled
    line.set_ydata(grb.fluxDensity(t, nu_r, **new_params))
    ax_plot.relim()
    ax_plot.autoscale_view(scaley=True)
    fig.canvas.draw_idle()

for s in sliders.values():
    s.on_changed(update)

def energy_callback(label):
    global energy_enabled
    energy_enabled = (label == "Enable")
    update()

def jet_callback(label):
    global current_jet
    current_jet = {"TopHat": grb.jet.TopHat,
                "Gaussian": grb.jet.Gaussian,
                "PowerLaw": grb.jet.PowerLaw}[label]
    update()

def q_callback(label):
    global q_val
    # Parse q from label, like "q=2" -> 2
    q_val = int(label.split('=')[1])
    update()

def spread_callback(label):
    global spread_enabled
    # Parse boolean from label
    spread_enabled = (label == "True")
    update()


radio_energy.on_clicked(energy_callback)
radio_jet.on_clicked(jet_callback)
radio_q.on_clicked(q_callback)
radio_spread.on_clicked(spread_callback)

def resetSliders(event):
    for s in sliders.values():
        s.reset()
    update()

button.on_clicked(resetSliders)

plt.subplots_adjust(left=0.07, right=0.98, bottom=0.02, top=0.93)
plt.show()