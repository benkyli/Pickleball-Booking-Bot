import requests
import json

with open('data.json') as jsonData:
    data = json.load(jsonData)

# Might want error handling here

# Check desired date. I dunno, might not be necessary. 

loginPayload = {
    data["Email Field"] : data["User Email"]    
}

with requests.Session() as sess:
    pass