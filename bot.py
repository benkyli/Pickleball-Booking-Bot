import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import asyncio
import aiohttp
import time
import os
import re

with open('data.json') as jsonData:
    data = json.load(jsonData)

loginPayload = {
    data["Email Field Name"] : data["User Email"],
    data["Password Field Name"] : data["User Password"]    
}

# Allows us to swap to selenium if necessary and may help against bot detection
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0'
}


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
    requestVerificationToken = soup.find("input", name='__RequestVerificationToken')['value']
    return requestVerificationToken

def getEventURLs():
    # Prepare date and time values
    year = "2025"
    month = "09"
    day = "06"
    startTime = "13:30"
    endTime = "14:30"

    # Set date-time parameters in dictionary
    date = createDateTime(year=year, month=month, day=day, time="00:00") # time doesn't matter for date parameter
    
    dateTimeData = data["DateTime Payload Form Encoded"]
    dateTimeData[data["Start Date Key"]] = date # start date and end date are the same because bookings are always taken 2 days in advance, so you don't get opportunities to do other days.
    dateTimeData[data["End Date Key"]] = date
    dateTimeData[data["Start Time Key"]] = createDateTime(year=year, month=month, day=day, time=startTime) # day doesn't matter for the time parameter
    dateTimeData[data["End Time Key"]] = createDateTime(year=year, month=month, day=day, time=endTime)

    # Get the booking page
    bookingPage = requests.post(url=data["Booking URL Updated"], data=dateTimeData)
    courts = bookingPage.json()["classes"]

    # Get event IDs and convert to urls
    eventIds = [court["EventId"] for court in courts]
    eventURLs = [f"https://cityofhamilton.perfectmind.com/Clients/BookMe4EventParticipants?eventId={eventId}&occurrenceDate={year}{month}{day}" for eventId in eventIds]
    
    return eventURLs

# Might need to add the rest of things
def reformatSeleniumCookies(seleniumCookies: list):
    cookies = {}
    for cookie in seleniumCookies:
        name = cookie["name"]
        value = cookie["value"]
        cookies[name] = value
    return cookies

def checkCookiesUpdated(driver, cookieJar):
    driverCookies = reformatSeleniumCookies(driver.get_cookies())
    for cookie in cookieJar:
        if cookie.key not in driverCookies or driverCookies[cookie.key] != cookie.value:
            return False
    return True

def checkSpotValue(resp):
    # Note: The () in the regex is the group(1) being extracted below; these are the spots.
    soup = BeautifulSoup(resp, "html.parser")
    spotsRegex = re.compile(r"var\s+spotsLeft\s*=\s*([01]);", re.DOTALL)
    spotsScript = soup.find("script", string=spotsRegex)
    if spotsScript:
        spots = re.search(spotsRegex, spotsScript.string).group(1)
        print(spots)
    else:
        print("uh oh no script found")

async def get(sess: aiohttp.ClientSession, url: str):
    try:
        async with sess.get(url=url, timeout=5) as resp:
            if resp.status == 200:
                checkSpotValue(await resp.text())
                return resp
            else:
                print(resp.status, "failed: ", resp.reason)
                return url

    except Exception as e:
        print(e)
    
async def spamURLs(urls):
    async with aiohttp.ClientSession(headers=headers) as sess:
        
        # Log in
        login = await sess.post(url=data["Login URL"], data=loginPayload)
   
        # wanna repeat this a few times at 12:30
        if login:
            for i in range(1):
                results = await asyncio.gather(*[get(sess=sess, url=url) for url in urls])

        # just store the cookies and headers. 
        return {"cookies": sess.cookie_jar}

# Set selenium driver type and cookies as dic
def checkCookiesUpdated(driver, cookieJar):
    driverCookies = reformatSeleniumCookies(driver.get_cookies())
    for cookie in cookieJar:
        if cookie.key not in driverCookies or driverCookies[cookie.key] != cookie.value:
            return False
        
    
    return True

# Spam the pages
def main():
    eventURLs = getEventURLs()
    params = asyncio.run(spamURLs(eventURLs))
    
    cookieJar = params["cookies"]
    
  
    # set up selenium driver
    for url in eventURLs:
        driver = webdriver.Firefox()
        wait = WebDriverWait(driver, 100)
       
        
        '''
        Might need to put all args in the cookie, not just name and val.
        Could try to create a profile to preload into the driver. Still keep trying the profile.
        '''
        driver.get(url=data["Booking Page URL"])

        for cookie in cookieJar:
            driver.add_cookie({'name': cookie.key, 'value': cookie.value})
          
      
        wait.until(lambda driver: checkCookiesUpdated(driver, cookieJar))
      
    
        # get reservation page
        driver.get(url=url)



    # then book it.

    # Then make it user friendly.

if __name__ == "__main__":
    main()