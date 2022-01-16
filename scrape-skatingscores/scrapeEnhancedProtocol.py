import pandas as pd
import numpy as np

import requests
from bs4 import BeautifulSoup
import time

class scrapeEvent:
    """
    Class for scraping the "Enhanced Protocol" scoresheet from skatingscores.com, initates by recording all skaders
    """
    def __init__(self, website, event_name):

        self.event_name = event_name
        self.dfs = pd.read_html(website)

        self.start = 0
        self.n = len(self.dfs)
        self.stop = self.n - 2
        self.sets = []

        start = self.start
        stop = self.stop

        all_skaters = []
        while start <= stop:
            left = start
            start += 11
            right = start

            #bio is located in first dataframe in sets of 11
            raw_bio = self.dfs[left:right][1].iloc[:, 1:] 
            raw_bio.columns = raw_bio.iloc[0,:]
            bio = raw_bio.iloc[1:,:].rename(columns={raw_bio.columns[0]: "Name", raw_bio.columns[1]: "Country"})
            all_skaters.append(bio)

        all_skaters = pd.concat(all_skaters, axis = 0).reset_index(drop = True)
        all_skaters['Event_Name'] = event_name
        self.all_skaters = all_skaters
                    
        time.sleep(0.33) # be nice to the generous server admins!

    def get_component_score(self, drop_rank = True):
        """
        Aggregates all component scores by skater 
        """
        start = self.start
        stop = self.stop

        all_components = []
        skater_count = 0

        while start <= stop:
            left = start
            start += 11
            right = start

            #bio is located in TENTH dataframe in sets of 11
            raw_component = self.dfs[left:right][10].iloc[:, 1:] 
            raw_component.columns = raw_component.iloc[0,:]
            raw_component = raw_component.loc[:,~raw_component.columns.duplicated()]

            component = raw_component.iloc[1:-1, :-1]
            component.index = component['Component']
            component.drop(columns = 'Component', inplace = True)

            component.insert(0, 'Name', self.all_skaters['Name'][skater_count])
            component.insert(1, 'Country', self.all_skaters['Country'][skater_count])
            skater_count += 1     

            all_components.append(component)

        all_components = pd.concat(all_components, axis = 0)
        for c in all_components.loc[:, ~(all_components.columns.isin(['Name', 'Country', 'Factor']))].columns:
            all_components[c] = all_components[c].str.split(' ').str[1]

        all_components['Event'] = self.event_name
        self.all_components = all_components



    def get_technical_score(self):
        """
        Aggregates all technical scores by skater, skates are denoted

        Source: [Wikipedia](https://en.wikipedia.org/wiki/ISU_Judging_System)
        - `*`: element exceeds allotted amount, receives GOE of 0
        - `+REP`: denotes a solo jump that has been performed twice, receiving 70% base value
        - `x`: denotes a 10% bonus halfway after the program
        - `!`: unclear takeoff edge with deduction of [-1,-2] on GOE
        - `e`:incorrect takeoff edge (i.e Lutz with inside edge)
        - `<`: denote under-rotation beginning on ice with [-1/4, -1/2] rotation happening before the jump
        - `<<`: denote under-rotation beginning on ice greater than -1/2 rotation happening before the jump; jump is downgraded one jump
        """
        start = self.start
        stop = self.stop

        all_technical = []
        skater_count = 0

        while start <= stop:
            left = start
            start += 11
            right = start
        
         #bio is located in THIRD dataframe in sets of 11
            raw_technical = self.dfs[left:right][3].iloc[:, 1:] 
            raw_technical = raw_technical.dropna(axis = 1)
            raw_technical.columns = raw_technical.iloc[0,:] #use 1st row as column
            technical = raw_technical.iloc[1:-1, :] # remove last row which contains column sums and the first row containing columns names

            technical.insert(0, 'Name', self.all_skaters['Name'][skater_count])
            technical.insert(1, 'Country', self.all_skaters['Country'][skater_count])
            skater_count += 1     

            all_technical.append(technical)

        all_technical = pd.concat(all_technical, axis = 0).reset_index(drop = True)
        for i in all_technical.columns[3:]:
            all_technical[i] = all_technical[i].astype(float, errors = 'ignore')

        all_technical['Event'] = self.event_name
        self.all_technical = all_technical
