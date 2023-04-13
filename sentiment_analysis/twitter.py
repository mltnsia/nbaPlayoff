import pandas as pd
import numpy as np
import nltk
import os
from nltk.corpus import stopwords
from textblob import TextBlob

import itertools

# list of names and dates
keywords = ['NBA Atlanta Hawks', 'NBA Boston Celtics', 'NBA Brooklyn Nets', 'NBA Charlotte Hornets', 'NBA Chicago Bulls', 'NBA Cleveland Cavaliers', 'NBA Dallas Mavericks', 'NBA Denver Nuggets', 'NBA Detroit Pistons', 'NBA Golden State Warriors', 'NBA Houston Rockets', 'NBA Indiana Pacers', 'NBA Los Angeles Clippers', 'NBA Los Angeles Lakers', 'NBA Memphis Grizzlies', 'NBA Miami Heat', 'NBA Milwaukee Bucks', 'NBA Minnesota Timberwolves', 'NBA New Orleans Pelicans', 'NBA New York Knicks', 'NBA Oklahoma City Thunder', 'NBA Orlando Magic', 'NBA Philadelphia 76ers', 'NBA Phoenix Suns', 'NBA Portland Trail Blazers', 'NBA Sacramento Kings', 'NBA San Antonio Spurs', 'NBA Toronto Raptors', 'NBA Utah Jazz', 'NBA Washington Wizards']
nba_offseasons = [('2007-06-15', '2007-10-29', '2007'), ('2008-06-18', '2008-10-27', '2008'), ('2009-06-15', '2009-10-26', '2009'), ('2010-06-18', '2010-10-25', '2010'), ('2011-06-13', '2011-12-24', '2011'), ('2012-06-22', '2012-10-29', '2012'), ('2013-06-21', '2013-10-28', '2013'), ('2014-06-16', '2014-10-27', '2014'), ( '2015-06-17', '2015-10-26', '2015'), ('2016-06-20', '2016-10-24', '2016'), ('2017-06-13', '2017-10-16', '2017'), ('2018-06-19', '2018-10-15', '2018'), ('2019-06-15', '2019-10-21', '2019'), ('2020-10-12', '2020-12-21', '2020'), ('2021-07-23', '2021-10-18', '2021'), ('2022-06-20', '2022-10-17', '2022')]

# create a list of queries
queries = list(itertools.product(nba_offseasons, keywords))

# print the list of queries
#print(queries)

# account for team name changes

#2008-2011 Brooklyn Nets were New Jersey Nets
queries[2]= (queries[2][0], "NBA New Jersey Nets")
queries[32]= (queries[32][0], "NBA New Jersey Nets")
queries[62]= (queries[62][0], "NBA New Jersey Nets")
queries[92]= (queries[92][0], "NBA New Jersey Nets")

#2008-2012 Charlotte Hornets were Charlotte Bobcats
queries[3]= (queries[3][0], "NBA Charlotte Bobcats")
queries[33]= (queries[33][0], "NBA Charlotte Bobcats")
queries[63]= (queries[63][0], "NBA Charlotte Bobcats")
queries[93]= (queries[93][0], "NBA Charlotte Bobcats")
queries[123]= (queries[123][0], "NBA Charlotte Bobcats")

#2008-2013 New Orleans Pelicans were New Orleans Hornets
queries[18]= (queries[18][0], "NBA New Orleans Hornets")
queries[48]= (queries[48][0], "NBA New Orleans Hornets")
queries[78]= (queries[78][0], "NBA New Orleans Hornets")
queries[108]= (queries[108][0], "NBA New Orleans Hornets")
queries[138]= (queries[138][0], "NBA New Orleans Hornets")
queries[168]= (queries[168][0], "NBA New Orleans Hornets")

#Data Preprocessing 
stop = nltk.download('stopwords')
stop = stopwords.words('english')

#Remove unnecessary characters
punct = ['%','/',':','\\','&amp;','&',';', '?', '\n']

def remove_punctuations(text):
    for punctuation in punct:
        text = text.replace(punctuation, '')
    return text

# create an empty list to store the DataFrames
dfs = []

i = 0
# loop over the list and run the code for each pair
for query in queries:
    keyword = query[1]
    dates = query[0]
    since_date, until_date, season = dates
    filename = f"{keyword.replace(' ', '-')}-{since_date}-{until_date}-tweets.json"
    command = f"snscrape --jsonl --max-results 2000 --since {since_date} twitter-search '{keyword} until:{until_date}' > {filename}"
    os.system(command)
    
    # read in the JSON file as a pandas DataFrame and append it to the list
    df = pd.read_json(filename, lines=True)
    
    # check if the dataframe is empty
    if df.empty:
        # fill the dataframe with a neutral content
        df = pd.DataFrame({'renderedContent': ['neutral']})
    
    #print(df['renderedContent'])
    print(i + 1)
    i = i + 1
    
    # Data Loading, Cleaning and Preprocessing

    #keep only renderedContent column and clean tweet data
    df1 = df[['renderedContent']].copy()
    df1 = df1.drop_duplicates('renderedContent')
    df1['renderedContent'].apply(lambda x: [item for item in x if item not in stop])
    df1['renderedContent'] = df1['renderedContent'].apply(lambda x: remove_punctuations(x))
    df1['renderedContent'].replace(' ', np.nan, inplace=True)
    df1.dropna(subset=['renderedContent'], inplace=True)
    
    # calculate the sentiment polarity score for each tweet's content
    df1['polarity'] = df1['renderedContent'].apply(lambda x: TextBlob(x).sentiment.polarity)
    avg_value = df1['polarity'].mean()

    # add columns for the keyword and since_date to the DataFrame
    df2 = pd.DataFrame({'season': season, 'keyword': keyword, 'polarity': avg_value}, index=[0])

    # add the DataFrame to the list
    dfs.append(df2)

result_df = pd.concat(dfs)
result_df.to_csv('twitter_nba_polarity_scores_updated.csv', index=False)