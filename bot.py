import requests
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
import datetime
import data_manager

# NOTE: When I started working on the ui, I changed the naming style to snake case to fit Python conventions better. However, I didn't want to change all the variable names in this file, so I just did the function names.

# this loads the data that is shared with the ui app.
data_manager.load_data()

# Allows us to swap to selenium if necessary and may help against bot detection
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0'
}

def create_datetime(year: str, month: str, day: str, time="00:00"):
    return f"{year}-{month}-{day}T{time}:00.000Z"

def test_login(email: str, password: str):
    payload = {
        data_manager.get_value("Email Field Name") : email,
        data_manager.get_value("Password Field Name") : password    
    }
    
    with requests.Session() as sess:
        try:
            login = sess.post(url=data_manager.get_value("Login URL"), data=payload)
            if login.status_code == 200:
                if "PMAuth" in sess.cookies:
                    return True
                return False # login values were wrong. Could refactor this to have 1 false return
            else:
                return False # login did not reach server properly.
        except:
            print("failed to get login page")

def get_event_urls(year: str, month: str, day: str, startTime: int, endTime: int):
    # Set date-time parameters in dictionary
    date = create_datetime(year=year, month=month, day=day, time="00:00") # time doesn't matter for date parameter
    
    dateTimeData = data_manager.get_value("DateTime Payload")
    dateTimeData[data_manager.get_value("Start Date Key")] = date # start date and end date are the same because bookings are always taken 2 days in advance, so you don't get opportunities to do other days.
    dateTimeData[data_manager.get_value("End Date Key")] = date
    dateTimeData[data_manager.get_value("Start Time Key")] = create_datetime(year=year, month=month, day=day, time=startTime) # day doesn't matter for the time parameter
    dateTimeData[data_manager.get_value("End Time Key")] = create_datetime(year=year, month=month, day=day, time=endTime)

    # Get the booking page
    bookingPage = requests.post(url=data_manager.get_value("Booking URL Updated"), data=dateTimeData)
    courts = bookingPage.json()["classes"]

    # Get event IDs and convert to urls
    eventIds = [court["EventId"] for court in courts]
    eventURLs = [f"https://cityofhamilton.perfectmind.com/Clients/BookMe4EventParticipants?eventId={eventId}&occurrenceDate={year}{month}{day}" for eventId in eventIds]
    
    return eventURLs

# Might need to add the rest of things
def reformat_selenium_cookies(seleniumCookies: list):
    cookies = {}
    for cookie in seleniumCookies:
        name = cookie["name"]
        value = cookie["value"]
        cookies[name] = value
    return cookies

def check_cookies_updated(driver, cookieJar):
    driverCookies = reformat_selenium_cookies(driver.get_cookies())
    for cookie in cookieJar:
        if cookie.key not in driverCookies or driverCookies[cookie.key] != cookie.value:
            return False
    return True

def check_spot_value(html):
    # Note: The () in the regex is the group(1) being extracted below; these are the spots.
    soup = BeautifulSoup(html, "html.parser")
    spotsRegex = re.compile(r"var\s+spotsLeft\s*=\s*([01]);")
    spotsScript = soup.find("script", string=spotsRegex)
    if spotsScript:
        spots = re.search(spotsRegex, spotsScript.string).group(1)
        return spots
    else:
        print("uh oh no spot value found")

# I could combine these functions, but I'm not gonna use this for anything else so I'll leave it hard coded like this.

def check_start_time(html):
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
        print("no start time found")


async def get(sess: aiohttp.ClientSession, url: str):
    try:
        async with sess.get(url=url, timeout=5) as resp:
            if resp.status == 200:
                respHTML = await resp.text()
                spotGotten = check_spot_value(respHTML)
                if spotGotten == "1": 
                    startTime = check_start_time(respHTML)
                    return [startTime, resp.url]
                # This will return None if the page was gotten successfully but the booking wasn't there
            else:
                print(resp.status, "failed: ", resp.reason, f"URL: {url}")

    except Exception as e:
        print(e)
    
async def spam_urls(urls, timeSlotsAmount):
    loginPayload = {
        data_manager.get_value("Email Field Name") : data_manager.get_value("User Email"),
        data_manager.get_value("Password Field Name") : data_manager.get_value("User Password")    
    }
    
    async with aiohttp.ClientSession(headers=headers) as sess:
        login = await sess.post(url=data_manager.get_value("Login URL"), data=loginPayload)  # should probably have error handling here
   
        successfulHolds = set()
        successfulTimeSlots = set()
        if login: # I wonder if the login times out if you just keep the loop going for hours.
            print("spamming links started")
            for i in range(20):
                results = await asyncio.gather(*[get(sess=sess, url=url) for url in urls])
                # Get all urls that we successfully held and save them
                for success in results:
                    if success != None:
                        bookingTime = success[0]
                        url = success[1]
                        if bookingTime not in successfulTimeSlots and url not in successfulHolds:
                            successfulTimeSlots.add(bookingTime)
                            successfulHolds.add(url)
                            # may also want to remove url from urls so we stop looping them. Also might want to add time check earlier so we skip some pages.

                if len(successfulTimeSlots) == timeSlotsAmount:
                    break
                        
        # just store cookies and urls
        return {"cookies": sess.cookie_jar,
                "urls" : successfulHolds,
                "timeSlots": successfulTimeSlots}


# Spam the pages
def site_scrape(date, start_time, end_time, book_now=False):
    year = date.year
    month = f"{date.month:02d}" # make it leading zero
    day = f"{date.day:02d}"
    startTimeHour = int(start_time[0:2]) # just the first 2 characters have the hour time.
    endTimeHour = int(end_time[0:2])
    timeSlotsAmount = endTimeHour - startTimeHour

    eventURLs = get_event_urls(year=year, month=month, day=day, startTime=start_time, endTime=end_time)

    # twelve thirty time checks.
    twelve_thirty = datetime.time(12, 30)
    twelve_thirty_one = datetime.time(12, 31)

    results = []
    if book_now:
        results = asyncio.run(spam_urls(urls=eventURLs, timeSlotsAmount=timeSlotsAmount))
    else:
        while True: # seems a little sketchy, but whatever.
            if datetime.datetime.now().time() > twelve_thirty and datetime.datetime.now().time() < twelve_thirty_one:
                results = asyncio.run(spam_urls(urls=eventURLs, timeSlotsAmount=timeSlotsAmount))
                break
            time.sleep(1)
    
    cookieJar = []
    successfulHolds = []
    if results:
        cookieJar = results["cookies"]
        successfulHolds = results["urls"]

    # Have a tracker for time slots. probably just max time - min time (hour), then use those as indices. Then when checking times, compare the lower time slot hour and minus to the lowest start time.
    if not successfulHolds:
        print("No open bookings")
        return False

    for success in successfulHolds:
        # We're just going to assume that the checkout will occur at this point. Surely nothing will fail...

        # Set up driver
        url = str(success) 
        driver = webdriver.Firefox()
        wait = WebDriverWait(driver, 25)
       
        # Update cookies
        driver.get(url=data_manager.get_value("Booking Page URL"))
        driver.delete_all_cookies()

        for cookie in cookieJar:
            driver.add_cookie({'name': cookie.key, 'value': cookie.value})

        wait.until(lambda driver: check_cookies_updated(driver, cookieJar))
    
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

        # simulate human movement and submit to book court
        time.sleep(1)
        actions = ActionChains(driver)
        checkoutButton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.process-now")))
        actions.move_to_element(checkoutButton).perform()
        time.sleep(1.2)
        checkoutButton.click()
    
    return len(successfulHolds)