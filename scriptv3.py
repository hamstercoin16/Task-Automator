import tkinter as tk
import threading
import time
from PIL import Image, ImageTk
from pynput.mouse import Controller, Button
from pynput import keyboard
from pynput.mouse import Listener as MouseListener

# --- Global variables ---
left_clicking = False
right_clicking = False
click_type = "left"  # "left" or "right"
mouse = Controller()
listener = None
mouse_recording = False
mouse_events = []
mouse_listener = None

# Hotkeys
hotkey_start = keyboard.Key.f7
hotkey_stop = keyboard.Key.f8
hotkey_switch = keyboard.Key.f9
hotkey_record_start = keyboard.Key.f10
hotkey_record_stop = keyboard.Key.f11
hotkey_play_recording = keyboard.Key.f12

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

# --- Mouse recording ---
def on_move(x, y):
    if mouse_recording:
        mouse_events.append(('move', x, y, time.time()))

def on_click(x, y, button, pressed):
    if mouse_recording:
        mouse_events.append(('click', x, y, str(button), pressed, time.time()))

def start_mouse_recording():
    global mouse_recording, mouse_events, mouse_listener
    mouse_events = []
    mouse_recording = True
    mouse_listener = MouseListener(on_move=on_move, on_click=on_click)
    mouse_listener.start()

def stop_mouse_recording():
    global mouse_recording, mouse_listener
    mouse_recording = False
    if mouse_listener:
        mouse_listener.stop()
        mouse_listener = None

def play_mouse_recording():
    if not mouse_events:
        print("No mouse events recorded.")
        return
    start_time = mouse_events[0][3] if mouse_events[0][0] == 'move' else mouse_events[0][5]
    for event in mouse_events:
        if event[0] == 'move':
            _, x, y, t = event
            time.sleep(max(0, t - start_time))
            mouse.position = (x, y)
            start_time = t
        elif event[0] == 'click':
            _, x, y, button, pressed, t = event
            time.sleep(max(0, t - start_time))
            mouse.position = (x, y)
            btn = Button.left if 'left' in button else Button.right
            if pressed:
                mouse.press(btn)
            else:
                mouse.release(btn)
            start_time = t

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

    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x400")
    settings_window.resizable(False, False)

    # Background image
    settings_background = Image.open("settingsbackground.jpg")
    settings_background = settings_background.resize((484, 512), Image.Resampling.LANCZOS)
    settings_photo = ImageTk.PhotoImage(settings_background)
    settings_label = tk.Label(settings_window, image=settings_photo)
    settings_label.image = settings_photo  
    settings_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Info label
    info_label = tk.Label(settings_window, text="")
    info_label.pack(pady=10)

    # Start hotkey
    start_label = tk.Label(settings_window, text=f"Start: {temp_hotkey_start}")
    start_label.place(x=23, y=10)

    # Stop hotkey
    stop_label = tk.Label(settings_window, text=f"Stop: {temp_hotkey_stop}")
    stop_label.place(x=23, y=80)


    # Switch hotkey
    switch_label = tk.Label(settings_window, text=f"Switch: {temp_hotkey_switch}")
    switch_label.place(x=23, y=150)

    # Recording labels and buttons
    startrecord_label = tk.Label(settings_window, text=f"Start Recording: {hotkey_record_start}")
    startrecord_label.place(x=270, y=10)

    stoprecord_label = tk.Label(settings_window, text=f"Stop Recording: {hotkey_record_stop}")
    stoprecord_label.place(x=270, y=80)

    playrecord_label = tk.Label(settings_window, text=f"Play Recording: {hotkey_play_recording}")
    playrecord_label.place(x=270, y=150)

    # Click type selection
    tk.Label(settings_window, text="Choose click type:").place(x=150, y=10)
    click_var = tk.StringVar(value=temp_click_type)
    def set_click_type():
        nonlocal temp_click_type
        temp_click_type = click_var.get()
    tk.Radiobutton(settings_window, text="Left", variable=click_var, value="left", command=set_click_type).place(x=175, y=33)
    tk.Radiobutton(settings_window, text="Right", variable=click_var, value="right", command=set_click_type).place(x=171, y=56)

    # Mouse recording buttons
    button_record_start = tk.Button(settings_window, text="Start Recording", command=start_mouse_recording, width=15)
    button_record_start.place(x=280, y=40)

    button_record_stop = tk.Button(settings_window, text="Stop Recording", command=stop_mouse_recording, width=15)
    button_record_stop.place(x=280, y=110)

    button_play_recording = tk.Button(settings_window, text="Play Recording", command=play_mouse_recording, width=15)
    button_play_recording.place(x=280, y=180)

    button_resetsettings = tk.Button(settings_window, text="Reset to Default", command=lambda: reset_settings(start_label, stop_label, switch_label, click_var), width=15)
    button_resetsettings.place(x=140, y=320)

    button_savesettings = tk.Button(settings_window, text="Save Settings", command=lambda: save_settings(), width=15)
    button_savesettings.place(x=140, y=360)
    
    key_switch_button = tk.Button(settings_window, text="Change Switch Key", command=lambda: listen_key("switch"))
    key_switch_button.place(x=10, y=180)    
    
    Change_stop_button = tk.Button(settings_window, text="Change Stop Key", command=lambda: listen_key("stop"))
    Change_stop_button.place(x=10, y=110)
    
    change_start_button = tk.Button(settings_window, text="Change Start Key", command=lambda: listen_key("start"))
    change_start_button.place(x=10, y=40)
    
    # --- Hover эффект для кнопок в окне настроек ---
    def add_hover_effect(buttons):
        def on_enter(e):
            e.widget['background'] = 'grey'
            e.widget['foreground'] = 'white'

        def on_leave(e):
            e.widget['background'] = 'SystemButtonFace'
            e.widget['foreground'] = 'black'

        for btn in buttons:
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    # Применяем к кнопкам настроек
    add_hover_effect([
        button_record_start, 
        button_record_stop, 
        button_play_recording, 
        key_switch_button,
        Change_stop_button,
        change_start_button
    ])

    def add_hover_effect_savesettings(buttons):
        def on_enter(e):
            e.widget['background'] = 'green'
            e.widget['foreground'] = 'white'

        def on_leave(e):
            e.widget['background'] = 'SystemButtonFace'
            e.widget['foreground'] = 'black'

        for btn in buttons:
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    add_hover_effect_savesettings([button_savesettings])

    def add_hover_effect_resetsettings(buttons):
        def on_enter(e):
            e.widget['background'] = 'red'
            e.widget['foreground'] = 'white'

        def on_leave(e):
            e.widget['background'] = 'SystemButtonFace'
            e.widget['foreground'] = 'black'

        for btn in buttons:
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    add_hover_effect_resetsettings([button_resetsettings])
        
    # --- Nested functions ---
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
tk.Label(root, text="Interval (sec):").place(x=165, y=40)
entry_interval = tk.Entry(root)
entry_interval.insert(0, "0.5")
entry_interval.place(x=140, y=70)

# Number of clicks
tk.Label(root, text="Number of clicks:").place(x=35, y=100)
entry_clicks = tk.Entry(root)
entry_clicks.insert(0, "5")
entry_clicks.place(x=25, y=130)

# Number of recordings
tk.Label(root, text="Number of recordings:").place(x=245, y=100)
entry_recordings = tk.Entry(root)
entry_recordings.insert(0, "5")
entry_recordings.place(x=245, y=130)

# Current click type
type_label = tk.Label(root, text=f"Current click: {click_type.capitalize()}")
type_label.pack(pady=5)

# Buttons
button_start = tk.Button(root, text="Start Click", command=start_clicking, width=15)
button_start.place(x=30, y=165)

button_stop = tk.Button(root, text="Stop Click", command=stop_clicking, width=15)
button_stop.place(x=30, y=205)

button_settings = tk.Button(root, text="Settings", command=settings, width=15)
button_settings.place(x=140, y=255)

button_record_start = tk.Button(root, text="Start Recording", command=start_mouse_recording, width=15)
button_record_start.place(x=250, y=165)

button_record_stop = tk.Button(root, text="Stop Recording", command=stop_mouse_recording, width=15)
button_record_stop.place(x=250, y=205)

# Hover effect for main window buttons
def colorbuttons():
    def on_enter(e):
        e.widget['background'] = 'grey' 
        e.widget['foreground'] = 'white' 

    def on_leave(e):
        e.widget['background'] = 'SystemButtonFace' 
        e.widget['foreground'] = 'black'    

    for btn in [
        button_start,
        button_stop,
        button_settings,
        button_record_start,
        button_record_stop
    ]:
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

colorbuttons()
start_listener()
root.mainloop()
