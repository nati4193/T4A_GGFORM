import pandas as pd

df = pd.DataFrame([[0, 2, 3], [0, 4, 1], [10, 20, 30]],
                  index=[4, 5, 6], columns=['A', 'B', 'C'])
print(df)

df.at[4, 'B']

df.loc[5].at['B']

