import tkinter as tk
from tkinter import ttk
from os import system
import threading, subprocess, time
from ctypes import windll
from sys import argv
from os.path import isfile
import psutil
class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, bg, text, text_color, command=None):
        tk.Canvas.__init__(self, parent, borderwidth=0, relief="flat", highlightthickness=0, bg=bg)
        self.command = command
        self.text = text  # Store text as an attribute
        self.bg = bg  # Store background color
        
        if cornerradius > 0.5*width:
            print("Error: cornerradius is greater than width.")
            return None

        if cornerradius > 0.5*height:
            print("Error: cornerradius is greater than height.")
            return None

        rad = 2*cornerradius
        self.default_color = color  # Default color for button
        self.pressed_color = "#1e90ff"  # Color when button is pressed

        self.shape()
        (x0, y0, x1, y1) = self.bbox("all")
        width = (x1-x0)
        height = (y1-y0)
        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def shape(self):
        """Draw the rounded button shape and border."""
        self.create_polygon(
            (5, self.winfo_height()-25, 5, 25,
             25, 5, self.winfo_width()-25, 5,
             self.winfo_width()-5, 25, self.winfo_width()-5, self.winfo_height()-25,
             25, self.winfo_height()-5),
            fill=self.default_color, outline="white"
        )
        self.create_oval(5, 5, self.winfo_width()-5, self.winfo_height()-5, outline="white", width=2)
        self.update_text()

    def _on_press(self, event):
        self.configure(bg=self.default_color)  # Keep background color black
        self.shape()  # Redraw the shape
        self.create_polygon(
            (5, self.winfo_height()-25, 5, 25,
             25, 5, self.winfo_width()-25, 5,
             self.winfo_width()-5, 25, self.winfo_width()-5, self.winfo_height()-25,
             25, self.winfo_height()-5),
            fill=self.pressed_color, outline="white"
        )
        self.update_text()  # Reapply text

    def _on_release(self, event):
        self.configure(bg="black")  # Keep background color black
        self.shape()  # Redraw the shape
        self.update_text()  # Reapply text
        if self.command is not None:
            self.command()

    def set_text(self, text):
        self.text = text
        self.update_text()

    def update_text(self):
        self.delete("text")
        width = self.winfo_width()
        height = self.winfo_height()
        font_size = int(height // 3)
        self.create_text(width // 2, height // 2, text=self.text, fill="white", font=("Arial", font_size), tags="text")

    def on_resize(self):
        """Handle button resize and update its appearance."""
        self.delete("all")
        self.shape()
        self.update_text()

class TimerApp:
    def __init__(self, root, customTimerFile: str = None):
        self.stop_event = threading.Event()
        self.timer_thread = None
        self.process = None
        self.root = root
        self.root.geometry("400x600")  # Adjusted size to fit circular buttons
        self.center_window(self.root, 400, 400)
        self.is_running = False
        self.root.update_idletasks()
        self.root.attributes('-toolwindow', False)
        self.root.attributes('-topmost', True)
        self.root.title("Sleep Timer")
        self.CustomTimerPath = customTimerFile

        self.root.overrideredirect(True)
        self.create_custom_titlebar()
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = windll.user32.GetParent(root.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        root.withdraw()
        root.after(10, lambda: root.wm_deiconify())

        self.style = ttk.Style()
        self.root.configure(bg='#000000')

        self.style.theme_use('clam')
        self.style.configure("TFrame", background='#000000')
        self.style.configure("TLabel", background='#000000', foreground='#F0F0F0')
        self.style.configure("TSpinbox", background='#000000', foreground='#F0F0F0', fieldbackground='#000000')
        self.style.configure("TButton", background='#000000', foreground='#F0F0F0')
        self.style.configure("TOptionMenu", background='#000000', foreground='#F0F0F0', arrowcolor='#F0F0F0')

        vcmd = (root.register(self.validate_spinbox), '%P', '%W')

        time_frame = ttk.Frame(root)
        time_frame.pack(pady=10)

        self.hour_var = tk.IntVar(value=12)
        self.hour_spinbox = ttk.Spinbox(
            time_frame, from_=1, to=12, textvariable=self.hour_var, width=3, font=("Arial", 16),
            validate='key', validatecommand=vcmd
        )
        self.hour_spinbox.grid(row=0, column=0, padx=5)

        colon_label = ttk.Label(time_frame, text=":", font=("Arial", 16))
        colon_label.grid(row=0, column=1)

        self.minute_var = tk.IntVar(value=0)
        self.minute_spinbox = ttk.Spinbox(
            time_frame, from_=0, to=59, textvariable=self.minute_var, width=3, font=("Arial", 16),
            validate='key', validatecommand=vcmd
        )
        self.minute_spinbox.grid(row=0, column=2, padx=5)

        self.ampm_var = tk.StringVar(value="AM")
        ampm_dropdown = tk.OptionMenu(time_frame, self.ampm_var, "AM", "AM", "PM")
        ampm_dropdown.grid(row=0, column=3, padx=5)
        ampm_dropdown['menu'].configure(bg='black', fg='white')
        ampm_dropdown.configure(background='black', foreground='white')

        self.day_buttons_frame = ttk.Frame(root)
        self.day_buttons_frame.pack(pady=10)

        self.create_weekday_buttons()

        self.start_button = tk.Button(root, text="Start", command=self.start_timer,font=("Arial",18),fg="white",bg="black")
        self.start_button.pack(fill=tk.X, padx=20, pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_timer, state=tk.DISABLED,font=("Arial",18),fg="white",bg="black")
        self.stop_button.pack(fill=tk.X, padx=20, pady=5)

        self.start_button.bind("<Enter>", lambda e: self.on_button_hover(self.start_button))
        self.start_button.bind("<Leave>", lambda e: self.on_button_leave(self.start_button))

        self.stop_button.bind("<Enter>", lambda e: self.on_button_hover(self.stop_button))
        self.stop_button.bind("<Leave>", lambda e: self.on_button_leave(self.stop_button))

        self.root.bind("<Configure>", self.on_resize)

        # Enable dragging
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.on_motion)
        self.root.bind("<ButtonRelease-1>", self.stop_move)

    def center_window(self, window, width, height, messagebox: bool = False):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        if messagebox:
            x -= 300
            y -= 250
        window.geometry(f"{width}x{height}+{x}+{y}")

    def create_weekday_buttons(self):
        """Create circular buttons for the days of the week."""
        button_frame = tk.Frame(self.root, bg="black")  # Use tk.Frame instead of ttk.Frame
        button_frame.pack(pady=20, fill=tk.X)

        # List of day initials
        days = ["S", "M", "T", "W", "T", "F", "S"]

        # Calculate button size based on the window width
        width = self.root.winfo_width()
        button_size = width // 7  # Ensure 7 buttons fit horizontally
        self.day_buttons = []

        for day in days:
            # Create rounded buttons for each day with black background and white text
            button = RoundedButton(
                button_frame, width=button_size, height=button_size,
                cornerradius=button_size // 2, padding=5,
                color="black", text_color="white", bg="black", text=day,
                command=lambda d=day: self.on_day_button_click(d)
            )

            button.pack(side=tk.LEFT, padx=0)  # Set padx to 0 to fit the screen

            self.day_buttons.append(button)

    def on_day_button_click(self, day, event=None):
        """Handle day button click event."""
        print(f"Button {day} clicked!")

    def start_timer(self):
        """Start the sleep timer."""
        if self.is_running:
            return

        hour = self.hour_var.get()
        minute = self.minute_var.get()
        ampm = self.ampm_var.get()
        

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_running = True

    def run_timer(self, seconds):
        """Run the timer for the specified seconds."""
        time.sleep(seconds)
        if not self.stop_event.is_set():
            self.show_timer_expired_message()

    def show_timer_expired_message(self):
        """Show a message box when the timer expires."""
        self.root.after(0, lambda: tk.messagebox.showinfo("Timer", "Time's up!"))
        # Run the timer executable (custom logic needed)
        if self.CustomTimerPath and isfile(self.CustomTimerPath):
            self.process = subprocess.Popen([self.CustomTimerPath], creationflags=subprocess.CREATE_NEW_CONSOLE)

    def stop_timer(self):
        """Stop the timer."""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.is_running = False

    def validate_spinbox(self, new_value, widget):
        """Validate spinbox input."""
        if new_value == "":
            return True
        try:
            int_value = int(new_value)
            if 0 <= int_value <= 59 and widget == self.minute_spinbox:
                return True
            elif 1 <= int_value <= 12 and widget == self.hour_spinbox:
                return True
        except ValueError:
            return False
        return False

    def on_button_hover(self, button):
        """Change button color on hover."""
        button.configure(background='gray')

    def on_button_leave(self, button):
        """Reset button color when leaving hover."""
        button.configure(background='black')

    def create_custom_titlebar(self):
        """Create a custom title bar."""
        title_bar = tk.Frame(self.root, bg='black', relief='raised', height=30)
        title_bar.pack(fill=tk.X, side=tk.TOP)

        # Title label
        title_label = tk.Label(title_bar, text="Sleep Timer", bg='black', fg='white', font=("Arial", 12))
        title_label.pack(side=tk.LEFT, padx=10)

        # Close button
        close_button = tk.Button(title_bar, text="X", command=self.root.quit, bg='black', fg='white', font=("Arial", 10), relief='flat')
        close_button.pack(side=tk.RIGHT, padx=5)

    def start_move(self, event):
        """Initiate dragging of the window."""
        self.x = event.x
        self.y = event.y

    def on_motion(self, event):
        """Move the window during dragging."""
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        self.root.geometry(f"+{self.root.winfo_x() + delta_x}+{self.root.winfo_y() + delta_y}")

    def stop_move(self, event):
        """Stop dragging the window."""
        self.x = None
        self.y = None

    def on_resize(self, event):
        """Adjust the day buttons horizontally on window resize."""
        width = self.root.winfo_width()
        button_size = width // 7  # Make buttons fit horizontally based on window size

        for button in self.day_buttons:
            button.configure(width=button_size, height=button_size)
            button.update_text()  # Update text size and position

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
