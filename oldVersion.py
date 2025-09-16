'''
This version of the code automates everything up until the checkout process. At that point, an invisible recaptcha occurs. I didn't want to use a recaptcha service, so I opted to use Selenium to finish the checkout process. This was kept just to demonstrate the process and evolution of the script
'''

import requests
import json
from bs4 import BeautifulSoup
import asyncio
import aiohttp
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
    day = "08"
    startTime = "12:30"
    endTime = "13:30"

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

def checkSpotValue(resp):
    # Note: The () in the regex is the group(1) being extracted below; these are the spots.
    soup = BeautifulSoup(resp, "html.parser")
    spotsRegex = re.compile(r"var\s+spotsLeft\s*=\s*([01]);", re.DOTALL)
    spotsScript = soup.find("script", string=spotsRegex)
    if spotsScript:
        spots = re.search(spotsRegex, spotsScript.string).group(1)
        return spots
    else:
        print("uh oh no script found")

def createLiabilityForm(bookingPage, formPage):
    formJSON = data["Liability Form Request JSON"]

    # Get form values from booking page
    bookingPageSoup = BeautifulSoup(bookingPage.text, "html.parser")
    form = bookingPageSoup.find("form", id="eventParticipantsSelection") # put this id name in data json
    formKeys = data["Liability Form Input Names"]
    for key in formKeys:
        attributeName = formKeys[key]
        attributeValue = form.find("input", attrs={"name": attributeName})["value"]
        formJSON[key] = attributeValue

    # Generate qid values
    qidSuffix = formJSON["ContactId"] + "_" + formJSON["EventId"] # put this initial string in data json
    qidKey = "qid_ba52b933-cd1f-4010-bc5d-9e1d00ca3466_" + qidSuffix
    qidKey2 = "qid_bb812e6a-ea9a-4786-9fc6-2f6485359389_" + qidSuffix
    formJSON[qidKey] = "Agreed"
    formJSON[qidKey2] = ""

    # Get the RequestVerificationToken
    formPageSoup = BeautifulSoup(formPage.text, "html.parser")
    tokenForm = formPageSoup.find("form") # there is only 1 form available on load
    tokenInput = tokenForm.find("input") # there is only 1 input in the form
    formJSON["__RequestVerificationToken"] = tokenInput["value"]
   
    return formJSON

async def get(sess: aiohttp.ClientSession, url: str):
    try:
        async with sess.get(url=url, timeout=5) as resp:
            if resp.status == 200:
                spotGotten = checkSpotValue(await resp.text())
                if spotGotten == "1": 
                    return resp.url
                # This will return None if the page was gotten successfully but the booking wasn't there
            else:
                print(resp.status, "failed: ", resp.reason)
                return url

    except Exception as e:
        print(e)
    
async def spamURLs(urls):
    async with aiohttp.ClientSession(headers=headers) as sess:
        login = await sess.post(url=data["Login URL"], data=loginPayload)  # should probably have error handling here
   
        # wanna repeat this a few times at 12:30
        successfulHolds = set()
        if login:
            for i in range(1):
                # Get all urls that we successfully held and save them
                results = await asyncio.gather(*[get(sess=sess, url=url) for url in urls])
                for url in results:
                    if url != None and url not in successfulHolds:
                        successfulHolds.add(url)

        # just store cookies and urls
        return {"cookies": sess.cookie_jar,
                "urls" : successfulHolds}

# Set selenium driver type and cookies as dic
def checkCookiesUpdated(driver, cookieJar):
    driverCookies = reformatSeleniumCookies(driver.get_cookies())
    for cookie in cookieJar:
        if cookie.key not in driverCookies or driverCookies[cookie.key] != cookie.value:
            return False
        
    return True

# Spam the pages
def main():
    # eventURLs = getEventURLs()
    eventURLs = ['https://cityofhamilton.perfectmind.com/Clients/BookMe4EventParticipants?eventId=bd4f3274-cf1a-fad6-8468-88ba7ed0fca4&occurrenceDate=20250911']
    results = asyncio.run(spamURLs(eventURLs))
    
    cookieJar = results["cookies"]
    successfulHolds = results["urls"]
    print(successfulHolds)

    with requests.Session() as sess:
        sess.headers = headers
        for cookie in cookieJar:
            sess.cookies.set(cookie.key, cookie.value)
      
        for success in successfulHolds:
            # Get liability form info from booking page. Send post request for the form.
            bookingPage = sess.get(success)
            headers["Referer"] = str(success)
            formPage = sess.get(data["Form Page URL"], headers=headers)
            
            # prepare and post form
            formJSON = createLiabilityForm(bookingPage, formPage)
            formPOST = sess.post(url=data["Form POST URL"], data=formJSON)
            print(formPOST.status_code)
            print(formPOST.reason)
            print(formPOST.json())

        #Check out page: Seems to be a lot of forms here. Might need to do a recaptcha check, fill in the obfuscated request data, get the token response, and input that into the checkout post request.

    # Then make it user friendly.

if __name__ == "__main__":
    main()