'''
Convenience functions based on baseball_scraper. 

Currently this just scrapes statcast, which does not permit downloading .csvs of event data.


Documentation on baseball_scraper: https://pypi.org/project/baseball-scraper/
'''

import baseball_scraper
import pandas as pd
import datetime

def statcast_scrape(start,end):
    '''
    Returns a DataFrame of all the successfull scraped time slices in range start, end. 
    
    If an exception is raised, prints a brief report, stops scraping, and returns
    all the successfully scraped slices.

    Usefull because large scrapes take a long time but cancel when they raise Exceptions that
    are generated from the target side. This function allows you to restart the scrape near
    where the exception raised.

    Parameters
    ----------
    start: datetime.date
        A datetime date object specifying the first date you want the scraper to return.
    
    end: datetime.date
        A datetime date object specifying the last date, inclusive, you want the scraper to return.

    Returns
    -------
    A pd.DataFrame object containinng all the successfully scraped time slices in the range.
    '''
    scrapes = [] ##
    while True:
        try:
            temp = baseball_scraper.statcast(start.strftime("%Y-%m-%d"), (start+datetime.timedelta(days=4)).strftime("%Y-%m-%d"))
        except ParserError:
            print("ParserError failure at {}".format(start.strftime("%Y-%m-%d")))
            break
        except:
            print("Unspecified failure at {}".format(start.strftime("%Y-%m-%d")))
            break
        scrapes.append(temp)
        start = start+datetime.timedelta(days=5)
        if start > end:
            break
    return pd.concat(scrapes)

def update_statcast(target_csv_name):
    '''
    Scapes any statcast data after the last game_date found
    in the year of the target file and adds it, returning a DataFrame that concatenates the
    new data with the old.
    
    '''
    out = pd.read_csv(target_csv_name)
    start = pd.Timestamp(out['game_date'].sort_values().iloc[-1])
    end = datetime.datetime.now()
    new = statcast_scrape(start, end)
    out = pd.concat([out,new])
    return out