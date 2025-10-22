# enhanced_network_monitor.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import speedtest
from ping3 import ping
import time
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque

# ---------------- Data Storage ---------------- #
class NetworkHistory:
    def __init__(self, maxlen=20):
        self.timestamps = deque(maxlen=maxlen)
        self.download_speeds = deque(maxlen=maxlen)
        self.upload_speeds = deque(maxlen=maxlen)
        self.ping_times = deque(maxlen=maxlen)
    
    def add_record(self, download, upload, ping_time):
        self.timestamps.append(datetime.now().strftime("%H:%M:%S"))
        self.download_speeds.append(download)
        self.upload_speeds.append(upload)
        self.ping_times.append(ping_time)
    
    def get_stats(self):
        if not self.download_speeds:
            return None
        return {
            'avg_download': sum(self.download_speeds) / len(self.download_speeds),
            'avg_upload': sum(self.upload_speeds) / len(self.upload_speeds),
            'avg_ping': sum(self.ping_times) / len(self.ping_times),
            'max_download': max(self.download_speeds),
            'min_download': min(self.download_speeds),
            'max_ping': max(self.ping_times),
            'min_ping': min(self.ping_times)
        }

history = NetworkHistory()
is_monitoring = False
monitor_thread = None

# ---------------- Functions ---------------- #
def check_network():
    try:
        # Update UI on main thread
        root.after(0, lambda: check_btn.config(state="disabled"))
        root.after(0, lambda: status_label.config(text="Checking network...", fg="blue"))
        root.after(0, lambda: progress_bar.start(10))
        
        # Speed Test
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # in Mbps
        upload_speed = st.upload() / 1_000_000      # in Mbps
        
        # Ping Test
        host = "8.8.8.8"
        latency = ping(host, timeout=2)
        if latency is None:
            latency = 0
        else:
            latency = latency * 1000  # in ms
        
        # Update labels on main thread
        root.after(0, lambda: download_label.config(text=f"Download: {download_speed:.2f} Mbps"))
        root.after(0, lambda: upload_label.config(text=f"Upload: {upload_speed:.2f} Mbps"))
        root.after(0, lambda: ping_label.config(text=f"Ping (8.8.8.8): {latency:.2f} ms"))
        
        # Add to history
        history.add_record(download_speed, upload_speed, latency)
        
        # Update graphs and stats on main thread
        root.after(0, update_graphs)
        root.after(0, update_stats)
        
        root.after(0, lambda: status_label.config(text="Network check completed!", fg="green"))
        
    except Exception as e:
        error_msg = f"Network check failed:\n{str(e)}"
        root.after(0, lambda: messagebox.showerror("Error", error_msg))
        root.after(0, lambda: status_label.config(text="Error occurred!", fg="red"))
    finally:
        root.after(0, lambda: progress_bar.stop())
        root.after(0, lambda: check_btn.config(state="normal"))

def start_check_thread():
    t = threading.Thread(target=check_network, daemon=True)
    t.start()

def continuous_monitor():
    global is_monitoring
    while is_monitoring:
        check_network()
        time.sleep(30)  # Check every 30 seconds

def toggle_monitoring():
    global is_monitoring, monitor_thread
    
    if not is_monitoring:
        is_monitoring = True
        monitor_btn.config(text="Stop Monitoring")
        monitor_thread = threading.Thread(target=continuous_monitor, daemon=True)
        monitor_thread.start()
        status_label.config(text="Continuous monitoring started...", fg="blue")
    else:
        is_monitoring = False
        monitor_btn.config(text="Start Continuous Monitor")
        status_label.config(text="Monitoring stopped", fg="orange")

def update_graphs():
    try:
        if len(history.timestamps) == 0:
            return
        
        # Clear previous plots
        ax1.clear()
        ax2.clear()
        
        times = list(history.timestamps)
        downloads = list(history.download_speeds)
        uploads = list(history.upload_speeds)
        pings = list(history.ping_times)
        
        # Plot download/upload speeds
        ax1.plot(times, downloads, 'b-o', label='Download', linewidth=2, markersize=4)
        ax1.plot(times, uploads, 'r-o', label='Upload', linewidth=2, markersize=4)
        ax1.set_title('Speed History', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Speed (Mbps)', fontsize=9)
        ax1.legend(loc='upper left', fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45, labelsize=7)
        ax1.tick_params(axis='y', labelsize=8)
        
        # Plot ping times
        ax2.plot(times, pings, 'g-o', label='Ping', linewidth=2, markersize=4)
        ax2.set_title('Latency History', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Latency (ms)', fontsize=9)
        ax2.set_xlabel('Time', fontsize=9)
        ax2.legend(loc='upper left', fontsize=8)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45, labelsize=7)
        ax2.tick_params(axis='y', labelsize=8)
        
        # Refresh canvas
        fig.tight_layout()
        canvas.draw()
    except Exception as e:
        print(f"Graph update error: {e}")

def update_stats():
    try:
        stats = history.get_stats()
        if stats:
            stats_text.config(state='normal')
            stats_text.delete(1.0, tk.END)
            stats_text.insert(tk.END, "=== Network Statistics ===\n\n")
            stats_text.insert(tk.END, f"Average Download: {stats['avg_download']:.2f} Mbps\n")
            stats_text.insert(tk.END, f"Average Upload: {stats['avg_upload']:.2f} Mbps\n")
            stats_text.insert(tk.END, f"Average Ping: {stats['avg_ping']:.2f} ms\n\n")
            stats_text.insert(tk.END, f"Max Download: {stats['max_download']:.2f} Mbps\n")
            stats_text.insert(tk.END, f"Min Download: {stats['min_download']:.2f} Mbps\n\n")
            stats_text.insert(tk.END, f"Best Ping: {stats['min_ping']:.2f} ms\n")
            stats_text.insert(tk.END, f"Worst Ping: {stats['max_ping']:.2f} ms\n\n")
            stats_text.insert(tk.END, f"Total Tests: {len(history.timestamps)}")
            stats_text.config(state='disabled')
    except Exception as e:
        print(f"Stats update error: {e}")

def clear_history():
    global history
    history = NetworkHistory()
    ax1.clear()
    ax2.clear()
    canvas.draw()
    stats_text.config(state='normal')
    stats_text.delete(1.0, tk.END)
    stats_text.config(state='disabled')
    download_label.config(text="Download: -")
    upload_label.config(text="Upload: -")
    ping_label.config(text="Ping: -")
    status_label.config(text="History cleared", fg="blue")

def on_closing():
    global is_monitoring
    is_monitoring = False
    root.destroy()

# ---------------- GUI Setup ---------------- #
root = tk.Tk()
root.title("Advanced Network Monitor")
root.geometry("900x700")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Main frame
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# Title
title_label = tk.Label(main_frame, text="Advanced Network Monitor", 
                        font=("Arial", 16, "bold"), fg="#2c3e50")
title_label.pack(pady=10)

# Top section (controls + current stats)
top_frame = ttk.Frame(main_frame)
top_frame.pack(fill=tk.X, padx=5, pady=5)

# Control Panel
control_frame = ttk.LabelFrame(top_frame, text="Controls", padding="10")
control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

button_frame = ttk.Frame(control_frame)
button_frame.pack()

check_btn = ttk.Button(button_frame, text="Check Network", command=start_check_thread)
check_btn.grid(row=0, column=0, padx=5, pady=5)

monitor_btn = ttk.Button(button_frame, text="Start Continuous Monitor", command=toggle_monitoring)
monitor_btn.grid(row=0, column=1, padx=5, pady=5)

clear_btn = ttk.Button(button_frame, text="Clear History", command=clear_history)
clear_btn.grid(row=0, column=2, padx=5, pady=5)

progress_bar = ttk.Progressbar(control_frame, mode='indeterminate', length=300)
progress_bar.pack(pady=10)

status_label = tk.Label(control_frame, text="Click 'Check Network' to start", 
                        fg="blue", font=("Arial", 10))
status_label.pack()

# Current Stats Panel
stats_panel = ttk.LabelFrame(top_frame, text="Current Reading", padding="10")
stats_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)

download_label = tk.Label(stats_panel, text="Download: -", font=("Arial", 11, "bold"), fg="#27ae60")
download_label.pack(pady=5)

upload_label = tk.Label(stats_panel, text="Upload: -", font=("Arial", 11, "bold"), fg="#e74c3c")
upload_label.pack(pady=5)

ping_label = tk.Label(stats_panel, text="Ping: -", font=("Arial", 11, "bold"), fg="#3498db")
ping_label.pack(pady=5)

# Graph Panel
graph_frame = ttk.LabelFrame(main_frame, text="Network Performance Graphs", padding="10")
graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Create matplotlib figure
fig = Figure(figsize=(8, 5), dpi=80)
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Statistics Panel
stats_frame = ttk.LabelFrame(main_frame, text="Summary Statistics", padding="10")
stats_frame.pack(fill=tk.BOTH, padx=5, pady=5)

stats_text = tk.Text(stats_frame, height=8, font=("Courier", 9))
stats_text.pack(fill=tk.BOTH, expand=True)
stats_text.config(state='disabled')

root.mainloop()