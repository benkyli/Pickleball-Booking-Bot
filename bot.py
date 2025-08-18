import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver


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

# needed if we want to switch to selenium for manual finish after. Automatic finish might need mix of beautifulSoup and requests instead. 
headers = {
"User-Agent":
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
}

with requests.Session() as sess:
    sess.headers.update(headers)
    login = sess.post(data["Login URL"], data=loginPayload)
  
    # I guess here we would just do get requests for all the links of that day for our time slot. 
    url = "https://cityofhamilton.perfectmind.com/39117/Clients/BookMe4EventParticipants?eventId=d0965f5a-a4f3-466a-83ce-121ff74e8d6a&occurrenceDate=20250819&widgetId=d63d746c-8862-4ca9-8b3c-5f79e841bba7&locationId=b83b0db1-8578-4056-a797-f24a053abd50&waitListMode=False"
    r = sess.get(url=url)
    
    landingPage = r.url

    # open this session into selenium
    driver = webdriver.Firefox()
    driver.get(url=data["Clean Booking Page URL"])
    driver.implicitly_wait(3)
    for c in sess.cookies:
        driver.add_cookie({'name': c.name, 'value': c.value})
    driver.implicitly_wait(10)
    driver.get(url=r.url)
    