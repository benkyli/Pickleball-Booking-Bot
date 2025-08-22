import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
from seleniumrequests import Firefox

def createDateTime(year, month, day, time="00:00"):
    return f"{year}-{month}-{day}T{time}:00.000Z"

# This would loop through the data from the booking page to get all the landing pages. Maybe could also get the holding pages, but could also get those in a different function.
def getLandingPage():
    return

def printDic(dic):
    for key in dic:
        print(key, ":", dic[key])

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

todayDay = f"{datetime.datetime.today().day:02}" # turn date integer into 2 digit string with leading 0's if necessary

with requests.Session() as sess:
    sess.headers.update(headers)
    sess.post(url=data["Login URL"], data=loginPayload)

    # Prepare date and time request data 
    year = "2025"
    month = "08"
    day = "24"
    startTime = "17:30"
    endTime = "20:30"

    # Set time parameters in dictionary
    startDate = createDateTime(year=year, month=month, day=day, time="00:00")
    endDate = startDate
    startTime = createDateTime(year=year, month=month, day=todayDay, time=startTime)
    endTime = createDateTime(year=year, month=month, day=todayDay, time=endTime)

    dateTimeData = data["DateTime Payload Form Encoded"]
    dateTimeData[data["Start Date Key"]] = startDate
    dateTimeData[data["End Date Key"]] = startDate
    dateTimeData[data["Start Time Key"]] = startTime
    dateTimeData[data["End Time Key"]] = endTime

    # Get default page's verification token
    prebook = sess.get(url=data["Booking Page URL"])
    soup = BeautifulSoup(prebook.text, "html.parser")
    requestVerificationToken = soup.find("input", {'name': '__RequestVerificationToken'})['value']
    dateTimeData["__RequestVerificationToken"] = requestVerificationToken

    # Get the updated Page
    bookingPage = sess.post(url=data["Booking URL Updated"], data=dateTimeData)
   
    courts = bookingPage.json()["classes"]
    print(len(courts))
    
    


    # Get all elements for given days and times. 



    

#     # Get all landing pages for desired date and time range
  
#     # I guess here we would just do get requests for all the links of that day for our time slot. 
#     url = "https://cityofhamilton.perfectmind.com/39117/Clients/BookMe4EventParticipants?eventId=d0965f5a-a4f3-466a-83ce-121ff74e8d6a&occurrenceDate=20250819&widgetId=d63d746c-8862-4ca9-8b3c-5f79e841bba7&locationId=b83b0db1-8578-4056-a797-f24a053abd50&waitListMode=False"
#     r = sess.get(url=url)
    
#     landingPage = r.url

#     # open this session into selenium
    # driver = webdriver.Firefox()
    # driver.get(url=data["Clean Booking Page URL"])
#     driver.implicitly_wait(3)
#     for c in sess.cookies:
#         driver.add_cookie({'name': c.name, 'value': c.value})
#     driver.implicitly_wait(10)
#     driver.get(url=r.url)
    
