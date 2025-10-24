import sys
import os
import json

# after dealing with all this data stuff, I realize now that I should have just made the user log in every time instead of trying to keep a persistent login status. Super unnecessary when the user details are the only dynamic values.

def create_persistent_path(filename, persistent_path):
    # get data from temp folder
    temp_path = os.path.join(sys._MEIPASS, filename)
    try:
        with open(temp_path, "r") as f:
            data = json.load(f)
        
        # create persistent path
        with open(persistent_path, "w") as f:
            json.dump(data, f, indent=4)

        return True

    except FileNotFoundError:
        print("No file was bundled with the original program")
        return False

def get_write_path(filename):
    # we boot with executable
    if getattr(sys, "frozen", False):
        # check to see if persistent path exists
        persistent_path = os.path.join(os.path.dirname(sys.executable), filename) 
        if not os.path.exists(persistent_path):
            success = create_persistent_path(filename, persistent_path)
            if not success:
                return False
        return persistent_path

    else: # gives original file location when booting from terminal
        base_path = os.path.dirname(__file__) 
        return os.path.join(base_path, filename)


# Set up global data variables
filename="data.json"
data = {}
write_path = get_write_path(filename)

def load_data():
    global data
    if write_path:
        with open(write_path, "r") as f:
            data = json.load(f)   

    else:
        print("No data file was found")

def data_loaded():
    if data:
        return True
    else:
        return False
        
def save_data():
    with open(write_path, "w") as f:
        json.dump(data, f, indent=4)

def get_value(key):
    if key in data: # this key checking should be unnecessary since the app should only be requesting keys that we know exist; the user should have no way to do this. But this seems like something that would be good to include
        return data[key]
    else:
        return False

def set_value(key, value):
    if key in data:
        data[key] = value
    else:
        raise False