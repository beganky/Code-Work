"""
Brendan Egan 
Seth Berry 
Unstructured Data Analytics
Final Project Visualizations
"""

import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns

##Below are from my scraper I created using the other attached python file (The output from that code is the following 2 .csv files)
#My player data set 
player_data = pd.read_csv("C:/users/eganb/Downloads/soccer_data/player_scraped_data.csv")
player_data.columns

#My team data set 
team_data = pd.read_csv("C:/users/eganb/Downloads/soccer_data/understat_teams_data.csv")
team_data.columns

#Now, I just need to create a few visualizations for my presentation.

#First, let's look at the highest point finishers across the last 10 seasons in each league.
top_10_teams = team_data.sort_values("points", ascending=False).head(10)

plt.figure(figsize=(10, 6))
ax = sns.scatterplot(data=top_10_teams, x="league", y="points", hue="season", s=150)

#Label each dot w/associated team name
for _, row in top_10_teams.iterrows():
    ax.text(
        row["league"],
        row["points"] + 0.5,    # slightly above the dot
        row["team"],
        ha="center",
        va="bottom",
        fontsize=8)

plt.title("Top 10 Point total Finishers by League (2015-2025)")
plt.xlabel("League of Team")
plt.ylabel("Points at Season End")
plt.legend(title="Season", loc="upper right")#What season are you looking @ rn 
#Put that in the top right so it is out of the way of data points
plt.show()

#Now, I want to print the best players by xG 

top_10_xG = player_data.sort_values("xg", ascending=False).head(10)

plt.figure(figsize=(10, 6))
az = sns.scatterplot(data=top_10_xG, x="league", y="xg", hue="season", s=150)#Create the scatterplot and set the size of the dot

#Label each dot w/associated player name
for _, row in top_10_xG.iterrows():
    az.text(
        row["league"],
        row["xg"] + 0.05,   
        row["player"],
        ha="center",
        va="bottom",
        fontsize=8)

plt.title("Top 10 xG Finishers by League (2015-2025)")
plt.xlabel("League of Player")
plt.ylabel("xG at Season End")
plt.legend(title="Season", loc="upper right")#What season are you looking @ rn

plt.show()


#Top 10 best chance creators 

top_10_xA = player_data.sort_values("xa", ascending=False).head(10)

plt.figure(figsize= (10, 6))
ay = sns.scatterplot(data= top_10_xA, x="league", y="xa", hue="season", s=150)

#Label each dot w/associated player name
for _, row in top_10_xA.iterrows():
    ay.text(
        row["league"],
        row["xa"] + 0.05,   
        row["player"],
        ha="center",
        va="bottom",
        fontsize=8)

plt.title("Top 10 xA Finishers by League (2015-2025)")
plt.xlabel("League of Player")
plt.ylabel("xA at Season End")
plt.legend(title="Season", loc="upper right")#What season are you looking @ rn

plt.show()