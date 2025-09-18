import tkinter as tk
from bot import testLogin

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pickleball Bot")
        self.geometry("500x500")
        
        # needs an indicator to see if you have a user registered. 

        def CheckLogin(self):
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
        self.yay = 3

        # have user field,

        # have password field

        # have submit. Submit might just be the checklogin from before. Except this time
        # If success, write user ans password to file, return main page
        # else, give an error to try again. Stay on this page. 

class scrapeScreen(tk.Frame):
    def __init__(self, parent, controller)