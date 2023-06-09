
from TeamsSubreddit import teams_subreddit, teams_name
from textblob import TextBlob
import numpy as np
from NBASeasons import nba_seasons, years
import pandas as pd
import datetime
import requests

def run_dates(start_date, end_date):
    one_day = datetime.timedelta(1)
    start_dates = [start_date]
    end_dates = []
    today = start_date
    while today < end_date:
        tomorrow = today + one_day
        if tomorrow.month != today.month:
            start_dates.append(tomorrow)
            end_dates.append(today)
        today = tomorrow
    end_dates.append(end_date)
    dict = {}
    # print(start_dates)
    # print(end_dates)
    for i in range(len(start_dates)):
        dict[start_dates[i]] = end_dates[i]
    # print(dict)
    return dict

# start_date = datetime.datetime(2022, 1, 1)
# end_date = datetime.datetime(2022, 2, 28)
# run_dates(start_date, end_date)


def get_submission_df(start_date, end_date, team_name):
    dates_dict = run_dates(start_date,end_date)
    # print(dates_dict)
    output = pd.DataFrame()
    subreddit = ['nba','nbadiscussion',teams_subreddit[team_name]]

    for subreddit in subreddit:
        for key, value in dates_dict.items():
                start_epoch = int(key.timestamp())
                end_epoch = int(value.timestamp())

                urls_submission = f'https://api.pushshift.io/reddit/search/submission/?subreddit={subreddit}&q={team_name}&after={start_epoch}&before={end_epoch}&size=1000'
                response_submission = requests.get(urls_submission)
                df_submission = pd.DataFrame(response_submission.json()['data'])
                # print(len(df_submission))
                output = pd.concat([output,df_submission])
    output.reset_index(drop=True)
    # print(len(output))
    return output


def get_comment_df(start_date, end_date, team_name):
    dates_dict = run_dates(start_date,end_date)
    # print(dates_dict)
    output = pd.DataFrame()
    subreddit = ['nba','nbadiscussion',teams_subreddit[team_name]]

    for subreddit in subreddit:
        for key, value in dates_dict.items():
                start_epoch = int(key.timestamp())
                end_epoch = int(value.timestamp())

                urls_submission = f'https://api.pushshift.io/reddit/search/comment/?subreddit={subreddit}&q={team_name}&after={start_epoch}&before={end_epoch}&size=1000'
                response_submission = requests.get(urls_submission)
                df_submission = pd.DataFrame(response_submission.json()['data'])
                # print(len(df_submission))
                output = pd.concat([output,df_submission])
    output.reset_index(drop=True)
    # print(len(output))
    return output



# date = '18/06/2008'
def to_date(date):
    day = int(date[0:2])
    month = int(date[3:5])
    year = int(date[6:10])
    time = datetime.time(0,0,0)
    date2 = datetime.datetime(year, month, day)
    combined = datetime.datetime.combine(date2, time)
    return combined

# to_date(date)


def remove_punctuations(text):
    punct =['%','/',':','\\','&amp;','&',';', '?']
    for punctuation in punct:
        text = text.replace(punctuation, '')
    return text



def process_df(df, type):
    if type == 'comment':
        df['body'] = df['body'].apply(lambda x: remove_punctuations(x))
        df2 = df[df.body != '']

        df3 = df2.reset_index()
        df4 = df3[['body']]
        df4.rename(columns = {'body':'text'}, inplace = True)

    elif type == "submission":
        df['selftext'] = df['selftext'].apply(lambda x: remove_punctuations(x))
        df2 = df[df.selftext != '']

        df3 = df2.reset_index()
        df4 = df3[['selftext']]
        df4.rename(columns = {'selftext':'text'}, inplace = True)
    return df

def get_subjectivity(text):
    return TextBlob(text).sentiment.subjectivity

def get_polarity(text):
    return TextBlob(text).sentiment.polarity

# df = process_df(df)
def process_textblob(df):
    df['subjectivity'] = df['text'].apply(get_subjectivity)
    df['polarity'] = df['text'].apply(get_polarity)
    # Obtain polarity scores generated by TextBlob
    df['textblob_score'] = df['text'].apply(lambda x: TextBlob(x).sentiment.polarity)
    # Convert polarity score into sentiment categories
    # neutral_threshold = 0.05
    # df['textblob_sentiment'] = df['textblob_score'].apply(lambda c: 'Positive' if c >= neutral_threshold else ('Negative' if c <= -(neutral_threshold) else 'Neutral'))

    return df

def avg_textblob(df):
    return df['textblob_score'].mean()


def main():
    output = pd.DataFrame(columns = ["year", "sentiment_score", "team_name"])
    year_list = []
    team_name = []
    sentiment_score = []
    for team in teams_name:
        for year in years:
            print(year + ", " + team)
            year_list.append(year)
            team_name.append(team)
            offseason_start = to_date(nba_seasons[year][2])
            offseason_end = to_date(nba_seasons[year][3])

            df = get_comment_df(offseason_start,offseason_end, team)
            if df.empty == True:
                sentiment_score.append(0)
            else:
                df = process_df(df, 'comment')
                df = process_textblob(df)
                value = avg_textblob(df)
                sentiment_score.append(value)

    output['year'] = year_list
    output['team_name'] = team_name
    output['sentiment_score'] = sentiment_score
    
    output.to_csv('reddit_sentiment_score.csv')
    return output

# main()
