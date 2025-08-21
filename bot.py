import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver

def createDateTime(year, month, day, time="00:00"):
    return f"{year}-{month}-{day}T{time}:00.000Z"

# This probably doesn't need to be a function
def getBookingPage(url, dateTimeData):
    resp = requests.post(url, data=dateTimeData) 
    return resp

# This would loop through the data from the booking page to get all the landing pages. Maybe could also get the holding pages, but could also get those in a different function.
def getLandingPage():
    return


with open('data.json') as jsonData:
    data = json.load(jsonData)

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
    # sess.headers.update(headers)
    # login = sess.post(url=data["Login URL"], data=loginPayload)

    # Set date and time request data 
    year = "2025"
    month = "08"
    day = "23"
    startTime = "00:00"
    endTime = "12:30"

    dateTimeData = data["Open Courts Request Data"]
    dateTimeData["Start Date Key"] = createDateTime(year=year, month=month, day=day, time="00:00")
    dateTimeData["End Date Key"] = dateTimeData["Start Date Key"]

    # might need to change so the date part is current day. Not sure. Need to check what the responses are in the html. 
    dateTimeData["Start Time Key"] = createDateTime(year=year, month=month, day=day, time=startTime)
    dateTimeData["End Time Key"] = createDateTime(year=year, month=month, day=day, time=endTime)
    
    bookingPage = sess.post(url=data["Clean Booking Page URL"], data=dateTimeData)
    soup = BeautifulSoup(bookingPage.content, "html.parser")

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
    
