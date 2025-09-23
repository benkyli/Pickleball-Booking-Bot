Only the eventID is necessary for getting to the booking screen.
Sample URL: https://cityofhamilton.perfectmind.com/Clients/BookMe4EventParticipants?eventId=a2eeaf37-c6ec-a772-ae6e-c4b3c4eddfa2
All we need is the eventId, which is the classId in the information page for the booking. Plug and chug.


User: bogejib211@colimarl.com
P: TestingStuff69!

  "Krilin Email": "kipisa5313@baxidy.com",
    "pw": "StuffMeDaddyXDD69!",

[Log in using requests in python](https://stackoverflow.com/questions/11892729/how-to-log-in-to-a-website-using-pythons-requests-module)
[Another example, specifically regarding __RequestVerificationToken](https://stackoverflow.com/questions/51430765/login-to-website-using-python-and-requestverificationtoken)

Will need an option to specify to get consecutive court in each hour interval. Otherwise it just tries to get 1 at all.  

# Loading booking page with parameters
1) Create the parameters json
2) put it into the request... the page itself is a get request, but the added filters are shown as a post. 

# Getting court urls
I'm thinking of having the program do a get request for the booking page. Then (or maybe you can just start with this) do a post request for your desired date and times. 

From there, get the table holding the courts of that day (table id="classes" ... let's see if that works xdd). Then, scrape the tr row attributes. However, skip the first one in the table because that's just the date. 

Okay, now that we have the attributes to each link, we actually want to click/enter each one to get their actual urls. These are the parts of the page where you will have to click to book.

<b>Will need to see how the holding system works.</b>
Do these actually hold when a person has clicked them? I wonder. Do other lose access to getting to this point? If I get to this point, will it go through or can a bot still overtake you, despite saying that the court.

Can test that by hyperlinking the book button when it says full. Will need 2 accounts to test that.
also need to check to see if a single account have hold multiple courts at once. 

# If the holding system works. Essentially just have multiple clients trying to click the book button on multiple courts. Will need to check if a user can hold more than 1 court, and if the court is actually held by the user. 

# Initial solution
- When you request an open landing page, the system holds it for you and locks out other users for "5 minutes" (feels like 3). However, there is some kind of problem occurring after doing this with the bot. It instead holds the spot, but doesn't assign it to the user. So when trying to manually checkout, there is no option even though the current user is definitely the one holding the spot. May need to change the header? Not sure how to do this part. May need to fully automate the entire checkout process from the request session itself. Would likely be better, but I wanted to try brute forcing quickly. 



[In depth SO post about python concurrent requests](https://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python)

Process now
1) Spam the fuck out of the links right before 12:30 using concurrent requests. Maybe only focus on 5 per batch instead of taking all 12. Or just try for all 12 because other people are doing the same thing. Maybe it's really competitive.
2) After about 30 seconds of this, check each url to see if you got them reserved. If you did, Access that link and mark off the time slot you got so you don't get multiple in the same slot. 
3) Given your reserved slots, finish the booking process, whether that be through more requests or manual clicking.


Current process report

But first off, I need to check if the next button is a reliable indicator of if we are holding a slot. 

Need to create a system that creates timeblocks from time settings. Then another system that checks to see which blocks have been filled by the holding system.

So we need to check the content on the request initially to see if we got the booking, due to the connector closing after finishing the requests. I suppose it should still keep going, so it makes sense to check during the async spam
Okay, so we should return the content, to check, 
then cross off the list of that time block. and store this linky. 

On user side, we should essesntially just show the slots that were successfully reserved. then they have to click or give permission to take the bookings. Takes care to not miss booking blocks. 
Should also have a timer for this to show how long the hold will last. 


For checking dynamic stuff:
https://www.reddit.com/r/learnpython/comments/1hoir54/how_do_you_go_about_web_scraping_dynamic_pages/

Resources file, constants file in book for me; check to see if spots are available.

Later feature
- Way to cancel booking (Could just be a redirect to the schedule page: https://cityofhamilton.perfectmind.com/MyProfile/Contact)


Form Features
1) - [x] FormId: in booking page form. (same across all forms)
2) - [x] ContactId: in booking page form. (depends on user)
3) - [x] EventId: in booking page form. Also just the eventId from before.
4) - [x] EventObjectId: Same across both forms. In page, but in a different attribute ("ObjectId")
5) - [x] Event location Id: in booking page form.
6) - [x] "qid_ba52b933-cd1f-4010-bc5d-9e1d00ca3466_2334376b-96f7-4fce-af55-d7f8558287df_009a3135-5f4d-7b24-f98a-99a63fff3d21": "Agreed"; the start of the string is the same across forms. The ending is just the event id.
7) - [ ] Request Verification token. May not be necessary. Not located in the booking page. Probably generated on page creation. hm. Will need to test.
8) - rest are empty params.
Form Response: Gives an Id that is needed for cart check out

Cart Item:
EventId: same as above
ObjectId: Same as above
MemberId: same as above
Full Name: Will need to parse from user (Might be in html/script already)
Cart Id: New thing. Might just be the id for the cart. Check html for this again
Cart Object and item id's: same as object and event prior.
Price type Id: Same across forms (free prob)
Cart Name: Same across forms, but seems to be tied to year


Should probably add error writes in case something happens. So I can see what they were, when they were, etc.

GUI
- Get log in info. 
    - Email
    - Password
- Get date desired info
    - Could have calendar function. Could just do single inputs for each: day, month, year
- Get time info.
    - Start
    - End