import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import asyncio
import aiohttp
import re
import time

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

# Prepare date and time values
year = "2025"
month = "09"
day = "16"
startTime = "12:30"
endTime = "15:30"

def createDateTime(year: str, month: str, day: str, time="00:00"):
    return f"{year}-{month}-{day}T{time}:00.000Z"

# Definitely delete later
def printDic(dic):
    for key in dic:
        print(key, ":", dic[key])


def getEventURLs():
    # Set date-time parameters in dictionary
    date = createDateTime(year=year, month=month, day=day, time="00:00") # time doesn't matter for date parameter
    
    dateTimeData = data["DateTime Payload"]
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

def checkSpotValue(html):
    # Note: The () in the regex is the group(1) being extracted below; these are the spots.
    soup = BeautifulSoup(html, "html.parser")
    spotsRegex = re.compile(r"var\s+spotsLeft\s*=\s*([01]);")
    spotsScript = soup.find("script", string=spotsRegex)
    if spotsScript:
        spots = re.search(spotsRegex, spotsScript.string).group(1)
        return spots
    else:
        print("uh oh no script found")

'''
Combine these functions more easily. Make it more robust, although, probably not necessary.
Then test the start time one. Yeagh, 
'''

def checkStartTime(html):
    soup = BeautifulSoup(html, "html.parser")
    timeRegex = re.compile(r'"StartTime":"([^"]+)"') 
    timeScript = soup.find("script", string=timeRegex)
    if timeScript:
        startTimeString = re.search(timeRegex, timeScript.string).group(1)
        # parse the string to get the start time 24 hour value.
        hourModifier = 0
        if startTimeString[-2:] == "PM" and startTimeString[:2] != "12": # there are no 12AM bookings, so no need for that edge case
            hourModifier = 12
        
        return int(startTimeString[:2]) + hourModifier
    
    else:
        print("no script found")


async def get(sess: aiohttp.ClientSession, url: str):
    try:
        async with sess.get(url=url, timeout=5) as resp:
            if resp.status == 200:
                respHTML = await resp.text()
                spotGotten = checkSpotValue(respHTML)
                if spotGotten == "1": 
                    startTime = checkStartTime(respHTML)
                    return [startTime, resp.url]
                # This will return None if the page was gotten successfully but the booking wasn't there
            else:
                print(resp.status, "failed: ", resp.reason)

    except Exception as e:
        print(e)
    
async def spamURLs(urls, timeSlotsAmount):
    async with aiohttp.ClientSession(headers=headers) as sess:
        login = await sess.post(url=data["Login URL"], data=loginPayload)  # should probably have error handling here
   
        # wanna repeat this a few times at 12:30
        successfulHolds = set()
        successfulTimeSlots = set()
        if login:
            for i in range(1):
                # Get all urls that we successfully held and save them
                results = await asyncio.gather(*[get(sess=sess, url=url) for url in urls])
                for success in results:
                    if success != None:
                        bookingTime = success[0]
                        url = success[1]
                        if bookingTime not in successfulTimeSlots and url not in successfulHolds:
                            successfulTimeSlots.add(bookingTime)
                            successfulHolds.add(url)
                            print(f"time got: {bookingTime}")
                            # may also want to remove url from urls so we stop looping them. Also might want to add time check earlier so we skip some pages.

                if len(successfulTimeSlots) == timeSlotsAmount:
                    break
                        

        # just store cookies and urls
        return {"cookies": sess.cookie_jar,
                "urls" : successfulHolds,
                "timeSlots": successfulTimeSlots}

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
    startTimeHour = int(startTime[0:2]) # just the first 2 characters have the hour time.
    endTimeHour = int(endTime[0:2])
    timeSlotsAmount = endTimeHour - startTimeHour

    results = asyncio.run(spamURLs(urls=eventURLs, timeSlotsAmount=timeSlotsAmount))
    
    cookieJar = results["cookies"]
    successfulHolds = results["urls"]

    # Have a tracker for time slots. probably just max time - min time (hour), then use those as indices. Then when checking times, compare the lower time slot hour and minus to the lowest start time.
    if not successfulHolds:
        print("No open bookings")
        return
    
    

    for success in successfulHolds:
        # We're just going to assume that the checkout will occur at this point. Surely nothing will fail...

        # Set up driver
        url = str(success) # string conversion is done here to save time during the request spamming
        driver = webdriver.Firefox()
        wait = WebDriverWait(driver, 25)
       
        # Update cookies
        driver.get(url=data["Booking Page URL"])
        driver.delete_all_cookies()

        for cookie in cookieJar:
            driver.add_cookie({'name': cookie.key, 'value': cookie.value})

        wait.until(lambda driver: checkCookiesUpdated(driver, cookieJar))
    
        # get event page
        driver.get(url=url)

        # wait for overlay to dissappear on reservation page
        wait.until(EC.invisibility_of_element_located((By.ID, "ajaxRequestStatus_attendance")))

        # click next button on the reservation page, liability form page, and pricing page
        for i in range(3):
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[./span[text()='Next']]")))
            button.click()
            wait.until(EC.staleness_of(button))

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.CLASS_NAME, "online-store")))

        # simulate human movement and submit
        time.sleep(1)
        actions = ActionChains(driver)
        checkoutButton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.process-now")))
        actions.move_to_element(checkoutButton).perform()
        time.sleep(1.2)
        checkoutButton.click()
            
    # Then make it user friendly.

if __name__ == "__main__":
    main()