# -*- coding: utf-8 -*-
from pynput.keyboard import Key, KeyCode, Listener as KListener
from pynput.mouse import Listener as MListener
import time
import tkinter as tk
from simpleaudio import WaveObject
from classes import Graph

width = 460
height = 300

holding_mouse = False


""" -------------------------  GUI Actions  --------------------------------"""

def on_click_hover(e):
    global holding_mouse
    x = Fenetre.winfo_pointerx() - hover_apm.winfo_width() // 2
    y = Fenetre.winfo_pointery() - hover_apm.winfo_height() // 2
    hover_apm.geometry("+{}+{}".format(x, y))
    if holding_mouse:
        hover_apm.after(10, lambda: on_click_hover(0))


def create_hover_apm():
    global hover_apm
    hover_apm = tk.Toplevel()
    w = hover_apm.winfo_screenwidth()
    h = hover_apm.winfo_screenheight()
    text = tk.Label(hover_apm, textvariable=var_cur, fg="white",
             bg="dark grey", font="Arial 10 bold")
    hover_apm.geometry("+{}+{}".format(w//2, 3*h//50))
    text.pack(fill=tk.BOTH, expand=True)
    hover_apm.bind('<Button-1>', on_click_hover)
    hover_apm.overrideredirect(True)


def destroy_hover_apm():
    global hover_apm
    hover_apm.destroy()
    hover_apm = None


def toggle_hover_apm():
    global hover_active
    if not hover_active:
        create_hover_apm()
    else:
        destroy_hover_apm()
    hover_active = not hover_active


def reset_button_callback():
    graph.reset()
    WaveObject.from_wave_file("reset.wav").play()


def create_reset_button():
    global reset_button_f
    reset_button_f = tk.Frame(Fenetre, width=width//3, height=height//11)
    reset_button_f.pack_propagate(0)  # don't shrink
    reset_button_f.place(x=0, y=height//8)
    reset_button = tk.Button(reset_button_f, text="Reset", fg="white",
                          command=reset_button_callback, background="#306030",
                          activebackground="#306030", activeforeground="white",
                          font="Arial 16")
    reset_button.pack(fill="both", expand=1)


def destroy_reset_button():
    global reset_button_f
    global stats_under_button
    slaves = reset_button_f.pack_slaves()
    for s in slaves:
        s.destroy()
    reset_button_f.destroy()


def main_button_callback():
    global tracking
    if not tracking:
        # delete_reset_button()
        main_button.config(text="Stop")
        main_button.config(background="#A02020", activebackground="#A02020")
        if reset_button_f is not None:
            destroy_reset_button()
        graph.play()
        WaveObject.from_wave_file("start_tracking.wav").play()
    else:
        main_button.config(text="Start Tracking")
        main_button.config(background="#3030D0", activebackground="#3030D0")
        graph.pause()
        create_reset_button()
        WaveObject.from_wave_file("stop_tracking.wav").play()

    tracking = not tracking
    update_stats()


""" -------------------------- Tracking APM --------------------------------"""

tracking = False
clicks = 0
keypresses = 0
max_apm = 0
avg_apm = 0
active_time = 0
key_history = []


def on_press(key):
    if key not in key_history:
        key_history.append(key)
        if Key.ctrl in key_history \
        or Key.ctrl_l in key_history \
        or Key.ctrl_r in key_history:
            if Key.enter in key_history:
                main_button_callback()
            if Key.backspace in key_history:
                if not tracking:
                    reset_button_callback()
            if KeyCode.from_char('*') in key_history:
                toggle_hover_apm()
        if tracking:
            graph.keypresses += 1
            graph.add_action(time.time())


def on_release(key):
    if key in key_history:
        key_history.remove(key)


def on_click(x, y, button, pressed):
    global holding_mouse
    if tracking and pressed:
        graph.clicks += 1
        graph.add_action(time.time())

    if pressed:
        holding_mouse = True
    else:
        holding_mouse = False

klistener = KListener(on_press=on_press, on_release=on_release)
mlistener = MListener(on_click=on_click)
klistener.start()
mlistener.start()


""" ----------------------  Building GUI layout  ---------------------------"""

# Initializing Window
Fenetre = tk.Tk()
Fenetre.geometry("{}x{}".format(width, height))
Fenetre.title("APM_tool v1.0")
Fenetre.config(background="black")

# Main button that toggles apm tracking
main_button_f = tk.Frame(Fenetre, width=width//3, height=height//8)
main_button_f.pack_propagate(0) # don't shrink
main_button_f.place(x=0, y=0)
main_button = tk.Button(main_button_f, text="Start Tracking", fg="white",
                          command=main_button_callback, background="#3030B0",
                          activebackground="#3030B0", activeforeground="white",
                          font="Arial 16")
main_button.pack(fill="both", expand=1)

# Reset Button (not apparent yet)
reset_button_f = None

# Hover apm (not enabled yet)
hover_active = False
hover_apm = None

# Top-right corner stats
stats = tk.Frame(Fenetre, width=2*width//3, height=height//4,
                 bg="black")
stats_left = tk.Frame(stats, width=width//3, height=height//4,
                 bg="black")
stats_right = tk.Frame(stats, width=width//3, height=height//4,
                 bg="black")
stats_under_button = tk.Frame(Fenetre, width=width//3, height=height//4,
                 bg="black")

stats.place(x=width//3, y=0)
stats_left.place(x=0, y=0)
stats_right.place(x=width//3, y=0)
stats_under_button.place(x=0, y=height//8)

var_cur = tk.StringVar()
var_max = tk.StringVar()
var_avg = tk.StringVar()
var_active = tk.StringVar()
var_kc = tk.StringVar()

var_cur.set("Current : 0 APM")
var_max.set("Max : 0 APM")
var_avg.set("Avg : 0 APM")
var_active.set("Active Time : 0 %")
var_kc.set("Keypresses :  0 %")

cur_apm_label = tk.Label(stats_under_button, textvariable=var_cur, fg="white",
                 bg="black", font="Arial 12 bold")
max_apm_label = tk.Label(stats_left, textvariable=var_max, fg="white",
                 bg="black", font="Arial 10")
avg_apm_label = tk.Label(stats_left, textvariable=var_avg, fg="white",
                 bg="black", font="Arial 10")
active_time_label = tk.Label(stats_right, textvariable=var_active, fg="white",
                 bg="black", font="Arial 10")
keys_clicks_label = tk.Label(stats_right, textvariable=var_kc,fg="white",
                 bg="black", font="Arial 10")

cur_apm_label.place(x=0, y=0)
max_apm_label.place(x=0, y=0)
avg_apm_label.place(x=0, y=height//8)
active_time_label.place(x=0, y=0)
keys_clicks_label.place(x=0, y=height//8)


def update_stats():
    cur_apm = int(graph.cur_apm)
    max_apm = int(graph.max_apm)
    avg_apm = int(graph.avg_apm)
    if graph.active == "inactive":
        active_time = 0
        var_active.set("Active Time : {}%".format(active_time))
    elif graph.active == "active":
        running_time = time.time() - graph.start_time - graph.paused_time
        active_time = graph.active_time / running_time
        active_time = round(100*active_time, 2)
        var_active.set("Active Time : {}%".format(active_time))
    keys_clicks = graph.keypresses / max((graph.clicks + graph.keypresses), 1)
    keys_clicks = round(100 * keys_clicks, 2)
    var_cur.set("Current : {} APM".format(cur_apm))
    var_max.set("Max : {} APM".format(max_apm))
    var_avg.set("Avg : {} APM".format(avg_apm))
    var_kc.set("Keypresses : {}%".format(keys_clicks))

    Fenetre.update_idletasks()

    if graph.active != "inactive":
        stats.after(100, update_stats)


# Real-time moving average apm graphing 
graph = Graph(Fenetre, bg="black", width=width, height=3*height//4,
              max_x=10, max_y=10)
graph.place(x=0, y=height//4)
graph.display(intro=True)


Fenetre.mainloop()
klistener.stop()
mlistener.stop()
