import pyautogui

import time

import threading

import tkinter as tk

from pynput import keyboard

from pynput.mouse import Controller, Button



mouse = Controller()



selected_color = None

running = False

worker = None

TOLERANCE = 8   # adjust if needed (higher = looser color match)





def colors_match(c1, c2, tol):

    return all(abs(a - b) <= tol for a, b in zip(c1, c2))





def click_loop():

    global running

    while running:

        x, y = pyautogui.position()

        current = pyautogui.pixel(x, y)



        if selected_color and colors_match(current, selected_color, TOLERANCE):

            mouse.click(Button.left)



        time.sleep(0.08)  # click speed





def start_bot():

    global running, worker

    if running or not selected_color:

        return



    running = True

    worker = threading.Thread(target=click_loop, daemon=True)

    worker.start()

    status_label.config(text="Running")





def stop_bot():

    global running

    running = False

    status_label.config(text="Stopped")





def on_press(key):

    global selected_color



    if key == keyboard.Key.f8:

        x, y = pyautogui.position()

        selected_color = pyautogui.pixel(x, y)

        status_label.config(text=f"Color {selected_color}")



    elif key == keyboard.Key.f6:

        start_bot()



    elif key == keyboard.Key.f7:

        stop_bot()


# ----- Always on top window -----



root = tk.Tk()

root.title("Color Bot")

root.geometry("210x70")

root.attributes("-topmost", True)

root.resizable(False, False)



status_label = tk.Label(root, text="F8 Pick | F6 Start | F7 Stop")

status_label.pack(expand=True)





def keyboard_thread():

    with keyboard.Listener(on_press=on_press) as listener:

        listener.join()





threading.Thread(target=keyboard_thread, daemon=True).start()



root.mainloop()
