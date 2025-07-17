import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess, re, cv2
from djitellopy import Tello

# Load speed from config.txt
def load_speed(path="config.txt"):
    try:
        with open(path, "r") as f:
            for line in f:
                if line.startswith("speed="):
                    return int(line.strip().split("=")[1])
    except:
        return 30  # default speed
    return 30

speed = load_speed()
drone = Tello()
frame_label = None

def get_wifi_name():
    try:
        result = subprocess.check_output([
            "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"
        ])
        ssid_match = re.search(r"^\s*SSID: (.+)$", result.decode(), re.MULTILINE)
        return ssid_match.group(1) if ssid_match else None
    except:
        return None

def connect_to_drone():
    ssid = get_wifi_name()
    if ssid and ssid.startswith("TELLO-"):
        try:
            drone.connect()
            drone.streamon()
            show_flight_ui(ssid)
        except Exception as e:
            messagebox.showerror("Drone Error", f"Failed to connect to drone: {e}")
    else:
        messagebox.showerror("Connection Error", "Error: Not connected to TELLO wifi or other error.")

def show_flight_ui(ssid):
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text=f"✔️ Connected to {ssid}", font=("Helvetica", 16), fg="green").pack(pady=10)
    tk.Button(root, text="Go Fly", command=start_flight).pack(pady=10)

def start_flight():
    for widget in root.winfo_children():
        widget.destroy()
    global frame_label
    frame_label = tk.Label(root)
    frame_label.pack()
    drone.takeoff()
    update_frame()
    root.bind("<KeyPress>", key_handler)
    root.bind("<KeyRelease>", stop_movement)

def update_frame():
    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (640, 480))
    img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
    frame_label.config(image=img)
    frame_label.image = img
    root.after(15, update_frame)

def key_handler(event):
    key = event.keysym
    if key == 'w':
        drone.send_rc_control(0, speed, 0, 0)
    elif key == 's':
        drone.send_rc_control(0, -speed, 0, 0)
    elif key == 'a':
        drone.send_rc_control(-speed, 0, 0, 0)
    elif key == 'd':
        drone.send_rc_control(speed, 0, 0, 0)
    elif key == 'Left':
        drone.send_rc_control(0, 0, 0, -speed)
    elif key == 'Right':
        drone.send_rc_control(0, 0, 0, speed)

def stop_movement(event):
    drone.send_rc_control(0, 0, 0, 0)

# Initial UI
root = tk.Tk()
root.title("DroneZY")
root.geometry("700x550")

tk.Label(root, text="How to connect:", font=("Helvetica", 14)).pack(pady=10)
tk.Label(root, text="1. Turn on your drone\n2. Connect to WiFi starting with TELLO-ABC1234\n3. Then press Connect", justify="left").pack(pady=10)
tk.Button(root, text="Connect", command=connect_to_drone, width=20).pack(pady=20)

root.mainloop()
