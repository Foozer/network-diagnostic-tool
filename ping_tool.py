import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import re
import socket
from datetime import datetime
import os

class PingTracerouteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Diagnostic Tool")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Set icon if available
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Configure style
        self.setup_styles()
        
        # Create main container
        self.main_frame = ttk.Frame(root, style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        self.create_header()
        
        # Create input section
        self.create_input_section()
        
        # Create buttons section
        self.create_buttons_section()
        
        # Create results section
        self.create_results_section()
        
        # Initialize variables
        self.is_running = False
        self.current_process = None
        
    def setup_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Main.TFrame', background='#2b2b2b')
        style.configure('Header.TLabel', 
                       background='#2b2b2b', 
                       foreground='#00ff88', 
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Input.TFrame', background='#3c3c3c')
        style.configure('Input.TLabel', 
                       background='#3c3c3c', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 10))
        style.configure('Input.TEntry', 
                       fieldbackground='#4a4a4a', 
                       foreground='#ffffff',
                       borderwidth=2,
                       relief='solid')
        
        # Configure radio button styles
        style.configure('Radio.TRadiobutton',
                       background='#3c3c3c',
                       foreground='#ffffff',
                       font=('Segoe UI', 10))
        style.map('Radio.TRadiobutton',
                 background=[('selected', '#00ff88'), ('active', '#4a4a4a')],
                 foreground=[('selected', '#000000'), ('active', '#ffffff')])
        
        style.configure('Button.TButton', 
                       background='#00ff88', 
                       foreground='#000000',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Button.TButton',
                 background=[('active', '#00cc6a'), ('pressed', '#00994d')])
        
        style.configure('Results.TFrame', background='#3c3c3c')
        style.configure('Results.TLabel', 
                       background='#3c3c3c', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 10, 'bold'))
        
    def create_header(self):
        """Create the application header"""
        header_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="🌐 Network Diagnostic Tool", 
                               style='Header.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Ping and Traceroute Network Analysis", 
                                  style='Input.TLabel',
                                  font=('Segoe UI', 12))
        subtitle_label.pack(pady=(5, 0))
        
    def create_input_section(self):
        """Create the input section for IP address"""
        input_frame = ttk.Frame(self.main_frame, style='Input.TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # IP Address input
        ip_frame = ttk.Frame(input_frame, style='Input.TFrame')
        ip_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ip_label = ttk.Label(ip_frame, text="Target IP Address or Hostname:", style='Input.TLabel')
        ip_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.ip_entry = ttk.Entry(ip_frame, style='Input.TEntry', font=('Segoe UI', 12))
        self.ip_entry.pack(fill=tk.X, pady=(0, 10))
        self.ip_entry.insert(0, "8.8.8.8")  # Default to Google DNS
        
        # Ping count input
        ping_frame = ttk.Frame(input_frame, style='Input.TFrame')
        ping_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ping_label = ttk.Label(ping_frame, text="Number of Ping Packets:", style='Input.TLabel')
        ping_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.ping_count = tk.StringVar(value="4")
        ping_count_frame = ttk.Frame(ping_frame, style='Input.TFrame')
        ping_count_frame.pack(fill=tk.X)
        
        for i, count in enumerate(["1", "4", "8", "10", "∞"]):
            rb = ttk.Radiobutton(ping_count_frame, 
                                text=count, 
                                variable=self.ping_count, 
                                value=count,
                                style='Radio.TRadiobutton')
            rb.pack(side=tk.LEFT, padx=(0, 20))
        
    def create_buttons_section(self):
        """Create the buttons section"""
        buttons_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Button container
        button_container = ttk.Frame(buttons_frame, style='Main.TFrame')
        button_container.pack()
        
        # Ping button
        self.ping_button = ttk.Button(button_container, 
                                     text="🔍 Ping Test", 
                                     style='Button.TButton',
                                     command=self.start_ping)
        self.ping_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Traceroute button
        self.trace_button = ttk.Button(button_container, 
                                      text="🛤️ Traceroute", 
                                      style='Button.TButton',
                                      command=self.start_traceroute)
        self.trace_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.clear_button = ttk.Button(button_container, 
                                      text="🗑️ Clear Results", 
                                      style='Button.TButton',
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(button_container, 
                                     text="⏹️ Stop", 
                                     style='Button.TButton',
                                     command=self.stop_operations,
                                     state='disabled')
        self.stop_button.pack(side=tk.LEFT)
        
    def create_results_section(self):
        """Create the results display section"""
        results_frame = ttk.Frame(self.main_frame, style='Results.TFrame')
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results header
        results_header = ttk.Label(results_frame, 
                                  text="📊 Results", 
                                  style='Results.TLabel',
                                  font=('Segoe UI', 14, 'bold'))
        results_header.pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            bg='#1e1e1e',
            fg='#00ff88',
            font=('Consolas', 10),
            insertbackground='#00ff88',
            selectbackground='#404040',
            relief='flat',
            borderwidth=0
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(results_frame, 
                                   textvariable=self.status_var,
                                   style='Results.TLabel',
                                   font=('Segoe UI', 9))
        self.status_bar.pack(fill=tk.X, padx=20, pady=(0, 10))
        
    def validate_ip(self, ip):
        """Validate IP address or hostname"""
        if not ip.strip():
            return False, "Please enter an IP address or hostname"
        
        # Check if it's a valid IP address
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ip_pattern, ip):
            return True, ""
        
        # Check if it's a valid hostname
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if re.match(hostname_pattern, ip):
            return True, ""
        
        return False, "Invalid IP address or hostname format"
    
    def start_ping(self):
        """Start ping operation in a separate thread"""
        if self.is_running:
            messagebox.showwarning("Warning", "Another operation is already running!")
            return
        
        target = self.ip_entry.get().strip()
        is_valid, error_msg = self.validate_ip(target)
        
        if not is_valid:
            messagebox.showerror("Error", error_msg)
            return
        
        self.is_running = True
        self.update_buttons_state()
        self.status_var.set("Running ping test...")
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"🔍 Pinging {target}...\n")
        self.results_text.insert(tk.END, f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Start ping in separate thread
        thread = threading.Thread(target=self.run_ping, args=(target,))
        thread.daemon = True
        thread.start()
    
    def run_ping(self, target):
        """Execute ping command"""
        try:
            count = self.ping_count.get()
            
            # Handle unlimited pings
            if count == "∞":
                command = ['ping', '-t', target]  # -t flag for continuous ping
            else:
                command = ['ping', '-n', count, target]
            
            creationflags = 0
            if os.name == 'nt':
                creationflags = subprocess.CREATE_NO_WINDOW
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=creationflags
            )
            
            # Store process reference for stopping
            self.current_process = process
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.root.after(0, self.update_results, output)
                    
                # Check if operation was stopped
                if not self.is_running:
                    process.terminate()
                    self.root.after(0, self.update_results, "\n⏹️ Ping stopped by user\n")
                    break
            
            # Get final result only if not stopped
            if self.is_running:
                return_code = process.poll()
                if return_code == 0:
                    self.root.after(0, self.update_results, "\n✅ Ping completed successfully!\n")
                else:
                    self.root.after(0, self.update_results, "\n❌ Ping failed!\n")
                    
        except Exception as e:
            self.root.after(0, self.update_results, f"\n❌ Error: {str(e)}\n")
        finally:
            self.current_process = None
            self.root.after(0, self.finish_operation)
    
    def start_traceroute(self):
        """Start traceroute operation in a separate thread"""
        if self.is_running:
            messagebox.showwarning("Warning", "Another operation is already running!")
            return
        
        target = self.ip_entry.get().strip()
        is_valid, error_msg = self.validate_ip(target)
        
        if not is_valid:
            messagebox.showerror("Error", error_msg)
            return
        
        self.is_running = True
        self.update_buttons_state()
        self.status_var.set("Running traceroute...")
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"🛤️ Traceroute to {target}...\n")
        self.results_text.insert(tk.END, f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Start traceroute in separate thread
        thread = threading.Thread(target=self.run_traceroute, args=(target,))
        thread.daemon = True
        thread.start()
    
    def run_traceroute(self, target):
        """Execute traceroute command"""
        try:
            command = ['tracert', target]
            creationflags = 0
            if os.name == 'nt':
                creationflags = subprocess.CREATE_NO_WINDOW
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=creationflags
            )
            
            # Store process reference for stopping
            self.current_process = process
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.root.after(0, self.update_results, output)
                    
                # Check if operation was stopped
                if not self.is_running:
                    process.terminate()
                    self.root.after(0, self.update_results, "\n⏹️ Traceroute stopped by user\n")
                    break
            
            # Get final result only if not stopped
            if self.is_running:
                return_code = process.poll()
                if return_code == 0:
                    self.root.after(0, self.update_results, "\n✅ Traceroute completed successfully!\n")
                else:
                    self.root.after(0, self.update_results, "\n❌ Traceroute failed!\n")
                    
        except Exception as e:
            self.root.after(0, self.update_results, f"\n❌ Error: {str(e)}\n")
        finally:
            self.current_process = None
            self.root.after(0, self.finish_operation)
    
    def update_results(self, text):
        """Update the results text area"""
        self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Ready")
    
    def stop_operations(self):
        """Stop running operations"""
        self.is_running = False
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass
        self.status_var.set("Operation stopped by user")
        self.update_buttons_state()
    
    def update_buttons_state(self):
        """Update button states based on running status"""
        if self.is_running:
            self.ping_button.config(state='disabled')
            self.trace_button.config(state='disabled')
            self.stop_button.config(state='normal')
        else:
            self.ping_button.config(state='normal')
            self.trace_button.config(state='normal')
            self.stop_button.config(state='disabled')
    
    def finish_operation(self):
        """Called when an operation finishes"""
        self.is_running = False
        self.status_var.set("Ready")
        self.update_buttons_state()

def main():
    root = tk.Tk()
    app = PingTracerouteApp(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 