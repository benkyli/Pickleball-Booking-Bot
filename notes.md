Only the eventID is necessary for getting to the booking screen.
Sample URL: https://cityofhamilton.perfectmind.com/Clients/BookMe4EventParticipants?eventId=a2eeaf37-c6ec-a772-ae6e-c4b3c4eddfa2
A bit at the start before the ? is removed, and everything except the event ID is removed after the ?

User: bogejib211@colimarl.com
P: TestingStuff69!

[Log in using requests in python](https://stackoverflow.com/questions/11892729/how-to-log-in-to-a-website-using-pythons-requests-module)

Will need an option to specify to get consecutive court in each hour interval. Otherwise it just tries to get 1 at all.  

# Getting court urls
I'm thinking of having the program do a get request for the booking page. Then (or maybe you can just start with this) do a post request for your desired date and times. 

From there, get the table holding the courts of that day (table id="classes" ... let's see if that works xdd). Then, scrape the tr row attributes. However, skip the first one in the table because that's just the date. 

Okay, now that we have the attributes to each link, we actually want to click/enter each one to get their actual urls. These are the parts of the page where you will have to click to book.

<b>Will need to see how the holding system works.</b>
Do these actually hold when a person has clicked them? I wonder. Do other lose access to getting to this point? If I get to this point, will it go through or can a bot still overtake you, despite saying that the court.

Can test that by hyperlinking the book button when it says full. Will need 2 accounts to test that.
also need to check to see if a single account have hold multiple courts at once. 

# If the holding system works. Essentially just have multiple clients trying to click the book button on multiple courts. Will need to check if a user can hold more than 1 court, and if the court is actually held by the user. 