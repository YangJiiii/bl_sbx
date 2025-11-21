import customtkinter as ctk
from tkinter import filedialog
import subprocess
import threading
import sys
import os
import queue


try:
    from pymobiledevice3.usbmux import list_devices
except ImportError:
    list_devices = None



ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class ExploitLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("iOS Sandbox Escape - Launcher")
        self.geometry("950x750")
        self.resizable(False, False)

        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # ==================================================
        # 1. HEADER SECTION
        # ==================================================
        self.header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1a1a")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Main Title
        self.label_title = ctk.CTkLabel(self.header_frame, text="BL_SBX EXPLOIT LAUNCHER", 
                                        font=("Consolas", 28, "bold"), text_color="#00ff00")
        self.label_title.pack(pady=20)

        # ==================================================
        # 2. INPUT SECTION
        # ==================================================
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # --- Row 0: UDID ---
        self.udid_label = ctk.CTkLabel(self.input_frame, text="DEVICE UDID:", font=("Roboto", 13, "bold"))
        self.udid_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.udid_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Scanning...", width=550, font=("Consolas", 12))
        self.udid_entry.grid(row=0, column=1, padx=10, pady=15)
        
        # Scan UDID
        self.btn_scan = ctk.CTkButton(self.input_frame, text="SCAN ↻", command=self.auto_fetch_udid, width=100, fg_color="#333", hover_color="#555")
        self.btn_scan.grid(row=0, column=2, padx=10, pady=15)
        
        # --- Row 1: Local Plist File ---
        self.file_label = ctk.CTkLabel(self.input_frame, text="LOCAL PLIST:", font=("Roboto", 13, "bold"))
        self.file_label.grid(row=1, column=0, padx=15, pady=15, sticky="w")
        self.file_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Select local .plist file...", width=550, font=("Consolas", 12))
        self.file_entry.grid(row=1, column=1, padx=10, pady=15)
        self.btn_browse = ctk.CTkButton(self.input_frame, text="BROWSE", command=self.browse_file, width=100, fg_color="#444")
        self.btn_browse.grid(row=1, column=2, padx=10, pady=15)

        # --- Row 2: Target Path (Remote) ---
        self.path_label = ctk.CTkLabel(self.input_frame, text="TARGET PATH:", font=("Roboto", 13, "bold"))
        self.path_label.grid(row=2, column=0, padx=15, pady=15, sticky="w")
        self.path_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Path on iPhone (/private/var/...)", width=550, font=("Consolas", 12))
        self.path_entry.grid(row=2, column=1, padx=10, pady=15)
        # Auto Fill
        self.btn_autofill = ctk.CTkButton(self.input_frame, text="AUTO FILL", command=self.fill_default_path, width=100, fg_color="#d68f09", hover_color="#b57908")
        self.btn_autofill.grid(row=2, column=2, padx=10, pady=15)

        # ==================================================
        # 3. ACTION BUTTON
        # ==================================================
        self.btn_start = ctk.CTkButton(self, text="RUN EXPLOIT (EXECUTE run.py)", 
                                       font=("Consolas", 18, "bold"), height=60, fg_color="#b30000", hover_color="#800000",
                                       command=self.start_process)
        self.btn_start.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # ==================================================
        # 4. CONSOLE LOG (BIG FONT)
        # ==================================================
        self.log_box = ctk.CTkTextbox(self, font=("Consolas", 14), text_color="#00ff00", fg_color="black")
        self.log_box.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.log_box.configure(state="disabled")

        # ==================================================
        # 5. FOOTER CREDITS (UPDATED)
        # ==================================================
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=5, column=0, pady=(0, 15))
        
        credit_text = "Launcher by YangJiii   |   Special Thanks: Duy Tran & pengubow"
        self.label_credits = ctk.CTkLabel(self.footer_frame, text=credit_text, 
                                          font=("Arial", 13, "bold"), text_color="gray")
        self.label_credits.pack()

        # Setup Queue
        self.log_queue = queue.Queue()
        self.check_log_queue()
        
        self.after(500, self.auto_fetch_udid)

    def auto_fetch_udid(self):
        """Hàm tự động tìm UDID của thiết bị đang kết nối"""
        self.log("Scanning for devices...\n")
        try:
            if list_devices:
                devices = list_devices()
                if devices:
                    first_device = devices[0]
                    serial = first_device.serial
                    
                    self.udid_entry.delete(0, "end")
                    self.udid_entry.insert(0, serial)
                    self.log(f"Auto-detected Device: {serial}\n")
                else:
                    self.log("No device found. Please connect your iPhone.\n")
            else:
                self.log("Error: pymobiledevice3 not installed correctly.\n")
        except Exception as e:
            self.log(f"Scan Error: {str(e)}\n")

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Plist Files", "*.plist"), ("All Files", "*.*")])
        if filename:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filename)

    def fill_default_path(self):
        default = "/private/var/containers/Shared/SystemGroup/systemgroup.com.apple.mobilegestaltcache/Library/Caches/com.apple.MobileGestalt.plist"
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, default)

    def log(self, message):
        self.log_queue.put(message)

    def check_log_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(100, self.check_log_queue)

    def start_process(self):
        udid = self.udid_entry.get().strip()
        local_path = self.file_entry.get().strip()
        remote_path = self.path_entry.get().strip()

        if not udid or not local_path or not remote_path:
            self.log("ERROR: Please fill in ALL 3 fields (UDID, Local File, Target Path).\n")
            return

        if not os.path.exists("run.py"):
            self.log("ERROR: File 'run.py' not found in current folder!\n")
            return

        self.btn_start.configure(state="disabled", text="RUNNING...")
        self.log("=" * 40 + "\n")
        self.log(f"STARTING EXPLOIT...\n")
        self.log(f"UDID: {udid}\n")
        self.log("=" * 40 + "\n")

        t = threading.Thread(target=self.run_subprocess, args=(udid, local_path, remote_path))
        t.daemon = True
        t.start()

    def run_subprocess(self, udid, local_path, remote_path):
        cmd = [sys.executable, "run.py", udid, local_path, remote_path]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            for line in iter(process.stdout.readline, ''):
                self.log(line)

            process.stdout.close()
            return_code = process.wait()

            if return_code == 0:
                self.log("\n>>> SUCCESS: Exploit completed successfully. <<<\n")
            else:
                self.log(f"\n>>> FAILED: Process exited with code {return_code}. <<<\n")

        except Exception as e:
            self.log(f"\nCRITICAL ERROR: {str(e)}\n")
        finally:
            self.after(0, lambda: self.btn_start.configure(state="normal", text="RUN EXPLOIT (EXECUTE run.py)"))

if __name__ == "__main__":
    app = ExploitLauncher()
    app.mainloop()