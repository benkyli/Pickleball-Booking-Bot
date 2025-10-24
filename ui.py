import tkinter as tk
from tkinter import messagebox
from bot import test_login, site_scrape
from datetime import date
from tkcalendar import Calendar
import webbrowser
import data_manager


class App(tk.Tk):
    def __init__(self, data_handler):
        super().__init__()
        # set data variables
        self.data_handler = data_handler

        # set window params and login status
        self.title("Pickleball Bot")
        self.geometry("750x750")
        self.user_email = None
        self.login_status = self.try_credentials()
        
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # set up frames
        self.frames = {}
        for F in (MainScreen, LoginScreen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        if self.login_status:
            self.show_frame("MainScreen")
        else:
            self.show_frame("LoginScreen")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        frame.update_content()

    def try_credentials(self):
        email = self.data_handler.get_value("User Email")
        password = self.data_handler.get_value("User Password")

        if email and password and test_login(email=email, password=password):  
            self.user_email = email
            return True
        else:
            return False
    
    def logout(self):
        self.user_email = None
        self.login_status = False

        self.data_handler.set_value("User Email", "") 
        self.data_handler.set_value("User Password", "")
        self.data_handler.save_data()
             
        self.show_frame("LoginScreen")
      
class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Login Screen")
        label.pack(padx=10, pady=10)

        # fields and submit button
        tk.Label(self, text="Email").pack()
        self.email_field = tk.Entry(self, width=30)
        self.email_field.pack()

        tk.Label(self, text="Password").pack()
        self.password_field = tk.Entry(self, width=30, show="*")
        self.password_field.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=20)

    def login(self):
        email = self.email_field.get()
        password = self.password_field.get()

        login_works = test_login(email=email, password=password)
        if login_works:
            self.controller.data_handler.set_value("User Email", email)
            self.controller.data_handler.set_value("User Password", password)
            self.controller.data_handler.save_data()

            # update user email for the controller 
            self.controller.user_email = email
            self.controller.login_status = True
            self.controller.show_frame("MainScreen")
        
        else:
            messagebox.showerror("Login Fail", f"Login failed. Please try again.")

    # just added to avoid missing method errors. Would make sense to have this frame inherit from a custom frame with an abstract method for this.
    def update_content(self):
        pass

class MainScreen(tk.Frame): 
    def __init__(self, parent, controller): # will need to **args this.
        super().__init__(parent)
        self.controller = controller
        self.logout_button_visible = False

        # header section showing login info
        header_frame = tk.Frame(self)
        header_frame.pack(side="top", fill="x", padx=5, pady=5)

        user_dropdown_frame = tk.Frame(header_frame, borderwidth=1, relief="solid")
        user_dropdown_frame.pack(side="right", padx=5)

        self.user_label = tk.Label(user_dropdown_frame, text="", cursor="hand2")
        self.user_label.pack()
        self.user_label.bind("<Button-1>", self.toggle_logout_button)
        
        self.logout_button = tk.Button(user_dropdown_frame, text="Log Out", command=self.controller.logout)

        # Body section
        body_frame = tk.Frame(self)
        body_frame.pack(pady=20)

        body_label = tk.Label(body_frame, text="Input your desired date and court time range")
        body_label.pack(pady=5)
        
        # Date input
        date_frame = tk.Frame(body_frame)
        date_frame.pack(pady=10)
        
        today = date.today()
        self.calendar = Calendar(date_frame, selectmode="day", mindate=today)
        self.calendar.pack()

        self.date_button = tk.Button(date_frame, text="Confirm Selected Date", command=self.show_selected_date)
        self.date_button.pack(pady=5)

        self.date_label = tk.Label(date_frame, text="", fg="green")
        self.date_label.pack()

        # Time range input
        time_frame = tk.Frame(body_frame)
        time_frame.pack(pady=10)

        self.times = [f"{hour:02d}:30" for hour in range(7,24)]
        self.start_time = tk.StringVar(time_frame) # may want to give default val. Prob shouldn't though
        self.end_time = tk.StringVar(time_frame)

        start_time_menu = tk.OptionMenu(time_frame, self.start_time, *self.times)
        start_time_menu.pack(side="left")
        tk.Label(time_frame, text="Start Time").pack(side="left", padx=5)

        end_time_menu = tk.OptionMenu(time_frame, self.end_time, *self.times) # might want to make it check the start time value and only do values after that.
        end_time_menu.pack(side="left")
        tk.Label(time_frame, text="End Time").pack(side="right", padx=5)

        self.time_button = tk.Button(body_frame, text="Confirm Time Range", command=self.show_time_range)
        self.time_button.pack()

        self.time_label = tk.Label(body_frame, text="", fg="green")
        self.time_label.pack(pady=5)

        # submit button
        submit_button_frame = tk.Frame(body_frame)
        submit_button_frame.pack(fill="x", pady=25)

        submit_button = tk.Button(submit_button_frame, text="Try Booking", command=self.scrape, relief="raised", borderwidth=3, bg="green", fg="white", padx=8, pady=5)
        submit_button.pack(side="right")

        # confirmation text and account schedule link
        self.in_progress_text = tk.Label(self, text="Bot waiting for 12:30", fg="red")

        self.confirmation_text = tk.Label(self, text="", fg="green")
      
        self.profile_link = tk.Label(self, text="https://cityofhamilton.perfectmind.com/39117/MyProfile/Contact", fg="blue", cursor="hand2")
        self.profile_link.bind("<Button-1>", self.open_link)

    def toggle_logout_button(self, event):
        if self.logout_button_visible:
            self.logout_button.pack_forget()
            self.logout_button_visible = False
        else:
            self.logout_button.pack(anchor="e")
            self.logout_button_visible = True

    def show_selected_date(self):
        selected_date = self.calendar.selection_get()
        self.date_label.config(text=f"Selected date: {selected_date}")
        
    def update_content(self):
        if self.controller.login_status:
            user_email = self.controller.user_email
            self.user_label.config(text= f"Logged in as {user_email}")
    
    def show_time_range(self):
        start_time = self.start_time.get()
        end_time = self.end_time.get()

        if start_time and end_time and self.valid_time_range(start_time, end_time):
            self.time_label.config(text=f"Selected Time Range: {start_time} - {end_time}")
           
        else:
            messagebox.showerror("Invalid Time Range", "Please input a start time earlier than the end time")

    def valid_time_range(self, start_time, end_time):
        start_index = self.times.index(start_time)
        end_index = self.times.index(end_time)
        
        if end_index > start_index:
            return True
        else:
            return False

    def scrape(self):
        # Need to do this to show that the bot is waiting.
        self.in_progress_text.pack()
        self.master.update()

        # The bot will ping the site when it's 12:30
        date = self.calendar.selection_get()
        start_time = self.start_time.get()
        end_time = self.end_time.get()

        if date and start_time and end_time and self.valid_time_range(start_time, end_time):
            scrape_successes = site_scrape(date, start_time, end_time)
            if scrape_successes > 0:
                self.in_progress_text.pack_forget()
                self.confirmation_text.config(text=f"Time slots booked: {scrape_successes}\n Please check your bookings at the link below")
                self.confirmation_text.pack()
                self.profile_link.pack()
        else:
            messagebox.showerror("Invalid Inputs", "Please ensure you have selected a date and valid time range")

    def open_link(self):
        webbrowser.open_new("https://cityofhamilton.perfectmind.com/39117/MyProfile/Contact")

if __name__ == "__main__":
    data_manager.load_data()
    if data_manager.data_loaded():
        app = App(data_manager)
        app.mainloop()
    else:
        print("no data file given with program")