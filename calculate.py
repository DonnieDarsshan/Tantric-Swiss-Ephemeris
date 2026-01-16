# =========================================================
# OFFLINE SWISS EPHEMERIS – TANTRIC DARK MODE (FINAL STABLE)
# =========================================================
import os, json, re
import sys

import swisseph as swe
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def get_ephe_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ephe")

import sys
EPHE_PATH = get_ephe_path()

SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")





# -------------------------------------------------
# AYANAMSHA (SAFE – VERSION COMPATIBLE & FUTURE PROOF)
# -------------------------------------------------
AYANAMSHA_MAP = {
    "Lahiri": swe.SIDM_LAHIRI,
    "KP New": swe.SIDM_KRISHNAMURTI,
    "Raman": swe.SIDM_RAMAN
}

# --- Optional / Less common but REAL Swiss Ephemeris ayanamshas ---

if hasattr(swe, "SIDM_YUKTESHWAR"):
    AYANAMSHA_MAP["Yukteshwar"] = swe.SIDM_YUKTESHWAR

if hasattr(swe, "SIDM_TRUE_REVATI"):
    AYANAMSHA_MAP["True Revati"] = swe.SIDM_TRUE_REVATI

if hasattr(swe, "SIDM_USHASHASHI"):
    AYANAMSHA_MAP["Usha–Shashi"] = swe.SIDM_USHASHASHI







# -------------------------------------------------
# SWISS EPHEMERIS
# -------------------------------------------------
swe.set_ephe_path(EPHE_PATH)
FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

PLANETS = {
    "Surya": swe.SUN,
    "Chandra": swe.MOON,
    "Mangala": swe.MARS,
    "Budha": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Rahu_true": swe.TRUE_NODE,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO

}


# -------------------------------------------------
# SETTINGS
# -------------------------------------------------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            return json.load(open(SETTINGS_FILE, "r", encoding="utf-8"))
        except:
            pass
    return {"output_dir": ""}

def save_settings():
    json.dump(settings, open(SETTINGS_FILE, "w", encoding="utf-8"), indent=2)

settings = load_settings()





# -------------------------------------------------
# SAFE AUTO-JUMP (SHIFT+TAB SAFE)
# -------------------------------------------------
_last_len = {}

def jump_if_complete(var, widget, size, key):
    cur = var.get()
    prev = _last_len.get(key, 0)
    _last_len[key] = len(cur)
    if cur.isdigit() and len(cur) == size and prev < size:
        widget.focus()


def smart_day_month_jump(event, var, next_widget):
    # Do not auto-jump when Shift+Tab is used
    if event.state & 0x1:
        return

    val = var.get()
    if not val.isdigit():
        return

    if len(val) == 1 and val[0] in "456789":
        next_widget.focus()
    elif len(val) >= 2:
        next_widget.focus()


def smart_month_jump(event, var, next_widget):
    # Do not interfere with Shift+Tab
    if event.state & 0x1:
        return

    val = var.get()
    if not val.isdigit():
        return

    # Month rules:
    # 0 → wait (01–09)
    # 1 → wait (10–12)
    # 2–9 → jump immediately
    if len(val) == 1:
        if val[0] in "23456789":
            next_widget.focus()
    elif len(val) >= 2:
        next_widget.focus()


def smart_hour_jump(event, var, next_widget):
    if event.state & 0x1:
        return

    val = var.get()
    if not val.isdigit():
        return

    if len(val) == 1 and val[0] in "3456789":
        next_widget.focus()
    elif len(val) >= 2:
        next_widget.focus()












def smart_minute_jump(event, var, next_widget):
    if event.state & 0x1:
        return

    val = var.get()
    if not val.isdigit():
        return

    if len(val) == 1 and val[0] in "6789":
        next_widget.focus()
    elif len(val) >= 2:
        next_widget.focus()

	
	
	
	
	
	
	
	
	


# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def sanitize_filename(name):
    return re.sub(r"[^\w]+", "_", name.strip()) or "kundali"

def choose_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        settings["output_dir"] = folder
        save_settings()
        out_label.config(text=f"Output folder: {folder}")


def open_output_folder():
    folder = settings.get("output_dir")
    if not folder or not os.path.isdir(folder):
        messagebox.showwarning("Output Folder", "Output folder is not set or does not exist.")
        return
    os.startfile(folder)
















# -------------------------------------------------
# AYANAMSHA CHECKBOX CONTROL
# -------------------------------------------------
def select_ayanamsha(name):
    for k in ayan_vars:
        ayan_vars[k].set(1 if k == name else 0)

def get_ayanamsha():
    for k in ayan_vars:
        if ayan_vars[k].get():
            return k
    return "Lahiri"

# -------------------------------------------------
# CALCULATION
# -------------------------------------------------


def calculate_all_ayanamshas(jd, lat, lon):
    results = {}

    for name, sid_mode in AYANAMSHA_MAP.items():
        swe.set_sid_mode(sid_mode)
        ayan = swe.get_ayanamsa(jd)

        planets = {}

        rahu_mean = swe.calc_ut(jd, swe.MEAN_NODE, FLAGS)[0][0] % 360
        rahu_true = swe.calc_ut(jd, swe.TRUE_NODE, FLAGS)[0][0] % 360

        planets["Rahu"] = rahu_mean
        planets["Rahu_true"] = rahu_true
        planets["Ketu"] = (rahu_mean + 180) % 360
        planets["Ketu_true"] = (rahu_true + 180) % 360

        for p, code in PLANETS.items():
            planets[p] = swe.calc_ut(jd, code, FLAGS)[0][0] % 360

        houses, _ = swe.houses(jd, lat, lon, b'P')

        cusps = {}
        for i in range(12):
            cusps[str(i + 1)] = (houses[i] - ayan) % 360

        results[name] = {
            "ayanamsha_value": ayan,
            "lagna": cusps["1"],
            "planets": planets,
            "cusps": cusps
        }

    return results




def calculate_sayana(jd, lat, lon):
    planets = {}

    for p, code in PLANETS.items():
        planets[p] = swe.calc_ut(jd, code, swe.FLG_SWIEPH)[0][0] % 360

    houses, _ = swe.houses(jd, lat, lon, b'P')
    cusps = {str(i + 1): houses[i] % 360 for i in range(12)}

    return {
        "ayanamsha_value": 0.0,
        "lagna": cusps["1"],
        "planets": planets,
        "cusps": cusps
    }







def calculate_and_save():
    try:
        if not name_var.get().strip():
            raise ValueError("Enter person name")

        if not settings.get("output_dir"):
            folder = filedialog.askdirectory()
            if not folder:
                return
            settings["output_dir"] = folder
            save_settings()
            out_label.config(text=f"Output folder:\n{folder}")

        filename = sanitize_filename(name_var.get()) + ".json"
        save_path = os.path.join(settings["output_dir"], filename)

        dt = datetime(
            int(yyyy_var.get()), int(mm_var.get()), int(dd_var.get()),
            int(hh_var.get()), int(min_var.get()), int(sec_var.get())
        )

        sign = -1 if tz_sign.get() == "-" else 1
        offset = sign * (int(tz_h.get()) * 60 + int(tz_m.get()))
        offset += int(dst_var.get()) * 60
        utc = dt - timedelta(minutes=offset)

        jd = swe.julday(
            utc.year, utc.month, utc.day,
            utc.hour + utc.minute / 60 + utc.second / 3600
        )

        # GOOGLE MAPS FORMAT LATITUDE
        lat = float(f"{lat_deg.get()}.{lat_frac.get() or '0'}")
        if lat_sign.get() == "-":
            lat = -lat

        # GOOGLE MAPS FORMAT LONGITUDE
        lon = float(f"{lon_deg.get()}.{lon_frac.get() or '0'}")
        if lon_sign.get() == "-":
            lon = -lon





        ayanamsha_results = calculate_all_ayanamshas(jd, lat, lon)
        ayanamsha_results["Sayana"] = calculate_sayana(jd, lat, lon)

        data = {
            "meta": {
                "name": name_var.get().strip(),
                "latitude": lat,
                "longitude": lon,
                "datetime_utc": utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            },

            "ayanamsha": "Lahiri",
            "lagna": ayanamsha_results["Lahiri"]["lagna"],
            "planets": ayanamsha_results["Lahiri"]["planets"],
            "cusps": ayanamsha_results["Lahiri"]["cusps"],

            "ayanamshas": ayanamsha_results
        }

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        messagebox.showerror("Error", str(e))

        
        



def clear_basic_fields():
    name_var.set("")
    dd_var.set("")
    mm_var.set("")
    yyyy_var.set("")
    hh_var.set("")
    min_var.set("")
    sec_var.set("00")
    e_name.focus()




# -------------------------------------------------
# UI – FINAL FIXED SCALE & FONTS
# -------------------------------------------------
root = tk.Tk()
root.title("Offline Swiss Ephemeris")
root.geometry("820x780")
root.configure(bg="#120404")
root.resizable(True, True)

# ✅ MODERATE scaling (not extreme)
root.tk.call("tk", "scaling", 1.15)

style = ttk.Style(root)
style.theme_use("clam")

# ✅ ONE UNIFORM FONT FOR EVERYTHING
APP_FONT = ("Segoe UI Semibold", 15)
# 🔥 FORCE SAME FONT INSIDE ENTRY BOXES (CRITICAL FIX)
root.option_add("*Font", APP_FONT)

TITLE_FONT = ("Segoe UI Semibold", 20)

style.configure(".", background="#120404", foreground="#f5eaea", font=APP_FONT)
style.configure("TEntry", fieldbackground="#1a0606", foreground="#f5eaea", insertcolor="#ff4d4d", font=APP_FONT)
style.configure("TButton", background="#5c0a0a", foreground="#ffecec", padding=8, font=APP_FONT)
style.map("TButton", background=[("active", "#8b0f0f")])
style.configure("TLabel", background="#120404", foreground="#f5eaea", font=APP_FONT)
style.configure("TCheckbutton", background="#120404", foreground="#f5eaea", font=APP_FONT)
style.configure("TSeparator", background="#5c0a0a")





# -------------------------------------------------
# MAIN 2-COLUMN LAYOUT (LEFT = INPUTS, RIGHT = ACTIONS)
# -------------------------------------------------
main_frame = ttk.Frame(root, padding=16)
main_frame.pack(fill="both", expand=True)

left_frame = ttk.Frame(main_frame)
right_frame = ttk.Frame(main_frame)

left_frame.pack(side="left", fill="both", expand=True, padx=(0,12))
right_frame.pack(side="right", fill="y", padx=(12,0))

# -------------------------------------------------
# COMPATIBILITY ALIAS (DO NOT REMOVE)
# -------------------------------------------------
# This makes all existing ttk.Label(frame, ...)
# ttk.Entry(frame, ...) etc work without changes
frame = left_frame










# VARIABLES
name_var = tk.StringVar()

# DATE
dd_var = tk.StringVar()
mm_var = tk.StringVar()
yyyy_var = tk.StringVar()

# TIME
hh_var = tk.StringVar()
min_var = tk.StringVar()
sec_var = tk.StringVar(value="00")



# GOOGLE MAPS FRIENDLY LATITUDE
# Default: +13.318833 (HOME LOCATION)
lat_sign = tk.StringVar(value="+")
lat_deg  = tk.StringVar(value="13")
lat_frac = tk.StringVar(value="318833")

# GOOGLE MAPS FRIENDLY LONGITUDE
# Default: +77.132609 (HOME LOCATION)
lon_sign = tk.StringVar(value="+")
lon_deg  = tk.StringVar(value="77")
lon_frac = tk.StringVar(value="132609")






# TIME ZONE
tz_sign = tk.StringVar(value="+")
tz_h = tk.StringVar(value="05")
tz_m = tk.StringVar(value="30")
dst_var = tk.StringVar(value="0")










ayan_vars = {
    "Lahiri": tk.IntVar(value=1),
    "KP New": tk.IntVar(value=0),
    "Raman": tk.IntVar(value=0)
}

# HEADER
ttk.Label(left_frame, text="OFFLINE SWISS EPHEMERIS", font=TITLE_FONT).pack(pady=8)


# NAME
# NAME
ttk.Label(left_frame, text="NAME").pack(anchor="w")
e_name = ttk.Entry(left_frame, textvariable=name_var)

def force_uppercase_name(*args):
    name_var.set(name_var.get().upper())

name_var.trace_add("write", force_uppercase_name)

e_name.pack(fill="x", pady=4)

# AUTO FOCUS ON APP START
root.after(200, lambda: e_name.focus())

# ENTER → JUMP TO DATE (DD)
def focus_dd(event=None):
    e_dd.focus()

e_name.bind("<Return>", focus_dd)





# DATE
ttk.Label(frame, text="Date (DD  MM  YYYY)").pack(anchor="w", pady=(10,4))
df = ttk.Frame(frame); df.pack(anchor="w")
e_dd = ttk.Entry(df, width=6, textvariable=dd_var)
e_mm = ttk.Entry(df, width=6, textvariable=mm_var)
e_yy = ttk.Entry(df, width=10, textvariable=yyyy_var)
e_dd.pack(side="left", padx=4)
e_mm.pack(side="left", padx=4)
e_yy.pack(side="left", padx=4)






# TIME
ttk.Label(frame, text="Time (HH  MM  SS)").pack(anchor="w", pady=(10,4))
tf = ttk.Frame(frame); tf.pack(anchor="w")
e_hh = ttk.Entry(tf, width=6, textvariable=hh_var)
e_mn = ttk.Entry(tf, width=6, textvariable=min_var)
e_sc = ttk.Entry(tf, width=6, textvariable=sec_var)
e_hh.pack(side="left", padx=4)
e_mn.pack(side="left", padx=4)
e_sc.pack(side="left", padx=4)



# -------------------------------
# SAFE KEY BINDINGS (AFTER WIDGET CREATION)
# -------------------------------
e_dd.bind("<KeyRelease>", lambda e: smart_day_month_jump(e, dd_var, e_mm))
e_mm.bind("<KeyRelease>", lambda e: smart_month_jump(e, mm_var, e_yy))
e_yy.bind("<KeyRelease>", lambda e: jump_if_complete(yyyy_var, e_hh, 4, "yy"))

e_hh.bind("<KeyRelease>", lambda e: smart_hour_jump(e, hh_var, e_mn))
e_mn.bind("<KeyRelease>", lambda e: smart_minute_jump(e, min_var, e_lat_deg))




# UTC OFFSET
ttk.Label(frame, text="UTC Offset (+ / −  HH  MM  DST)").pack(anchor="w", pady=(10,4))
uf = ttk.Frame(frame); uf.pack(anchor="w")
ttk.Entry(uf, width=4, textvariable=tz_sign).pack(side="left", padx=4)
ttk.Entry(uf, width=6, textvariable=tz_h).pack(side="left", padx=4)
ttk.Entry(uf, width=6, textvariable=tz_m).pack(side="left", padx=4)
ttk.Label(uf, text="DST").pack(side="left", padx=6)
ttk.Entry(uf, width=6, textvariable=dst_var).pack(side="left")










# -------------------------------------------------
# LATITUDE / LONGITUDE — GOOGLE MAPS FORMAT
# (+ / −  DEG  FRACTION)
# Example:
# + | 13 | 318833  → 13.318833
# - | 77 | 13      → -77.13
# -------------------------------------------------

# LATITUDE
ttk.Label(frame, text="Latitude (+ / −   Deg   Fraction)").pack(anchor="w", pady=(10,4))
lf = ttk.Frame(frame); lf.pack(anchor="w")

e_lat_sign = ttk.Entry(lf, width=4, textvariable=lat_sign, justify="center")
e_lat_deg  = ttk.Entry(lf, width=8, textvariable=lat_deg)
e_lat_frac = ttk.Entry(lf, width=12, textvariable=lat_frac)

e_lat_sign.pack(side="left", padx=4)
e_lat_deg.pack(side="left", padx=4)
e_lat_frac.pack(side="left", padx=4)


# LONGITUDE
ttk.Label(frame, text="Longitude (+ / −   Deg   Fraction)").pack(anchor="w", pady=(10,4))
lof = ttk.Frame(frame); lof.pack(anchor="w")

e_lon_sign = ttk.Entry(lof, width=4, textvariable=lon_sign, justify="center")
e_lon_deg  = ttk.Entry(lof, width=8, textvariable=lon_deg)
e_lon_frac = ttk.Entry(lof, width=12, textvariable=lon_frac)

e_lon_sign.pack(side="left", padx=4)
e_lon_deg.pack(side="left", padx=4)
e_lon_frac.pack(side="left", padx=4)





















# -------------------------------------------------
# RIGHT PANEL – ACTIONS (ALWAYS VISIBLE)
# -------------------------------------------------
ttk.Label(
    right_frame,
    text="Actions",
    font=("Segoe UI Semibold", 18)
).pack(pady=(4,16))

ttk.Button(
    right_frame,
    text="Set Output Folder",
    command=choose_output_folder,
    width=22
).pack(pady=8)

out_label = ttk.Label(
    right_frame,
    text=f"Output folder:\n{settings['output_dir'] or 'Not set'}",
    wraplength=260,
    justify="left"
)
out_label.pack(pady=8)

ttk.Separator(right_frame).pack(fill="x", pady=14)


ttk.Button(
    right_frame,
    text="Calculate & Save",
    command=calculate_and_save,
    width=22
).pack(pady=12)




ttk.Button(
    right_frame,
    text="Clear Name / Date / Time",
    command=clear_basic_fields,
    width=22
).pack(pady=10)
    


ttk.Button(
    right_frame,
    text="Open Output Folder",
    command=open_output_folder,
    width=22
).pack(pady=6)




root.mainloop()




