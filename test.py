import pandas as pd
import numpy as np

df = pd.DataFrame([[np.nan,'P3:pass','D1:xxxxx','M2:yyyy','R01'],
                   ['P1:OK','M1:failed','D2:zzzzz','M2:aaaaaa','R02'],
                   ['D2:Denied','M1:bbbbb',np.nan,np.nan,'R03']],
                  columns=['R01Q01','R01Q02','R01Q03','R01Q04','r_id'])

print(df)

df.loc[2].iat[2]
z = []

def combine_response(df):
    for row in range(len(df)):
        for col in df.columns:
            if col.startswith('R'):
                if pd.notna(df.loc[row].at[col]):
                    x = (str(df.loc[row].at[col]))
                    y = str(col) + (x[0:2])
                    df.loc[row].at[col] = y
    df['output'] = [y[pd.notna(y)].tolist() for y in df.values]
    return df

print(df)

combine_response(df)

'''
for row in range(len(df)):
    for col in df.columns:
        if col.startswith('Q'):
            if df.loc[row].at[col].notna():
                x = (str(df.loc[row].at[col]))
                y = str(col) + (x[0:2])
                df['output'] = [x[pd.notna(x)].tolist() for x in df.values]
                
                 and df.loc[row].at[col] != 'NaN'
'''

one = {'a': '2', 'c': 't', 'b': '4'}
two = {'a': '3.4', 'c': '7.6'}
three = {'a': 1.2, 'c': 3.4, 'd': '2.3'}

new_dict = {}
list_dict = [one, two, three]

for d in list_dict:
    for key in d:
        if key not in new_dict:
            new_dict[key] = []
        new_dict[key].append(d[key])

print(new_dict)