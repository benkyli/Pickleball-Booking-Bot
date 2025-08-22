Only the eventID is necessary for getting to the booking screen.
Sample URL: https://cityofhamilton.perfectmind.com/Clients/BookMe4EventParticipants?eventId=a2eeaf37-c6ec-a772-ae6e-c4b3c4eddfa2
All we need is the eventId, which is the classId in the information page for the booking. Plug and chug.


User: bogejib211@colimarl.com
P: TestingStuff69!

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


# make post for booking page
1) Get the template for the post from data
2) Replace the start and end date-times with your own desired parameters
3) plug this into a post request with the page link as data?
1.99) May need to swap request's __RequestVerificationToken with your current cookie's
2) 


Concurrent requests