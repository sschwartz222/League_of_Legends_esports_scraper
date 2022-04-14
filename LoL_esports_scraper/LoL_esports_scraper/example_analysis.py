import json
import pandas as pd
from pandas import DataFrame, Series
f_all = open('results/results_all_games.json',)
f_lcs = open('results/results_NA_2021_spring.json')
data_all = json.load(f_all)
data_lcs = json.load(f_lcs)
df_all = pd.DataFrame.from_dict(data_all)
df_lcs = pd.DataFrame.from_dict(data_lcs)
#doing some sample analysis with pandas to show what this scraped data is potentially useful for

#first, starting with the most recent 2021 Spring North American season, showing the dataframe
print(df_lcs)

#nice and neat :)

#lets take a look at the number of wins from red and blue side, respectively
#remember that a 0 in the winner column indicates a blue win, while a 1 indicates a red win
print(df_lcs.loc[df_lcs['winner'] == 0].count())
print(df_lcs.loc[df_lcs['winner'] == 1].count())

#45-45 split, pretty unusual

#how about for all regular season games for all four major leagues from 2014 to the present?
print(df_all.loc[df_all['winner'] == 0].count())
print(df_all.loc[df_all['winner'] == 1].count())

#this time, it's a 5376-4482 split in favor of blue
#blue has a ~54.5% win rate over nearly 10,000 games!

#ok what about finding the longest game of the season for the most recent North American split?
print(df_lcs[['datetime', 'blue_team', 'red_team', 'winner', 'duration']].sort_values('duration', ascending=False))

#100 Thieves and Golden Guardians with some bangers, apparently
#3383 seconds is around 56 minutes, 23 seconds, which seems super long!
#how does that stack up to historial figures though?
print(df_all['duration'].max())
print(df_all['duration'].mean())
print(df_all['duration'].median())
print(df_all['duration'].min())

#5680 seconds is over 94 minutes, and was such a dreadful game between the Korean teams SKT T1 and Jin Air Greenwings
#that they changed some core game mechanics to prevent something like that from ever happening again lol
#The 56 minute game is still long, however, compared to the average game time of 35:15 and median time of 34:12

#one last one for show; what has average game time looked like over the years?
print(df_all.groupby('season').agg({'season':'count', 'duration' : 'mean'}))

#ignoring season 3 data (byproduct of Korea having part of a split before the new year back in the day),
#the results are pretty convincing in showing the trend of shorter game times
#there are lots of reasons for this--in many ways this is intentional with the late-game game-ending mechanics
#added specifically to make sure long games like the 100 Theives/GG game are rare, and that 94 minute games like
#the SKT/JAG game never happen again

f_all.close()
f_lcs.close()