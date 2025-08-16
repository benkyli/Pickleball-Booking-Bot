import requests
import json
from bs4 import BeautifulSoup

def createDateTime(year, month, day, time="00:00"):
    return f"{year}-{month}-{day}T{time}:00.000Z"

def getBookingPage(url, parametersWithDateAndTime):
    params = parametersWithDateAndTime
    resp = requests.get(url,) # params or header, not sure which is the correct one to input here.
    return

def getLandingPage():
    return


with open('data.json') as jsonData:
    data = json.load(jsonData)

# Might want error handling here

# Check desired date. I dunno, might not be necessary. 

loginPayload = {
    data["Email Field"] : data["User Email"]    
}

with requests.Session() as sess:
    pass