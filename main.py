#Import Library
import re
import pandas as pd

print("Pandas version",pd.__version__)

from googletrans import Translator
translator = Translator()

#Import file
form_url = 'https://docs.google.com/spreadsheets/d/1qfNAL6iQ_gHhRkUn7QTZ88pjTUGHn2L_eLMQ_9yp_kQ/edit#gid=1736157131'
def gsheet2excel(x):
    e = 'export?format=xlsx&'
    excel_url =  x.replace('edit',e)
    print(excel_url)
    return excel_url
x = gsheet2excel(form_url)

df = pd.read_excel(x)

#Translate column head
df_en = df.copy()
df_en
df_en.rename(columns=lambda x: translator.translate(x).text, inplace=True)
col_head = df_en.columns

print(col_head)

#Edit column header to code
for col in df_en.columns:
    if col[0] == "Q":
        df_en.rename({col:str(col[0:3])},axis=1,inplace = True)
df_en.columns

print(df.columns)

#Edit main column header
df_en.rename({
    "Timestamp":"timestamp",
    "Name of surveyed station":"stn_name",
    "Name of data recorder":"agent_name",
    "Choose a facility":"r_id",
    "Name the facility.":"acc_name",
    "Specify the location of the facility.":"acc_loc",
    "Upload a review of facility images (maximum 10 images).":"acc_img",
    "Additional reviews of this facility":"acc_comment"
    },axis = 1, inplace = True)

print(df_en.columns)
df_en

#Simplify R Response
df_en['r_id'] = df_en['r_id'].str.slice_replace(3,repl='')
print(df_en['r_id'])

#Simplify Question Response
for col in df_en.columns:
    if col[0] == 'Q':
        for q in df_en[col]:
            if df_en.q.notnull().values.any():
                print(df_en[q])

            


df_en
'''