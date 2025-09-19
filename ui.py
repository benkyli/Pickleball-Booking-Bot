import tkinter as tk
from bot import testLogin

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # window params
        self.title("Pickleball Bot")
        self.geometry("500x500")
        
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        def check_login(self):
            with open("data.json", "r") as data:
                email = data["User Email"]
                password = data["User Password"]
            if email and password:
                if testLogin(email=email, password=password):
                    return # then put a login screen ui. self.show_frame("nameOfFrame")
                else:
                    return # login screen
            else:
                return # put an error code or something, or just ask to try again. Same as above, but with other name
            

class MainScreen(tk.Frame):
    def __init__(self, parent, controller, user):

        # have a section showing user logged in
        # Allow user to logout if wrong user. Logout should clear the user and password from the file.

        # have button for going to scrape screen
        self.yay = 1

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
        self.password_field = tk.Entry(self, width=30, show="*").pack(pady=5)
        self.password_field.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=20)

    def login(self):
        email = self.email_entry.get()
        password = self.password_field.get()

    # add handler to show password


        # have submit. Submit might just be the checklogin from before. Except this time
        # If success, write user ans password to file, return main page
        # else, give an error to try again. Stay on this page. 

        # if fail
        # tk.messagebox.showinfo("Success", f"First Field: ")


class scrapeScreen(tk.Frame):
    def __init__(self, parent, controller):
        self.juum = 3
        # have fields for date, time range.
        # have option to do now or at specific time. Maybe have a little highlight that explains the diff.
        