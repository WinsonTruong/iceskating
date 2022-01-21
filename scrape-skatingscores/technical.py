import pandas as pd 

def deepen_technical(df):
    include = ['Name', 'Country', 'Element', 'Event', 'BaseValue'] #excluded: ', 'GOETotal'
    columns_to_fix = []
    for i in df.columns:
        if i in include:
            pass
        else:
            columns_to_fix.append(i)
    return df.melt(id_vars = include, value_vars = columns_to_fix).rename(columns = {0: 'JudgeNationality', 'value': 'IndividualGOE'})
