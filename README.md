DailyProgBot
============

The r/DailyProgrammer's automated submission bot source-code

About
-----

This is simply a single-file Python script that, when launched on certain days of the week, will retrieve a certain difficulty of programming challenge from a Google Document Spreadsheet, format it and post it for Reddit, and finally update the target Subreddit's links.

This code is specificly designed for r/DailyProgrammer's automated submission system for queued programming challenges.

The only two dependancies are the GSpread (Google Spreadsheet interface) and the PRAW Python Reddit API. Special thanks to those devs for making much of this work so much easier!
