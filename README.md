# Sports-Analytics-Project

Brendan Egan 
Final Project Spring 2026
Unstructured Data Analytics

The goal of this project was to scrape through 10 seasons of data for both team and players in Europe's top leagues. 
Using understat.com I was able to scrape through the 2015-2025 seasons and determine who were the best goalscorers, chance creators and who played the most minutes. 
I also wanted to collect team data in order to see who were the best performing teams throughout those 10 years. 

(Side note, 2015/2016 was the season that advanced statistics such as xG & xA were recorded [xG: Expected goal rate & xA: Expected assist rate])
That means that if you attempt to collect 2014/2015 data my scraper will ignore that year and chug along to the next season.
If you collect any data before 2015 all the columns with xG, xA, xDF (expected goal differential) will be empty and you would not be able to do any analysis at all.

I was able to collect that data through quite a fun... process where I had to learn to deal with understatclient the python package.

My only real struggle I ran into was an issue of collecting data from La Liga (Spain's first division) where my scraper as well as the understat page claimed it did not exist. 
  I thought that was really hard to believe as I had the page pulled up in my browser, but I digress. 

In the future (besides figuring out the La Liga issue...), I want to build another scraper that will pull individual player contract data so that I can attempt to create a model that determines when players should be paid. 
I would love to have a model that can predict overpays from clubs solely by looking at recent players who have performed similar and see how they did in comparison to their contract valuation. 
That model would be able to assist clubs in finding when they should lock down a player to a long term contract and save money in the long run or should they take a gamble for a player who has been playing below expectations. 
Finally, I think if I could weigh each league based on how effective clubs from leagues are at continental I would be able to give players stats a better comparison to one another. As styles will vary from league to league and players transferring in will have to adapt to that new style. In the age of data and film, coaches will adapt play styles from game to game, so a general comparison of league to league would help me compare stats of a 33 year old Premier League (England's first division) veteran to a 19 year old playing in Serie B (Italy's second division) and see who would be worth offering a new deal to.


