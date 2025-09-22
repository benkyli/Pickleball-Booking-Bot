import tkinter as tk
from tkinter import messagebox
from bot import test_login
import json

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # set window params and login status
        self.title("Pickleball Bot")
        self.geometry("500x500")
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
            self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        frame.update_content()

    def try_credentials(self):
        with open("data.json", "r") as f:
            data = json.load(f)
            email = data["User Email"]
            password = data["User Password"]

        if email and password and test_login(email=email, password=password):  
            self.user_email = email
            return True
        else:
            return False
    
    def logout(self):
        self.user_email = None
        self.login_status = False

        with open("data.json") as f:
            data = json.load(f)
            data["User Email"] = ""
            data["User Password"] = ""
            
        with open("data.json", "w") as f:
            json.dump(data, f)   

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
            with open("data.json") as f:
                data = json.load(f)
                data["User Email"] = email
                data["User Password"] = password

            with open("data.json", "w") as f:
                json.dump(data, f)

            # update user email attribute for the controller 
            self.controller.user_email = email
            self.controller.login_status = True
            self.controller.show_frame("MainScreen")
        
        else:
            tk.messagebox.showerror("Login Fail", f"Login failed. Please try again.")

    # just added to avoid missing method errors. Would make sense to have this frame inherit from a custom frame with an abstract method for this.
    def update_content(self):
        pass

    # add handler to show password



class MainScreen(tk.Frame): 
    def __init__(self, parent, controller): # will need to **args this.
        super().__init__(parent)
        self.controller = controller
        self.logout_button_visible = False

        # header section showing tab purpose and login info
        header_frame = tk.Frame(self)
        header_frame.pack(side="top", fill="x")

        tab_label = tk.Label(header_frame, text="Choose when you want to book the court")
        tab_label.pack(side="left")

        self.user_label = tk.Label(header_frame, text="", cursor="hand2")
        self.user_label.pack(side="right")
        self.user_label.bind("<Button-1>", self.toggle_logout_button)
        
        self.logout_button = tk.Button(self, text="Log Out", command=self.controller.logout)

        # buttons showing book now and book at 12:30

    def toggle_logout_button(self, event):
        if self.logout_button_visible:
            self.logout_button.pack_forget()
            self.logout_button_visible = False
        else:
            self.logout_button.pack()
            self.logout_button_visible = True
        
    def update_content(self):
        if self.controller.login_status:
            user_email = self.controller.user_email
            self.user_label.config(text= f"Logged in as {user_email}")

        # Ensure the logout button is not visible when the screen is first loaded.
        # self.logout_button.pack_forget()
        # self.logout_button_visible = False


class scrapeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        # have fields for date, time range.
        # have option to do now or at specific time. Maybe have a little highlight that explains the diff.
        
if __name__ == "__main__":
    app = App()
    app.mainloop()