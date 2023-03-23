import pandas as pd
import numpy as np
from nba_api.stats import endpoints

# list of seasons to pull data from API
seasons = ["2005-06", "2006-07", "2007-08", "2008-09", "2009-10", "2010-11", "2011-12", "2012-13", 
           "2013-14", "2014-15", "2015-16", "2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]

def get_initial_table():
    # initialize df with latest full season 21/22
    df = endpoints.leaguestandings.LeagueStandings(season="2004-05").standings.get_data_frame()[['SeasonID', 'TeamID', 'TeamCity', 'TeamName', 'Conference', 'PlayoffRank', 'WinPCT', 'DiffPointsPG']]

    # concatenate all seasons in list to df
    for i in seasons:
        temp_df = endpoints.leaguestandings.LeagueStandings(season=i).standings.get_data_frame()[['SeasonID', 'TeamID', 'TeamCity', 'TeamName', 'Conference', 'PlayoffRank', 'WinPCT', 'DiffPointsPG']]
        df = pd.concat([df, temp_df])

    # change seasonid type to numeric
    df["SeasonID"] = df["SeasonID"].str[1:]
    df["SeasonID"] = pd.to_numeric(df["SeasonID"])

    ### uncomment to create mapping csv
    # create teamID to teamName and conference mapping
    # idNameMapping = df[["TeamID", 'TeamName', 'Conference']][df['SeasonID'] == 2021].set_index('TeamID')
    # idNameMapping.to_csv('id_name_mapping.csv')

    return df

def get_final_table():

    df = get_initial_table()

    # playoffrank lag lists that will become columns
    PlayoffRankLag1 = []
    PlayoffRankLag2 = []
    PlayoffRankLag3 = []
    PlayoffRankLag4 = []

    # winpct lag lists that will become columns
    WinPCTLag1 = []
    WinPCTLag2 = []
    WinPCTLag3 = []
    WinPCTLag4 = []

    # diffpointspg lag lists that will become columns
    DiffPointsPGLag1 = []
    DiffPointsPGLag2 = []
    DiffPointsPGLag3 = []
    DiffPointsPGLag4 = []

    # 2004/05 was the first season NBA had 30 teams
    # to get 3 lagged years for each team, final season has to be 2007/08

    # loop through df and append 3 lags into lists
    for i, row in df.iterrows():
        currentTeamID = row.TeamID
        currentSeasonID = row.SeasonID
        if currentSeasonID >= 2008:
            for n in range(1, 5):
                eval(f'PlayoffRankLag{n}').append(df[(df["SeasonID"] == currentSeasonID - n) & (df["TeamID"] == currentTeamID)].iloc[0]["PlayoffRank"]) # append lagged playoff rank into list
                eval(f'WinPCTLag{n}').append(df[(df["SeasonID"] == currentSeasonID - n) & (df["TeamID"] == currentTeamID)].iloc[0]["WinPCT"]) # append lagged winpct into list
                eval(f'DiffPointsPGLag{n}').append(df[(df["SeasonID"] == currentSeasonID - n) & (df["TeamID"] == currentTeamID)].iloc[0]["DiffPointsPG"]) # append lagged diffpointspg into list
        else:
            for n in range(1, 5):
                eval(f'PlayoffRankLag{n}').append(None)
                eval(f'WinPCTLag{n}').append(None)
                eval(f'DiffPointsPGLag{n}').append(None)

    # convert lagged lists into df columns
    for n in range(1, 5):
        df[f"PlayoffRankLag{n}"] = eval(f'PlayoffRankLag{n}')
        df[f"WinPCTLag{n}"] = eval(f'WinPCTLag{n}')
        df[f"DiffPointsPGLag{n}"] = eval(f'DiffPointsPGLag{n}')

    # remove rows with nan values
    df = df[df['PlayoffRankLag1'].notna()]

    # create target column from playoff rank
    df['isPlayoff'] = (df['PlayoffRank'] <= 8).astype(int)

    # split df into east and west conferences
    # df_east = df[df["Conference"] == "East"]
    # df_west = df[df["Conference"] == "West"]

    # drop current playoff rank, winpct, diffpointspg, and conference columns
    # df_east = df_east.drop(columns=['PlayoffRank', 'Conference', 'WinPCT', 'DiffPointsPG', 'TeamCity', 'TeamName']).reset_index(drop=True)
    # df_west = df_west.drop(columns=['PlayoffRank', 'Conference', 'WinPCT', 'DiffPointsPG', 'TeamCity', 'TeamName']).reset_index(drop=True)
    df = df.drop(columns=['PlayoffRank', 'Conference', 'WinPCT', 'DiffPointsPG', 'TeamCity', 'TeamName']).reset_index(drop=True)

    ### uncomment to create csv
    # df.to_csv('df.csv')

    # df_east.to_csv('df_east.csv')
    # df_west.to_csv('df_west.csv')

    return df