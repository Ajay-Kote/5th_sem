# network_monitor.py

import tkinter as tk
from tkinter import messagebox
import threading
import speedtest
from ping3 import ping
import time

# ---------------- Functions ---------------- #

def check_network():
    try:
        # Disable button during check
        check_btn.config(state="disabled")
        status_label.config(text="Checking network...", fg="blue")
        root.update()

        # Speed Test
        st = speedtest.Speedtest()
        download_speed = st.download() / 1_000_000  # in Mbps
        upload_speed = st.upload() / 1_000_000      # in Mbps

        download_label.config(text=f"Download: {download_speed:.2f} Mbps")
        upload_label.config(text=f"Upload: {upload_speed:.2f} Mbps")

        # Ping Test
        host = "google.com"
        latency = ping(host) * 1000  # in ms
        ping_label.config(text=f"Ping to {host}: {latency:.2f} ms")

        status_label.config(text="Network check completed!", fg="green")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Error occurred!", fg="red")
    finally:
        check_btn.config(state="normal")

def start_thread():
    t = threading.Thread(target=check_network)
    t.start()

# ---------------- GUI Setup ---------------- #

root = tk.Tk()
root.title("Network Monitoring Tool")
root.geometry("400x300")
root.resizable(False, False)

title_label = tk.Label(root, text="Mini Project: Network Monitor", font=("Arial", 14, "bold"))
title_label.pack(pady=10)

check_btn = tk.Button(root, text="Check Network", font=("Arial", 12), command=start_thread)
check_btn.pack(pady=10)

status_label = tk.Label(root, text="Click 'Check Network' to start", fg="blue")
status_label.pack(pady=5)

download_label = tk.Label(root, text="Download: -", font=("Arial", 12))
download_label.pack(pady=5)

upload_label = tk.Label(root, text="Upload: -", font=("Arial", 12))
upload_label.pack(pady=5)

ping_label = tk.Label(root, text="Ping: -", font=("Arial", 12))
ping_label.pack(pady=5)

root.mainloop()
