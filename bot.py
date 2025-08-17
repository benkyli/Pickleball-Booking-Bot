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
    data["Email Field Name"] : data["User Email"],
    data["Password Field Name"] : data["User Password"]    
}

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36      (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}


with requests.Session() as sess:
    login = sess.post(data["Login URL"], data=loginPayload, headers=headers)
  
    # I guess here we would just do get requests for all the links of that day for our time slot. 
    url = "https://cityofhamilton.perfectmind.com/39117/Clients/BookMe4EventParticipants?eventId=3bdb4f73-e5f5-5c8b-adca-3c7b619a3c0e&occurrenceDate=20250818&widgetId=d63d746c-8862-4ca9-8b3c-5f79e841bba7&locationId=b83b0db1-8578-4056-a797-f24a053abd50&waitListMode=False"
    r = sess.get(url=url)
    print(r.url)