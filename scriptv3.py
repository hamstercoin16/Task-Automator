import tkinter as tk
import threading
import time
from PIL import Image, ImageTk
from pynput.mouse import Controller, Button
from pynput import keyboard

# --- Global variables ---
left_clicking = False
right_clicking = False
click_type = "left"  # "left" or "right"
hotkey_start = keyboard.Key.f8
hotkey_stop = keyboard.Key.f9
hotkey_switch = keyboard.Key.f6
mouse = Controller()
listener = None

# --- Clicking functions ---
def start_clicking():
    global left_clicking, right_clicking
    if click_type == "left":
        if left_clicking:
            return
        left_clicking = True
    else:
        if right_clicking:
            return
        right_clicking = True
    threading.Thread(target=auto_click, daemon=True).start()

def stop_clicking():
    global left_clicking, right_clicking
    left_clicking = False
    right_clicking = False

def auto_click():
    try:
        interval = float(entry_interval.get())
    except ValueError:
        interval = 0.5
        entry_interval.delete(0, tk.END)
        entry_interval.insert(0, "0.5")
    while left_clicking or right_clicking:
        if left_clicking:
            mouse.click(Button.left)
        elif right_clicking:
            mouse.click(Button.right)
        time.sleep(interval)

def switch_click_type():
    global click_type
    click_type = "right" if click_type == "left" else "left"
    type_label.config(text=f"Current click: {click_type.capitalize()}")

# --- Global hotkeys ---
def on_press(key):
    try:
        if key == hotkey_start:
            start_clicking()
        elif key == hotkey_stop:
            stop_clicking()
        elif key == hotkey_switch:
            switch_click_type()
    except AttributeError:
        pass

def start_listener():
    global listener
    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()

# --- Settings window ---
def settings():
    global click_type, hotkey_start, hotkey_stop, hotkey_switch
    temp_hotkey_start = hotkey_start
    temp_hotkey_stop = hotkey_stop
    temp_hotkey_switch = hotkey_switch
    temp_click_type = click_type

    def listen_key(action):
        info_label.config(text=f"Press the button for {action}...")

        def on_key(event):
            nonlocal temp_hotkey_start, temp_hotkey_stop, temp_hotkey_switch
            key_name = event.keysym
            if key_name.lower() == "return":
                new_key = keyboard.Key.enter
            else:
                new_key = key_name

            if action == "start":
                temp_hotkey_start = new_key
                start_label.config(text=f"Start: {key_name}")
            elif action == "stop":
                temp_hotkey_stop = new_key
                stop_label.config(text=f"Stop: {key_name}")
            elif action == "switch":
                temp_hotkey_switch = new_key
                switch_label.config(text=f"Switch: {key_name}")

            info_label.config(text=f"Key {key_name} selected for {action}")
            settings_window.unbind("<Key>")

        settings_window.bind("<Key>", on_key)

    def save_settings():
        nonlocal temp_hotkey_start, temp_hotkey_stop, temp_hotkey_switch, temp_click_type
        global hotkey_start, hotkey_stop, hotkey_switch, click_type
        hotkey_start = temp_hotkey_start
        hotkey_stop = temp_hotkey_stop
        hotkey_switch = temp_hotkey_switch
        click_type = temp_click_type
        type_label.config(text=f"Current click: {click_type.capitalize()}")
        settings_window.destroy()
    
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x400")
    settings_window.resizable(False, False)
    
    # Background image for settings window
    settings_background = Image.open("settingsbackground.jpg")
    settings_background = settings_background.resize((484, 512), Image.Resampling.LANCZOS)
    settings_photo = ImageTk.PhotoImage(settings_background)
    settings_label = tk.Label(settings_window, image=settings_photo)
    settings_label.image = settings_photo  
    settings_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Start hotkey
    start_label = tk.Label(settings_window, text=f"Start: {temp_hotkey_start}")
    start_label.pack(pady=5)
    tk.Button(settings_window, text="Change Start Key", command=lambda: listen_key("start")).pack(pady=5)

    # Stop hotkey
    stop_label = tk.Label(settings_window, text=f"Stop: {temp_hotkey_stop}")
    stop_label.pack(pady=5)
    tk.Button(settings_window, text="Change Stop Key", command=lambda: listen_key("stop")).pack(pady=5)

    # Switch hotkey
    switch_label = tk.Label(settings_window, text=f"Switch: {temp_hotkey_switch}")
    switch_label.pack(pady=5)
    tk.Button(settings_window, text="Change Switch Key", command=lambda: listen_key("switch")).pack(pady=5)

    # Click type selection
    tk.Label(settings_window, text="Choose click type:").pack(pady=10)
    click_var = tk.StringVar(value=temp_click_type)
    def set_click_type():
        nonlocal temp_click_type
        temp_click_type = click_var.get()
    tk.Radiobutton(settings_window, text="Left", variable=click_var, value="left", command=set_click_type).pack()
    tk.Radiobutton(settings_window, text="Right", variable=click_var, value="right", command=set_click_type).pack()

    # Info label
    info_label = tk.Label(settings_window, text="")
    info_label.pack(pady=10)

    # Save button
    tk.Button(settings_window, text="Save changes", command=save_settings).pack(pady=10)

# --- GUI setup ---
root = tk.Tk()
root.title("Autoclicker")
root.geometry("400x300")
root.resizable(False, False)

# Background image
background_image = Image.open("background.jpg")
background_photo = ImageTk.PhotoImage(background_image)
background_label = tk.Label(root, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Interval input
tk.Label(root, text="Interval (sec):").pack(pady=5)
entry_interval = tk.Entry(root)
entry_interval.insert(0, "0.5")
entry_interval.pack(pady=5)

# Current click type
type_label = tk.Label(root, text=f"Current click: {click_type.capitalize()}")
type_label.pack(pady=5)

# Button hover animation
def colorbuttons():
    def on_enter(e):
        e.widget['background'] = 'grey' 
        e.widget['foreground'] = 'white' 

    def on_leave(e):
        e.widget['background'] = 'SystemButtonFace' 
        e.widget['foreground'] = 'black'    

    # Attach animation to buttons
    for btn in [button_start, button_stop, button_settings]:
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

# buttons
button_start = tk.Button(root, text="Start", command=start_clicking, width=15)
button_start.place(x=50, y=210)

button_stop = tk.Button(root, text="Stop", command=stop_clicking, width=15)
button_stop.place(x=200, y=210)

button_settings = tk.Button(root, text="Settings", command=settings, width=15)
button_settings.place(x=125, y=255)

colorbuttons()

start_listener()

root.mainloop()
