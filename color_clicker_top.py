import pyautogui
import time
import threading
import tkinter as tk
from tkinter import ttk
from pynput import keyboard
from pynput.mouse import Controller, Button
from PIL import ImageGrab, Image

mouse = Controller()

selected_color = None
running = False
worker = None
is_holding = False

def colors_match(c1, c2, tol):
    return all(abs(a - b) <= tol for a, b in zip(c1, c2))

def click_loop():
    global running, is_holding
    while running:
        x, y = pyautogui.position()
        radius = radius_var.get()
        tol = tolerance_var.get()
        mode = holding_mode_var.get()
        
        # Grab a small box around the cursor for the search radius
        # bbox format: (left, top, right, bottom)
        bbox = (x - radius, y - radius, x + radius + 1, y + radius + 1)
        
        try:
            img = ImageGrab.grab(bbox=bbox, all_screens=True)
            pixels = img.getdata()
        except:
            continue

        # Check if any pixel in the radius matches our target
        found_match = False
        if selected_color:
            for p in pixels:
                if colors_match(p[:3], selected_color, tol):
                    found_match = True
                    break

        if mode == "Holding":
            if found_match and not is_holding:
                mouse.press(Button.left)
                is_holding = True
            elif not found_match and is_holding:
                mouse.release(Button.left)
                is_holding = False
        else: # Normal Click Mode
            if found_match:
                mouse.click(Button.left)
                time.sleep(0.1) # Prevents excessive clicking on a single target

        time.sleep(0.03) # High polling rate for fast reaction
    
    # Cleanup mouse state when stopping
    if is_holding:
        mouse.release(Button.left)
        is_holding = False

def start_bot():
    global running, worker
    if running or not selected_color: return
    running = True
    worker = threading.Thread(target=click_loop, daemon=True)
    worker.start()
    status_label.config(text="RUNNING", fg="#00FF00")

def stop_bot():
    global running
    running = False
    status_label.config(text="STOPPED", fg="#FF3333")

def on_press(key):
    global selected_color
    try:
        if key == keyboard.Key.f8:
            x, y = pyautogui.position()
            selected_color = pyautogui.pixel(x, y)
            # Update UI Preview
            hex_color = '#%02x%02x%02x' % selected_color
            color_preview.config(bg=hex_color)
            status_label.config(text=f"Picked: {selected_color}", fg="white")
        elif key == keyboard.Key.f6:
            start_bot()
        elif key == keyboard.Key.f7:
            stop_bot()
    except:
        pass

# ----- GUI -----
root = tk.Tk()
root.title("Color Bot Pro")
root.geometry("240x260")
root.attributes("-topmost", True)
root.configure(bg="#1e1e1e")

# Styles
style = ttk.Style()
style.theme_use('clam')

# Status & Preview Frame
top_frame = tk.Frame(root, bg="#1e1e1e")
top_frame.pack(pady=10)

color_preview = tk.Frame(top_frame, width=30, height=30, relief="sunken", borderwidth=2, bg="#333333")
color_preview.pack(side="left", padx=10)

status_label = tk.Label(top_frame, text="F8 Pick | F6 Start | F7 Stop", fg="white", bg="#1e1e1e", font=("Arial", 9, "bold"))
status_label.pack(side="left")

# Settings Frame
settings_frame = tk.Frame(root, bg="#1e1e1e")
settings_frame.pack(padx=15, fill="x")

# Tolerance Slider
tk.Label(settings_frame, text="Tolerance", fg="white", bg="#1e1e1e").pack(anchor="w")
tolerance_var = tk.IntVar(value=8)
tk.Scale(settings_frame, from_=0, to_=100, orient="horizontal", variable=tolerance_var, bg="#1e1e1e", fg="white", highlightthickness=0).pack(fill="x")

# Radius Slider
tk.Label(settings_frame, text="Search Radius (px)", fg="white", bg="#1e1e1e").pack(anchor="w", pady=(5,0))
radius_var = tk.IntVar(value=0) 
tk.Scale(settings_frame, from_=0, to_=20, orient="horizontal", variable=radius_var, bg="#1e1e1e", fg="white", highlightthickness=0).pack(fill="x")

# Mode Dropdown
tk.Label(settings_frame, text="Mode", fg="white", bg="#1e1e1e").pack(anchor="w", pady=(5,0))
holding_mode_var = tk.StringVar(value="Normal")
mode_menu = ttk.Combobox(settings_frame, textvariable=holding_mode_var, values=["Normal", "Holding"], state="readonly")
mode_menu.pack(fill="x", pady=5)

# Keyboard Listener Thread
def keyboard_thread():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

threading.Thread(target=keyboard_thread, daemon=True).start()

root.mainloop()
