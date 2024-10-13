import tkinter as tk
from tkinter import ttk
from os import system
import threading,subprocess,time#timerEXE stuff
from ctypes import windll
from sys import argv
from os.path import isfile
import psutil
class TimerApp:
    def __init__(self, root,customTimerFile:str=None):
        self.stop_event = threading.Event()
        self.timer_thread = None
        self.process = None
        self.root = root
        self.root.geometry("300x200")
        self.center_window(self.root, 300, 200)
        self.is_running = False
        self.root.update_idletasks()  # Update to ensure the window is created
        self.root.attributes('-toolwindow', False)  # Ensure it appears on the taskbar
        self.root.attributes('-topmost',True)
        self.root.title("Sleep Timer")
        self.CustomTimerPath=customTimerFile
        # Remove native title bar and add a custom one
        self.root.overrideredirect(True)
        self.create_custom_titlebar()
        GWL_EXSTYLE=-20
        WS_EX_APPWINDOW=0x00040000
        WS_EX_TOOLWINDOW=0x00000080
        hwnd = windll.user32.GetParent(root.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        root.withdraw()
        root.after(10, lambda:root.wm_deiconify())

        # Configure dark mode theme
        self.style = ttk.Style()
        self.root.configure(bg='#000000')  # Set dark background for the window
        
        # Set a dark theme for ttk widgets
        self.style.theme_use('clam')
        self.style.configure("TFrame", background='#000000')
        self.style.configure("TLabel", background='#000000', foreground='#F0F0F0')
        self.style.configure("TSpinbox", background='#000000', foreground='#F0F0F0', fieldbackground='#000000')
        self.style.configure("TButton", background='#000000', foreground='#F0F0F0')
        self.style.configure("TOptionMenu", background='#000000', foreground='#F0F0F0', arrowcolor='#F0F0F0')

        # Validation command for spinboxes to keep values in range
        vcmd = (root.register(self.validate_spinbox), '%P', '%W')

        # Time frame (Hours : Minutes AM/PM)
        time_frame = ttk.Frame(root)
        time_frame.pack(pady=20)

        # Hours
        self.hour_var = tk.IntVar(value=12)
        self.hour_spinbox = ttk.Spinbox(
            time_frame, from_=1, to=12, textvariable=self.hour_var, width=3, font=("Arial", 16),
            validate='key', validatecommand=vcmd
        )
        self.hour_spinbox.grid(row=0, column=0, padx=5)

        # Colon :
        colon_label = ttk.Label(time_frame, text=":", font=("Arial", 16))
        colon_label.grid(row=0, column=1)

        # Minutes
        self.minute_var = tk.IntVar(value=0)
        self.minute_spinbox = ttk.Spinbox(
            time_frame, from_=0, to=59, textvariable=self.minute_var, width=3, font=("Arial", 16),
            validate='key', validatecommand=vcmd
        )
        self.minute_spinbox.grid(row=0, column=2, padx=5)

        # AM/PM Dropdown
        self.ampm_var = tk.StringVar(value="AM")
        ampm_dropdown = tk.OptionMenu(time_frame, self.ampm_var, "AM", "AM", "PM")
        ampm_dropdown.grid(row=0, column=3, padx=5)
        ampm_dropdown['menu'].configure(bg='black', fg='white')  # Dropdown menu color
        ampm_dropdown.configure(background='black', foreground='white')

        # Start/Stop Buttons
        self.start_button = ttk.Button(root, text="Start", command=self.start_timer)
        self.start_button.pack(fill=tk.X, padx=20, pady=5)

        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(fill=tk.X, padx=20, pady=5)

        # Button hover effects
        self.start_button.bind("<Enter>", lambda e: self.on_button_hover(self.start_button))
        self.start_button.bind("<Leave>", lambda e: self.on_button_leave(self.start_button))

        self.stop_button.bind("<Enter>", lambda e: self.on_button_hover(self.stop_button))
        self.stop_button.bind("<Leave>", lambda e: self.on_button_leave(self.stop_button))
    def start_timer(self):pass
    def stop_timer(self):pass
    def center_window(self, window, width, height,messagebox:bool=False):
        """Center the window on the screen."""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        if messagebox:
            x-=300
            y-=250
        window.geometry(f"{width}x{height}+{x}+{y}")

    def create_custom_titlebar(self):
        titlebar = tk.Frame(self.root, bg="#000000", relief='raised', bd=2)
        titlebar.pack(side=tk.TOP, fill=tk.X)

        # Title label
        title_label = tk.Label(titlebar, text="Timer App", bg="#000000", fg="white", font=("Arial", 12))
        title_label.pack(side=tk.LEFT, padx=10)

        # Close button
        close_button = tk.Button(titlebar, text="X", bg="#000000", fg="white", command=self.root.quit, bd=0)
        close_button.pack(side=tk.RIGHT, padx=5)

        # Bind drag functionality to move the window
        titlebar.bind("<Button-1>", self.start_move)
        titlebar.bind("<B1-Motion>", self.on_motion)
        titlebar.bind("<ButtonRelease-1>", self.stop_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        new_x = self.root.winfo_x() + deltax
        new_y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{new_x}+{new_y}")

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_button_hover(self, button):
        """Change the button background to white and text to black on hover."""
        button.config(style="Hover.TButton")
        self.style.configure("Hover.TButton", background='white', foreground='black')

    def on_button_leave(self, button):
        """Revert the button background and text color when the mouse leaves."""
        button.config(style="TButton")
        self.style.configure("TButton", background='#000000', foreground='#F0F0F0')
    

    def show_custom_messagebox(self, title, message):
        # Create a Toplevel window for the custom message box
        messagebox_window = tk.Toplevel(self.root)
        messagebox_window.title(title)
        messagebox_window.geometry("300x100")
        self.center_window(messagebox_window,300,100,True)
        messagebox_window.configure(bg='black')

        # Message label with white text on black background
        message_label = tk.Label(messagebox_window, text=message, bg='black', fg='white', font=("Arial", 12))
        message_label.pack(pady=20)

        # OK button to close the message box
        ok_button = ttk.Button(messagebox_window, text="OK", command=messagebox_window.destroy)
        ok_button.pack()
        ok_button.bind("<Enter>", lambda e: self.on_button_hover(ok_button))
        ok_button.bind("<Leave>", lambda e: self.on_button_leave(ok_button))

        # Make sure the message box is always on top
        messagebox_window.transient(self.root)
        messagebox_window.grab_set()
        self.root.wait_window(messagebox_window)


    def validate_spinbox(self, proposed_value, widget_name):
        # Validate that spinbox entries stay within their min/max range
        if widget_name.endswith('!spinbox'):
            spinbox_widget = self.root.nametowidget(widget_name)
            min_value = int(spinbox_widget.cget('from'))
            max_value = int(spinbox_widget.cget('to'))

            # Check if the proposed value is within the valid range
            if proposed_value.isdigit() and min_value <= int(proposed_value) <= max_value:
                return True
            elif proposed_value == "":  # Allow empty values for now
                return True
            else:
                return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False,False)
    app=TimerApp(root)
    root.mainloop()
