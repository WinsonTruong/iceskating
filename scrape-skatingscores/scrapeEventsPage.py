import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

class scrapeEvents:
    """
    Scrapes the events table for a given skating season on skatingscores.com
    """

    def __init__(self, url):
        self.url = url
        events_raw = pd.read_html(self.url)[1]
        events_raw.columns = ['Country', 'Event_Abbreviation', 'Event_Name', 'Event_Begin']
        self.events_raw = events_raw


    def scrape(self):
        df = pd.read_html(self.url)[1]

        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        soup.prettify()
        tables = soup.find_all("tbody")

        links = []
        for tr in tables[1].findAll("tr"):
            trs = tr.findAll("td")
            for each in trs:
                try:
                    link = each.find('a')['href']
                    links.append(link)
                except:
                    pass
        links_to_events = [self.url + i[6:] for i in links]
        abbrv_of_valid_events = [i[len(self.url):-1].upper() for i in links_to_events] # some events were cancelled and are not pulled via this method above
        
        links_to_completed_events = pd.DataFrame()
        links_to_completed_events['Abbreviation'], links_to_completed_events['URL'] = abbrv_of_valid_events, links_to_events
        
        self.completed_events = links_to_completed_events

        self.events = pd.merge(left = self.events_raw, right = self.completed_events, left_on = 'Event_Abbreviation', right_on = 'Abbreviation', how = 'inner')

