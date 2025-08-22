import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from seleniumrequests import Firefox

def createDateTime(year, month, day, time="00:00"):
    return f"{year}-{month}-{day}T{time}:00.000Z"

# Definitely delete later
def printDic(dic):
    for key in dic:
        print(key, ":", dic[key])

# May not be necessary; perhaps delete later
def getUserVerificationToken(url):
    prebook = sess.get(url=url)
    soup = BeautifulSoup(prebook.text, "html.parser")
    requestVerificationToken = soup.find("input", {'name': '__RequestVerificationToken'})['value']
    return requestVerificationToken

def getEventURLs():
    # Prepare date and time values
    year = "2025"
    month = "08"
    day = "24"
    startTime = "17:30"
    endTime = "20:30"

    # Set date-time parameters in dictionary
    date = createDateTime(year=year, month=month, day=day, time="00:00") # time doesn't matter for date parameter
    startTime = createDateTime(year=year, month=month, day=day, time=startTime) # day doesn't matter for the time parameter
    endTime = createDateTime(year=year, month=month, day=day, time=endTime)

    dateTimeData = data["DateTime Payload Form Encoded"]
    dateTimeData[data["Start Date Key"]] = date # start date and end date are the same because bookings are always taken 2 days in advance, so you don't get opportunities to do other days.
    dateTimeData[data["End Date Key"]] = date
    dateTimeData[data["Start Time Key"]] = startTime
    dateTimeData[data["End Time Key"]] = endTime

    # Get the updated Page
    bookingPage = requests.post(url=data["Booking URL Updated"], data=dateTimeData)
    courts = bookingPage.json()["classes"]

    # Get event IDs
    eventIds = []
    for court in courts:
        eventIds.append(court["EventId"])

    # convert to urls
    eventURLs = [f"https://cityofhamilton.perfectmind.com/Clients/BookMe4EventParticipants?eventId={eventId}" for eventId in eventIds]
    
    return eventURLs

with open('data.json') as jsonData:
    data = json.load(jsonData)

loginPayload = {
    data["Email Field Name"] : data["User Email"],
    data["Password Field Name"] : data["User Password"]    
}

# needed if we want to switch to selenium for manual finish after. Automatic finish might need mix of beautifulSoup and requests instead. 
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0'
}

with requests.Session() as sess:
    # might want to put date time inputs here. makes the most sense.
    eventURLs = getEventURLs()
    
    # Log in
    sess.headers.update(headers)
    sess.post(data["Login URL"], data=loginPayload)

    while True:
        for i, url in enumerate(eventURLs):
            reserve = sess.get(url=url)
            print(i)

    
        
#     landingPage = r.url

#     # open this session into selenium
    # driver = webdriver.Firefox()
    # driver.get(url=data["Clean Booking Page URL"])
#     driver.implicitly_wait(3)
#     for c in sess.cookies:
#         driver.add_cookie({'name': c.name, 'value': c.value})
#     driver.implicitly_wait(10)
#     driver.get(url=r.url)
    
