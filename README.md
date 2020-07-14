# Thor
This discord bot was something that I worked on in my spare time from 2016-2017. It got up to about 60k-70k members then started having serious problems as the hardware I was running it on was rubbish (512mb of ram).

The source code never went public until the project was long dead so there are somethings I would tidy up if I were still maintaining the project.  Wether that be varible names, functions that never get called or performance issues. 

There was a PostgreSQL database that went hand in hand with this, it held a log of disiplinery actions for the most part and not too much else, which for the ammount that this bot got used, SQL was very much overkill.

I used some of Danny's (Rapptz) code in places (largely eval code), and SnowyLuma's Code (database connection handling). Aside from that (and the libraries I used) no other code was put into mine.

Biggest thanks goes out to the discord.py community who helped inspire, motivate and teach me how to accomplish many of the issues I faced when writing this.
