# Proposal/Plan

## Proposals
Project Idea #1: I would like to make a bot that scrapes various League of Legends esports websites and conglomerates all data about recent matches
and also grabs videos of game highlights from YouTube, essentially creating a “reader’s digest” of a particular day, week or tournament. 
I would use the Scrapy library for the web crawling functionality. 
I am unsure how I want to structure the obtained content, but it could be in a simple web page made with Bottle.

To Do
Proof of concept on the integrations with League of Legends APIs or scraping of websites
Figure out how you want to represent the data
Figure out how to get that representation from the data that you obtain thanks to #1
Build out a UI (Bottle sounds good to me) 

## Goals and Roadmap
End of week 4: Organize and structure exactly what data I want to be gathering and showing the user, and what websites to gather data from

End of week 5: Proof of concept gather one specific data element from the North American (LCS) matches happening that weekend

End of week 7: Have system in place to gather the rest of the data from all leagues/tournaments and have very basic webpage to display all info

Rest of the time: Make website look good and have selection parameters; visualize data in interesting ways?

# Result/Reflection

## Project Description
While initially I was planning on making a web-app concerned with recent matches, I ended up pivoting towards a much deeper dive
on the scraping and data side of things while foregoing the front-end portion. I thought this worked out for me well in terms of 
allowing me to work on some new skills since I have used a web framework like Bottle in the past for a different class.
I was able to use both the Scrapy library for web crawling and the pandas library for some data analysis, both of which I had
never used prior to this class.
The final product is a scraper that crawls the lol.gamepedia (League of Legends esports wiki) website and scrapes all stats
from all regular season games from all four major regions (North America, Europe, China, Korea) from 2014 (Season 4) to the present.
While the description is somewhat straightforward, the process was far from it for me, since I couldn't figure out for the longest
time what I wanted to extract and how I wanted to format/present said data. I eventually decided on going game-by-game from each
match week of each year, scraping as much data as I could to put in a pandas dataframe. Doing only regular season games gave an
extremely generous sample size, but also granted some consistency that would not have been kept if I had tried to also scrape
playoffs/international tournament games. The consistency, however, was not without flaws, as both rules have changed over the 
years (leading to stats pages looking different/having different information), and incomplete/missing information is still an issue 
for older matches. A lot of the challenge was working around these inconsistencies and error-proofing the extraction to still get
as much as possible out of a page even when data was missing.

## How To Run The Project
Go to the level of the directory where most things are visible (spiders folder, example_analysis, results folder, etc.). Type:
```
scrapy crawl domestic
```
into the terminal (domestic is the name of the crawler, named for the domestic tournaments it scrapes). This will cause the 
scraper to do its thing. The resultant JSONs will be stored in the results folder, but a full copy of the scraped files
are already in there if you don't want to run the program yourself. If you do choose to run it, you do not have to delete anything
as the program will automatically overwrite those json files with the new ones. 
Also included is example_analysis.py, where I go through a brief demo of some data-analysis possibilities with the obtained JSON files.
To run that, just type:
```
py example_analysis.py
```