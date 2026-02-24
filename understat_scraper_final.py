"""
Understat Soccer Scraper — Final Version (2015-2023)

Uses the understatapi package instead of raw requests (I made two separate scrapers before I came to this realization)
which was awesome... anyways, the package handles Understat's bot protection and helped me pull my data from Understat's website.

Running this from start to finish takes around 20 minutes just a quick heads up...

Where is everything supposedly saved...
Output (saved to soccer_data/):
  player_scraped_data.csv  — one row per player per season
  understat_teams_data.csv    — one row per team per season
"""

#Bring in all the necessary packages
import time
import argparse
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from understatapi import UnderstatClient

#Logging all of the data and list comprehensions so I can actually track said data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("understat_scraper.log"),
        logging.StreamHandler()])
log = logging.getLogger(__name__)

#Here is the setup for both the leagues and seasons I want to pull data for 

Leagues = {
    "EPL":         "Premier League",
    "Bundesliga":  "Bundesliga",
    "Serie_A":     "Serie A",
    "Ligue_1":     "Ligue 1"}

    #I swear this should have been La Ligas
#    "La_Liga":     "La Liga" but it did not work despite that being the url 
#https://understat.com/league/La_liga I swear that takes you right to the page... do not get me started.
#I spent five days trying to pull data from the 2014 season in the Premier League and figured out that xG and xA data did not exist back then... please do not ask how awesome I felt figuring that out
#La Liga (Spain's first division) is also not included, because the scraper kept breaking or claiming the pages did not exist... even though I was staring at them in my browser

#When do I want to collect
Seasons = list(range(2015, 2024)) #These will be at the end of the url and represent the beginning year of the season

#Where am I hiding the data secrets. 
Output_spot = Path("soccer_data")
Output_spot.mkdir(exist_ok=True)

REQUEST_DELAY = 5   #Seconds between requests so I do not get blocked by Understat's bot 
#Huge pain in the butt btw especially after my nightmare trying to dance around CloudFlare 
#Understat blocked me for having this at 3, so I stuck with 5... bc it worked... 

#Player data
Player_cols = {
    "player_name": "player",
    "team_title":  "team",
    "time":        "minutes", 
    "npg":         "non_penalty_goals", #Scoring in the 'run of play'
    "npxG":        "npxg", #Non-penalty expected goals
    "xG":          "xg", #Expected goals
    "xA":          "xa", #Expected assits 
    "xGChain":     "xg_chain", 
    "xGBuildup":   "xg_buildup"} #Last two measure how involved a given player is in the build up to a shot

#Columns of numeric data, which will be converted to numeric types for calculations (per 90 stats)
Player_stat_cols = [
    "games", "minutes", "goals", "assists", "shots", "key_passes",
    "yellow_cards", "red_cards", "non_penalty_goals",
    "xg", "xa", "npxg", "xg_chain", "xg_buildup"]

#What do I want to find in the player data and what am I keeping (save to .csv later)
def build_players_df(raw: list, league: str, season: int) -> pd.DataFrame:
    here_we_go = pd.DataFrame(raw).rename(columns=Player_cols)

    keep = [
        "player", "team", "position", "games", "minutes", "goals", "assists",
        "shots", "key_passes", "yellow_cards", "red_cards", "non_penalty_goals",
        "xg", "xa", "npxg", "xg_chain", "xg_buildup",]
    ugly_data = here_we_go[[c for c in keep if c in here_we_go.columns]]

    for col in Player_stat_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

#Per 90 stats that are calculated w/raw data then converted to per 90 w/rounding so my data is not disgusting.
    mins = ugly_data["minutes"].replace(0, np.nan)
    ugly_data["goals_per90"]        = (ugly_data["goals"]   / mins * 90).round(3)
    ugly_data["assists_per90"]      = (ugly_data["assists"] / mins * 90).round(3)
    ugly_data["xg_per90"]           = (ugly_data["xg"]      / mins * 90).round(3)
    ugly_data["xa_per90"]           = (ugly_data["xa"]      / mins * 90).round(3)
    ugly_data["goal_contributions"] = ugly_data["goals"].fillna(0) + ugly_data["assists"].fillna(0)
    ugly_data["xg_overperformance"] = (ugly_data["goals"] - ugly_data["xg"]).round(3)

#What season & league are we looking @
    ugly_data["league"] = Leagues[league]
    ugly_data["season"] = f"{season}/{str(season + 1)[-2:]}"

    start_data = ugly_data[ugly_data["minutes"] > 0].reset_index(drop=True) #Get rid of the bums who did not play during the given season
    #Let me be clear they are miles better than me.
    front = ["season", "league", "player", "team", "position"]
    rest  = [c for c in start_data.columns if c not in front]
    return start_data[front + rest]


#Team data
def build_teams_df(raw: dict, league: str, season: int) -> pd.DataFrame:
    rows = []
    for team_id, info in raw.items():
        history = info.get("history", [])
        if not history:
            continue
        #Track how each team did from match history and give me my stats to use later
        wins   = sum(1 for m in history if m.get("wins")  == 1) 
        draws  = sum(1 for m in history if m.get("draws") == 1)
        losses = sum(1 for m in history if m.get("loses") == 1)
        gf     = sum(float(m.get("scored", 0)) for m in history) #Goals for metric 
        ga     = sum(float(m.get("missed", 0)) for m in history) #Goals allowed
        xg     = sum(float(m.get("xG",     0)) for m in history) #Add up the expected goals 
        #Each shot is on a 0 - 1 scale taking into a crap ton of variables to measure it
        xga    = sum(float(m.get("xGA",    0)) for m in history) #Sum up the expected goals allowed
        #Round a few things and do some calculations to make this look a little pretty 
        rows.append({
            "team":           info.get("title", "Unknown"),
            "games_played":   len(history),
            "wins":           wins,
            "draws":          draws,
            "losses":         losses,
            "goals_scored":   int(gf),
            "goals_conceded": int(ga),
            "goal_diff":      int(gf - ga),
            "points":         wins * 3 + draws, #3 pts for a win & 1 pt for a draw (not sure if that is common knowledge, but just in case...)
            "xg":             round(xg,  2), #Round so these are not disgusting to look at 
            "xga":            round(xga, 2),
            "xg_diff":        round(xg - xga, 2)}) 

#Build the dataframe and let's see if it is empty (that will be so upsetting)
    clean_data = pd.DataFrame(rows)
    if clean_data.empty:
        return clean_data

#Sort the teams by pts, goal diff and goals scored (that is the tie breaker system [determines league position] if teams are tied on points)
    sorted = clean_data.sort_values(
        ["points", "goal_diff", "goals_scored"],
        ascending=[False, False, False]
    ).reset_index(drop=True)
    sorted.insert(0, "position", sorted.index + 1) #Remember that index starts @ 0, so add 1 to each to get actual position

    sorted["league"]       = Leagues[league] #Looks through each league
    sorted["season"] = f"{season}/{str(season + 1)[-2:]}" #Looks through each season

    front = ["season", "league", "position", "team", "points"] #Set the order of how I want the printed table to appear
    rest  = [c for c in sorted.columns if c not in front]
    return sorted[front + rest]

#RUN IT -Chris Brown

def run_scraper(leagues: list, seasons: list) -> tuple:
    player_frames = [] #Create empty lists to hold dataframes
    team_frames   = []
    total = len(leagues) * len(seasons)
    done  = 0

    #I LOOKED THIS UP I HAD NO CLUE WHAT I WAS DOING AND WAS TIRED OF GETTING BLOCKED FROM SCRAPING
    understat = UnderstatClient()
#Let's me pull the data for each league and then build my dataframes (understat has a specific function when scraping their website)

    for league in leagues:
        for season in seasons:
            done += 1
            label = f"{season}/{str(season + 1)[-2:]}"
            log.info(f"[{done}/{total}] {Leagues[league]} — {label}")
            #Let's me know what league is currently being worked on/ what has already been done
            try:
                #Grab player data
                raw_players = understat.league(league=league).get_player_data(season=str(season))
                if raw_players:
                    df = build_players_df(raw_players, league, season)
                    player_frames.append(df)
                    log.info(f"  Players : {len(df):,} rows")
                else:
                    log.warning(f"Uh oh no player data returned. Crud...")

                time.sleep(REQUEST_DELAY)

                #Pull team data
                raw_teams = understat.league(league=league).get_team_data(season=str(season))
                if raw_teams:
                    raw_data = build_teams_df(raw_teams, league, season)
                    team_frames.append(raw_data)
                    log.info(f"  Teams   : {len(raw_data)} rows")
                else:
                    log.warning(f"No team data returned. I AM BROKEN!!!")

                time.sleep(REQUEST_DELAY)

            except Exception as e:
                log.error(f"Failed for {league} {label}: {e} get back to work.")
                continue

    #Save all the data to individual CSVs
    if player_frames:
        all_players = pd.concat(player_frames, ignore_index=True)
        path = Output_spot / "player_scraped_data.csv"
        all_players.to_csv(path, index=False)
        log.info(f"\n IT WORKED! player_scraped_data.csv — {len(all_players):,} rows → {path}")
    else:
        all_players = pd.DataFrame()
        log.error("No player data collected. Go fish...")

    if team_frames:
        all_teams = pd.concat(team_frames, ignore_index=True)
        path = Output_spot / "understat_teams_data.csv"
        all_teams.to_csv(path, index=False)
        log.info(f"\n IT WORKED!! understat_teams_data.csv   — {len(all_teams):,} rows → {path}")
    else:
        all_teams = pd.DataFrame()
        log.error("This is broken and no team data was collected. You successfully wasted your own time!!!")

    return all_players, all_teams

#CLI [Command Line Interface](This is where I am making sure that I have everything working)
#Allows me to pull specific data instead of everything under the sun (on the page)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape Understat player + team data into CSVs (2015-2024)"
    )
    parser.add_argument(
        "--leagues", nargs="+", choices=list(Leagues.keys()),
        default=list(Leagues.keys()), metavar="LEAGUE",
        help=f"Leagues: {list(Leagues.keys())}  (default: all)") 
    #Looks through each individual league and makes sure to only scrape valid leagues listed above 

    parser.add_argument(
        "--seasons", nargs="+", type=int, default=Seasons, metavar="YEAR",
        help="Season START years --seasons 2020 2021  (2020 = 2020/21 season)")
    #Only looks through the seasons listed in Seasons variable above 

    return parser.parse_args()
    #Make sure data is clean and not broken.



if __name__ == "__main__":
    args = parse_args()

    invalid = [s for s in args.seasons if s < 2015 or s > 2024] #SHOULD BREAK IF OUTSIDE OF THIS RANGE
    if invalid:
        print(f"Warning: removing out-of-range seasons: {invalid}")
        args.seasons = [s for s in args.seasons if 2015 <= s <= 2024] #Do not allow outside of range data into the set

    if not args.seasons:
        print("No valid seasons. Exiting.")
        exit(1) 

    log.info("=" * 60)
    log.info("Understat Scraper — Players + Team Standings")
    log.info(f"Leagues : {args.leagues}")
    log.info(f"Seasons : {[f'{s}/{str(s+1)[-2:]}' for s in args.seasons]}")
    log.info("=" * 60)
    #Makes my data readable and prints seasons in the format of 2020/2021 opposed to 2020

    players, teams = run_scraper(leagues=args.leagues, seasons=args.seasons)

#These let me know if I messed up everything, and if they tell me I did... oh boy 
    if not players.empty: #AKA if we have data saved, it will show the first 5
        print(f"\n Player sample ───────────────────────────────────────────")
        print(players[["season","league","player","team","goals","assists","xg"]].head(5).to_string(index=False))
        #Pull the first 5 players

    if not teams.empty: #If team data has something this will print
        print(f"\n Team standings sample ───────────────────────────────────")
        print(teams[["season","league","position","team","points","xg","xga"]].head(5).to_string(index=False))
        #Pull the first 5 teams 
