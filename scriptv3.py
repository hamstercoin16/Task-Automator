import tkinter as tk
import threading
import time
from PIL import Image, ImageTk
from pynput.mouse import Controller, Button
from pynput import keyboard
from pynput.mouse import Listener as MouseListener
import pyautogui

# Global variables
left_clicking = False
right_clicking = False
click_type = "left"  # "left" or "right"
mouse = Controller()
listener = None
mouse_recording = False
mouse_events = []
mouse_listener = None
settings_window_open = False

# Hotkeys
hotkey_start = keyboard.Key.f7
hotkey_stop = keyboard.Key.f8
hotkey_switch = keyboard.Key.f9
hotkey_record_start = keyboard.Key.f10
hotkey_record_stop = keyboard.Key.f11
hotkey_play_recording = keyboard.Key.f12

# licking functions
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
        user_input = entry_clicks.get()
        if user_input == 'infinity':
            interval = float(entry_interval.get())
            clicks_to_perform = float('inf') 
        else:
            interval = float(entry_interval.get())
            clicks_to_perform = int(entry_clicks.get())
    except ValueError:
        interval = 0.5
        clicks_to_perform = 10
        entry_interval.delete(0, tk.END)
        entry_interval.insert(0, "0.5")
        entry_clicks.delete(0, tk.END)
        entry_clicks.insert(0, "10")

    clicks_done = 0
    while (left_clicking or right_clicking) and clicks_done < clicks_to_perform:
        if left_clicking:
            mouse.click(Button.left)
        elif right_clicking:
            mouse.click(Button.right)
        time.sleep(interval)
        clicks_done += 1
    
    stop_clicking()


def switch_click_type():
    global click_type
    click_type = "right" if click_type == "left" else "left"
    type_label.config(text=f"Current click: {click_type.capitalize()}")

# Mouse recording 
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
    global mouse_events
    
    if not mouse_events:
        print("No mouse events recorded.")
        return
    
    try:
        user_input = entry_recordings.get()
        if user_input.lower() == 'infinity':
            play_count = float('inf')
        else:
            play_count = int(user_input)
    except ValueError:
        play_count = 1
        entry_recordings.delete(0, tk.END)
        entry_recordings.insert(0, "1")

    if not mouse_events:
        print("Список событий пуст.")
        return
    
    first_event = mouse_events[0]
    initial_time = first_event[-1]

    count = 0
    while count < play_count:
        playback_start_time = time.time()

        for event in mouse_events:
            event_type = event[0]
            t_recorded = event[-1]
            
            relative_delay = t_recorded - initial_time
            target_time = playback_start_time + relative_delay

            sleep_duration = target_time - time.time()
            if sleep_duration > 0:
                time.sleep(sleep_duration)
            
            if event_type == 'move':
                _, x, y, _ = event
                # Используем duration=0 для мгновенного перемещения
                pyautogui.moveTo(x, y, duration=0) 
            elif event_type == 'click':
                _, x, y, button_str, pressed, _ = event
                # Используем duration=0 для мгновенного клика
                if 'left' in button_str:
                    pyautogui.click(x, y, button='left', duration=0)
                elif 'right' in button_str:
                    pyautogui.click(x, y, button='right', duration=0)
        
        count += 1
        print(f"Воспроизведение завершено: {count}/{play_count}")

# Global hotkeys
def on_press(key):
    if key == hotkey_start:
        start_clicking()
    elif key == hotkey_stop:
        stop_clicking()
    elif key == hotkey_switch:
        switch_click_type()
    
    elif key == hotkey_record_start:
        start_mouse_recording()
    elif key == hotkey_record_stop:
        stop_mouse_recording()
    elif key == hotkey_play_recording:
        play_mouse_recording()

def start_listener():
    global listener
    if listener and listener.is_alive():
        listener.stop()
    
    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()

# SETTINGS WINDOW
def settings():
    global click_type, hotkey_start, hotkey_stop, hotkey_switch, hotkey_record_start, hotkey_record_stop, hotkey_play_recording, settings_window_open

    temp_hotkey_start = hotkey_start
    temp_hotkey_stop = hotkey_stop
    temp_hotkey_switch = hotkey_switch
    temp_click_type = click_type
    
    temp_hotkey_record_start = hotkey_record_start
    temp_hotkey_record_stop = hotkey_record_stop
    temp_hotkey_record_play = hotkey_play_recording

    if settings_window_open:
        return
    settings_window_open = True
    
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x400")
    settings_window.resizable(False, False)

    settings_background = Image.open("settingsbackground.jpg")
    settings_background = settings_background.resize((484, 512), Image.Resampling.LANCZOS)
    settings_photo = ImageTk.PhotoImage(settings_background)
    settings_label = tk.Label(settings_window, image=settings_photo)
    settings_label.image = settings_photo  
    settings_label.place(x=0, y=0, relwidth=1, relheight=1)

    info_label = tk.Label(settings_window, text="")
    info_label.pack(pady=10)

    start_label = tk.Label(settings_window, text=f"Start: {temp_hotkey_start}")
    start_label.place(x=23, y=10)

    stop_label = tk.Label(settings_window, text=f"Stop: {temp_hotkey_stop}")
    stop_label.place(x=23, y=80)

    switch_label = tk.Label(settings_window, text=f"Switch: {temp_hotkey_switch}")
    switch_label.place(x=23, y=150)

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
    
    # Funktions
    def reset_settings(start_label, stop_label, switch_label, click_var):
        nonlocal temp_hotkey_start, temp_hotkey_stop, temp_hotkey_switch, temp_click_type, temp_hotkey_record_start, temp_hotkey_record_stop, temp_hotkey_record_play   
        temp_hotkey_start = keyboard.Key.f7
        temp_hotkey_stop = keyboard.Key.f8
        temp_hotkey_switch = keyboard.Key.f9
        temp_hotkey_record_start = keyboard.Key.f10
        temp_hotkey_record_stop = keyboard.Key.f11
        temp_hotkey_record_play = keyboard.Key.f12       
        click_var.set(temp_click_type)
        start_label.config(text=f"Start: {temp_hotkey_start}")
        stop_label.config(text=f"Stop: {temp_hotkey_stop}")
        switch_label.config(text=f"Switch: {temp_hotkey_switch}")
        startrecord_label.config(text=f"Start Recording: {temp_hotkey_record_start}")
        stoprecord_label.config(text=f"Stop Recording: {temp_hotkey_record_stop}")
        playrecord_label.config(text=f"Play Recording: {temp_hotkey_record_play}")
        info_label.config(text="Settings reset to default.")
        info_label.place(x=140, y=250)
    
    def on_settings_close():
        global settings_window_open
        settings_window_open = False
        settings_window.destroy()
    settings_window.protocol("WM_DELETE_WINDOW", on_settings_close)

    def save_settings():
        nonlocal temp_hotkey_start, temp_hotkey_stop, temp_hotkey_switch, temp_click_type, temp_hotkey_record_start, temp_hotkey_record_stop, temp_hotkey_record_play
        global hotkey_start, hotkey_stop, hotkey_switch, click_type, hotkey_record_start, hotkey_record_stop, hotkey_play_recording
        hotkey_start = temp_hotkey_start
        hotkey_stop = temp_hotkey_stop
        hotkey_switch = temp_hotkey_switch
        hotkey_record_start = temp_hotkey_record_start
        hotkey_record_stop = temp_hotkey_record_stop
        hotkey_play_recording = temp_hotkey_record_play
        click_type = temp_click_type
        type_label.config(text=f"Current click: {click_type.capitalize()}")
        settings_window.destroy()
        start_listener()
        on_settings_close()


    def listen_key(action):
        info_label.config(text=f"Press the button for {action}...")
        info_label.place(x=115, y=250)

        def on_key(event):
            nonlocal temp_hotkey_start, temp_hotkey_stop, temp_hotkey_switch, temp_hotkey_record_start, temp_hotkey_record_stop, temp_hotkey_record_play
            key_name = event.keysym.upper()

            if key_name == "RETURN":
                new_key = keyboard.Key.enter
            elif key_name.startswith("F") and key_name[1:].isdigit():
                new_key = getattr(keyboard.Key, key_name)
            else:
                new_key = keyboard.KeyCode.from_char(event.char)

            if action == "start":
                temp_hotkey_start = new_key
                start_label.config(text=f"Start: {key_name}")
            elif action == "stop":
                temp_hotkey_stop = new_key
                stop_label.config(text=f"Stop: {key_name}")
            elif action == "switch":
                temp_hotkey_switch = new_key
                switch_label.config(text=f"Switch: {key_name}")
            elif action == "record_start":
                temp_hotkey_record_start = new_key
                startrecord_label.config(text=f"Start Recording: {key_name}")
            elif action == "record_stop":
                temp_hotkey_record_stop = new_key
                stoprecord_label.config(text=f"Stop Recording: {key_name}")
            elif action == "record_play":
                temp_hotkey_record_play = new_key
                playrecord_label.config(text=f"Play Recording: {key_name}")

            info_label.config(text=f"Key {key_name} selected for {action}")
            settings_window.unbind("<Key>")

        settings_window.bind("<Key>", on_key)

    
    # Mouse recording buttons
    button_change_record_start = tk.Button(settings_window, text="Change Start Recording Key", command=lambda: listen_key("record_start"), width=20)
    button_change_record_start.place(x=270, y=40)

    button_change_record_stop = tk.Button(settings_window, text="Change Stop Recording Key", command=lambda: listen_key("record_stop"), width=20)
    button_change_record_stop.place(x=270, y=110)

    button_change_record_play = tk.Button(settings_window, text="Change Play Recording Key", command=lambda: listen_key("record_play"), width=20)
    button_change_record_play.place(x=270, y=180)
        
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
    
    # Hover effects for settings buttons
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

    add_hover_effect([
        key_switch_button,
        Change_stop_button,
        change_start_button,
        button_change_record_start,
        button_change_record_stop,
        button_change_record_play
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
        

# GUI setup
root = tk.Tk()
root.title("Autoclicker")
root.geometry("400x300")
root.resizable(False, False)

# Background image
background_image = Image.open("background.jpg")
background_photo = ImageTk.PhotoImage(background_image)
background_label = tk.Label(root, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Labels
tk.Label(root, text="Interval (sec):").place(x=165, y=40) # Interval input
entry_interval = tk.Entry(root)
entry_interval.insert(0, "0.5")
entry_interval.place(x=140, y=70)

tk.Label(root, text="Number of clicks:",).place(x=25, y=100) # Number of clicks
entry_clicks = tk.Entry(root)
entry_clicks.insert(0, "infinity")
entry_clicks.place(x=15, y=130)

tk.Label(root, text="Number of recordings:").place(x=255, y=100) # Number of recordings
entry_recordings = tk.Entry(root)
entry_recordings.insert(0, "1")
entry_recordings.place(x=255, y=130)

type_label = tk.Label(root, text=f"Current click: {click_type.capitalize()}") # Current click type
type_label.place(x=152, y=7)

# Buttons
button_start = tk.Button(root, text="Start Click", command=start_clicking, width=15)
button_start.place(x=20, y=165)

button_stop = tk.Button(root, text="Stop Click", command=stop_clicking, width=15)
button_stop.place(x=20, y=205)

button_settings = tk.Button(root, text="Settings", command=settings, width=15)
button_settings.place(x=140, y=255)

button_record_start = tk.Button(root, text="Start Recording", command=start_mouse_recording, width=15)
button_record_start.place(x=260, y=165)

button_record_stop = tk.Button(root, text="Stop Recording", command=stop_mouse_recording, width=15)
button_record_stop.place(x=260, y=205)

button_record_play= tk.Button(root, text="Play Recording", command=play_mouse_recording, width=15)
button_record_play.place(x=140, y=185)

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
        button_record_stop,
        button_record_play
    ]:
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

colorbuttons()
start_listener()
root.mainloop()
