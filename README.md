DailyProgBot
============

The r/DailyProgrammer's automated submission bot source-code

About
-----

This is simply a single-file Python script that, when launched on certain days of the week, will retrieve a certain difficulty of programming challenge from a Google Document Spreadsheet, format it and post it for Reddit, and finally update the target Subreddit's links.

This code is specificly designed for r/DailyProgrammer's automated submission system for queued programming challenges.

The only two dependancies are the GSpread (Google Spreadsheet interface) and the PRAW Python Reddit API. Special thanks to those devs for making much of this work so much easier!

To deploy such a system, simply run the "DailyProgBot.py" Python file next to another file (named "AccountDetails.py") containing your account names and passwords. Such a file would look like the following:

    #!/usr/bin/python
    
    # Reddit usernames & pass
    EASY_USERNAME = 'DailyProgBot_Easy'
    EASY_PASSWORD = 'Password'
    INTER_USERNAME = 'DailyProgBot_Inter'
    INTER_PASSWORD = 'Password'
    HARD_USERNAME = 'DailyProgBot_Hard'
    HARD_PASSWORD = 'Password'
    
    # Google account username & pass
    GSPREAD_USERNAME = 'Username@gmail.com'
    GSPREAD_PASSWORD = 'Password'

Please note that this code is writen as a simple and quick script, and does not follow "good programming practices" for comercial systems, such as using oAuth2.0 (rather than using a simple username / password as it currently does). You've been warned!
