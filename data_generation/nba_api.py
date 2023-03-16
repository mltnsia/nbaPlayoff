import pandas as pd
import numpy as np
from nba_api.stats import endpoints

# list of seasons to pull data from API
seasons = ["2020-21", "2019-20", "2018-19", "2017-18", "2016-17", "2015-16", "2014-15", "2013-14", "2012-13", "2011-12", "2010-11", "2009-10", "2008-09", "2007-08", "2006-07", "2005-06", "2004-05"]

def get_initial_table():
    # initialize df with latest full season 21/22
    df = endpoints.leaguestandings.LeagueStandings(season="2021-22").standings.get_data_frame()[['SeasonID', 'TeamID', 'TeamCity', 'TeamName', 'Conference', 'PlayoffRank', 'WinPCT', 'DiffPointsPG']]

    # concatenate all seasons in list to df
    for i in seasons:
        temp_df = endpoints.leaguestandings.LeagueStandings(season=i).standings.get_data_frame()[['SeasonID', 'TeamID', 'TeamCity', 'TeamName', 'Conference', 'PlayoffRank', 'WinPCT', 'DiffPointsPG']]
        df = pd.concat([df, temp_df])

    # change seasonid type to numeric
    df["SeasonID"] = pd.to_numeric(df["SeasonID"])

    return df

def get_final_table():
    # playoffrank lag lists that will become columns
    PlayoffRankLag1 = []
    PlayoffRankLag2 = []
    PlayoffRankLag3 = []

    # winpct lag lists that will become columns
    WinPCTLag1 = []
    WinPCTLag2 = []
    WinPCTLag3 = []

    # diffpointspg lag lists that will become columns
    DiffPointsPGLag1 = []
    DiffPointsPGLag2 = []
    DiffPointsPGLag3 = []

    df = get_initial_table()

    # 2004/05 was the first season NBA had 30 teams
    # to get 3 lagged years for each team, final season has to be 2007/08

    # loop through df and append 3 lags into lists
    for i, row in df.iterrows():
        currentTeamID = row.TeamID
        currentSeasonID = row.SeasonID
        if currentSeasonID >= 22007:
            for n in range(1, 4):
                eval(f'PlayoffRankLag{n}').append(df[(df["SeasonID"] == currentSeasonID - n) & (df["TeamID"] == currentTeamID)].iloc[0]["PlayoffRank"]) # append lagged playoff rank into list
                eval(f'WinPCTLag{n}').append(df[(df["SeasonID"] == currentSeasonID - n) & (df["TeamID"] == currentTeamID)].iloc[0]["WinPCT"]) # append lagged winpct into list
                eval(f'DiffPointsPGLag{n}').append(df[(df["SeasonID"] == currentSeasonID - n) & (df["TeamID"] == currentTeamID)].iloc[0]["DiffPointsPG"]) # append lagged diffpointspg into list
        else:
            for n in range(1, 4):
                eval(f'PlayoffRankLag{n}').append(None)
                eval(f'WinPCTLag{n}').append(None)
                eval(f'DiffPointsPGLag{n}').append(None)

    # convert lagged lists into df columns
    for n in range(1, 4):
        df[f"PlayoffRankLag{n}"] = eval(f'PlayoffRankLag{n}')
        df[f"WinPCTLag{n}"] = eval(f'WinPCTLag{n}')
        df[f"DiffPointsPGLag{n}"] = eval(f'DiffPointsPGLag{n}')

    # remove rows with nan values
    df_nonulls = df[df['PlayoffRankLag1'].notna()]

    # create target column from playoff rank
    df_nonulls['isPlayoff'] = (df_nonulls['PlayoffRank'] <= 8).astype(int)

    # split df into east and west conferences
    df_east = df_nonulls[df_nonulls["Conference"] == "East"]
    df_west = df_nonulls[df_nonulls["Conference"] == "West"]

    # drop current playoff rank, winpct, diffpointspg, and conference columns
    df_east = df_east.drop(columns=['PlayoffRank', 'Conference', 'WinPCT', 'DiffPointsPG'])
    df_west = df_west.drop(columns=['PlayoffRank', 'Conference', 'WinPCT', 'DiffPointsPG'])

    return df_east, df_west