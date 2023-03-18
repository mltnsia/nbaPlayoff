
import pandas as pd
import numpy as np
from pynytimes import NYTAPI
from datetime import datetime
import csv
from textblob import TextBlob

nba_seasons = {
    '2006-2007': ['31/10/2006','14/06/2007','15/06/2007','29/10/2007'],
    '2007-2008': ['30/10/2007','17/06/2008','18/06/2008','27/10/2008'],
    '2008-2009': ['28/10/2008', '14/06/2009','15/06/2009','26/10/2009'],
    '2009-2010': ['27/10/2009', '17/06/2010','18/06/2010','25/10/2010'],
    '2010-2011': ['26/10/2010', '12/06/2011','13/06/2011','24/12/2011'],
    '2011-2012': ['25/12/2011', '21/06/2012','22/06/2012','29/10/2012'],
    '2012-2013': ['30/10/2012', '20/06/2013','21/06/2013','28/10/2013'],
    '2013-2014': ['29/10/2013', '15/06/2014','16/06/2014','27/10/2014'],
    '2014-2015': ['28/10/2014', '16/06/2015','17/06/2015','26/10/2015'],
    '2015-2016': ['27/10/2015', '19/06/2016','20/06/2016','24/10/2016'],
    '2016-2017': ['25/10/2016', '12/06/2017','13/06/2017','16/10/2017'],
    '2017-2018': ['17/10/2017', '08/06/2018','09/06/2018','15/10/2018'],
    '2018-2019': ['16/10/2018', '13/06/2019','15/06/2019','21/10/2019'],
    '2019-2020': ['22/10/2019', '11/10/2020','12/10/2020','21/12/2020'],
    '2020-2021': ['22/12/2020', '22/07/2021','23/07/2021','18/10/2021'],
    '2021-2022': ['19/10/2021', '19/06/2022','20/06/2022','17/10/2022']
}

api_key = "0W1lEGuYhGRSA8hHL5PJTG4Xb3GA4oA9"
nyt = NYTAPI(api_key, parse_dates=True)

final_df = pd.DataFrame(columns=['season', 'team', 'score'])

for season, dates in nba_seasons.items():
    offseason_start_str = dates[2]
    offseason_end_str = dates[3]
    date_format = "%d/%m/%Y"
    offseason_start = datetime.strptime(offseason_start_str, date_format)
    offseason_end = datetime.strptime(offseason_end_str, date_format)
    
    articles = nyt.article_search(query = "N.B.A.",
                              results = 500,
                             dates = {
                                 "begin": offseason_start,
                                 "end": offseason_end
                             },
                             options = {
                                 "section_name": [
                                     "Sports"
                                 ]
                             })
    
    sentiment_scores = {}
    
    for x in articles:
        text = x["lead_paragraph"] + " " + x["abstract"]
        text = text.lower().replace(".", "").replace(",", "")
        blob = TextBlob(text)

        sentiment_score = blob.sentiment.polarity

        for keyword in ["celtics", "nets", "knicks", "76ers", "raptors",
                       "bulls", "cavaliers", "pistons", "pacers", "bucks",
                       "hawks", "hornets", "heat", "magic", "wizards",
                       "nuggets", "timberwolves", "thunder", "trail blazers", "jazz",
                       "warriors", "clippers", "lakers", "suns", "kings",
                       "mavericks", "rockets", "grizzlies", "pelicans", "spurs"]:
            if keyword in text:
                if keyword not in sentiment_scores:
                    sentiment_scores[keyword] = []
                sentiment_scores[keyword].append(sentiment_score)

    for team in sentiment_scores:
        sentiment_scores[team] = sum(sentiment_scores[team])/len(sentiment_scores[team])

    teams = list(sentiment_scores.keys())   
    scores = list(sentiment_scores.values())
    df = pd.DataFrame(columns=['season', 'team', 'score'])
    df['team'] = teams
    df['score'] = scores
    df['season'] = season
    final_df = final_df.append(df, ignore_index=True, sort=False)

final_df['season'] = final_df['season'].str.slice(5)
final_df['season'] = pd.to_numeric(final_df['season'])
print(final_df)

final_df.to_csv('nyt_scrape.csv', index=False)
