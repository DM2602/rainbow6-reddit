import praw
from time import time, sleep
from sys import exc_clear
from urllib import quote
 
def main():
    username = "accountName"
    password = "pw"
    subreddit_name = "sub"

    #Bot Settings
    sleep_time = 120 # time (in seconds) the bot sleeps before performing a new check
    time_until_message = 180 # time (in seconds) a person has to add flair before a initial message is sent
    time_until_remove = 600 # time (in seconds) after a message is sent that a person has to add flair before the post is removed and they have to resubmit it

    post_grab_limit = 20 # how many new posts to check at a time.
    post_memory_limit = 50 # how many posts the bot should remember before rewriting over it

    #Initial Message that tells then that they need to flair their post
    add_flair_subject_line = "You have not tagged your post."
    add_flair_message = "This post does not have any flair and has been removed.\n\nPlease add flair to your post. If you do not add flair within **" + formatTimeString( time_until_remove ) + "**, you will have to resubmit your post. Don't know how to flair your post? Click [here](https://www.reddit.com/r/DBZDokkanBattle/wiki/linkflair_guideline) to view our guidelines on how to flair your post. if you are using the mobile version of the site click the hamburger menu in the top right of the screen and switch to the desktop site and then follow the instructions as you would on desktop."

    #Second message telling them to resubmit their post since they have not flaired in time
    remove_post_subject_line = "You have not flaired your post within the allotted amount of time."
    remove_post_message = "This post still does not have any flair and will remain removed, feel free to resubmit your post and remember to flair it once it is posted.*"

    no_flair = []
    already_done = []
    post_age = time_until_message + time_until_remove
    user_agent = ( "Auto flair moderator for reddit created by /u/Coenl") # tells reddit the bot's purpose.
    session = praw.Reddit( user_agent = user_agent )
    session.login( username = username, password = password )
    subreddit=session.get_subreddit( subreddit_name )

    #Loop
    while True:
        # memory clean up code
        # keeps arrays at reasonable sizes
        if len( already_done ) >= post_memory_limit:
            i = 0
            posts_to_forget = post_memory_limit - post_grab_limit
            while i < posts_to_forget:
                already_done.pop( 0 )
                i += 1
        if len( no_flair ) >= post_memory_limit:
            i = 0
            while i < posts_to_forget:
                no_flair.pop( 0 )
                i += 1

        # try-catch runtime issues. Prevents bot from crashing when a problem is encountered. 
        # Most frequent trigger is a connection problemsuch as when reddit is down
        try:
            # get newest 20 submissions
            for stored_post in no_flair:
                if stored_post not in already_done:
                    unflaired_post = session.get_submission( submission_id = stored_post )
                    if ( unflaired_post.link_flair_text is not None):
                        unflaired_post.approve()
						# removes the warning post after its been reapproved
                        for comment in unflaired_post.comments:
                            if comment.author.name == "accountName":
                                comment.remove()
                        already_done.append( unflaired_post.id )
            for submission in subreddit.get_new( limit = post_grab_limit ):
                # if post is older than specified age
                if( ( time() - submission.created_utc ) > time_until_message):
                    # if post has not already been processed
                    if submission.id not in already_done:
                        # if post has not already been flagged for not having flair
                        if submission.id not in no_flair:
                            # if post does not have flair
                            if ( submission.link_flair_text is None ):
                                author = submission.author
								#login and send user message
                                session.login( username = username, password = password )
                                submission.add_comment(add_flair_message)
								#session.send_message( author, add_flair_subject_line, final_add_flair_message )
                                submission.remove()
                                no_flair.append( submission.id )
                            #if the post has flair, it is added to already_done
                            else:
                                already_done.append(submission.id)
        #handles runtime errors.
        except Exception:
			#clears the exception
            exc_clear()
        sleep( sleep_time )

# turn a time in seconds into a human readable string
def formatTimeString(time_in):
     minutes, seconds = divmod( time_in, 60 )
     hours, minutes = divmod( minutes, 60 )
     time_string = ""
     if hours > 0:
          time_string += "{0} hour".format(hours)
          if hours > 1:
               time_string += "s"
          time_string += " "
     if minutes > 0:
          time_string += "{0} minute".format(minutes)
          if minutes > 1:
               time_string += "s"
          time_string += " "
     if seconds > 0:
          time_string += "{0} second".format(seconds)
          if seconds > 1:
               time_string += "s"
          time_string += " "
     return time_string[:-1]



#call main fuctions
main()