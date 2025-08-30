import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver

import asyncio
import aiohttp

def createDateTime(year: str, month: str, day: str, time="00:00"):
    return f"{year}-{month}-{day}T{time}:00.000Z"

# Definitely delete later
def printDic(dic):
    for key in dic:
        print(key, ":", dic[key])

# May not be necessary; perhaps delete later
def getUserVerificationToken(url: str, sess):
    prebook = sess.get(url=url)
    soup = BeautifulSoup(prebook.text, "html.parser")
    requestVerificationToken = soup.find("input", {'name': '__RequestVerificationToken'})['value']
    return requestVerificationToken

def getEventURLs():
    # Prepare date and time values
    year = "2025"
    month = "08"
    day = "29"
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

    # Get event IDs and convert to urls
    eventIds = [court["EventId"] for court in courts]
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

async def get(sess: aiohttp.ClientSession, url: str):
    try:
        async with sess.get(url=url, timeout=5) as resp:
            if resp.status != 200:
                print(f"Response fail: {resp.status}")

            return resp

    except Exception as e:
        print(e)
    
# TODO: MUST test this thoroughly.
async def spamURLs(urls):
    async with aiohttp.ClientSession() as sess:
        
        # Log in
        login = await sess.post(url=data["Login URL"], data=loginPayload)
   
        # wanna repeat this a few times at 12:30
        if login:
            for i in range(1):
                print(i)
                results = await asyncio.gather(*[get(sess=sess, url=url) for url in urls])
            
        return results

# Spam the pages
def main():
    eventURLs = getEventURLs()
    test = asyncio.run(spamURLs(eventURLs))
    # check to see if we got the booking


    # then book it.

    # Then make it user friendly.

if __name__ == "__main__":
    main()
    
        
#     landingPage = r.url

#     # open this session into selenium
    # driver = webdriver.Firefox()
    # driver.get(url=data["Clean Booking Page URL"])
#     driver.implicitly_wait(3)
#     for c in sess.cookies:
#         driver.add_cookie({'name': c.name, 'value': c.value})
#     driver.implicitly_wait(10)
#     driver.get(url=r.url)
    
