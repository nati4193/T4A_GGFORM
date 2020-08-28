#Import Library
import re
import pandas as pd
import numpy as np
print("Pandas version", pd.__version__)

# Import station database
def getstation():
    df_stn = pd.read_csv(
        r'C:\Users\nngna\OneDrive\Documents\MAYDAY_NATI\T4A_GGFORM\db\m_station_db.csv')
    df_stn = df_stn.rename(columns={"name_th": "stn_name_th"})
    df_stn.info()
    return df_stn

df1 = getstation()

# Import response data
form_url = 'https://docs.google.com/spreadsheets/d/1SN2lYQLvXx6H9FjYAtdPCpT_L0SJzcxfCGmgI7kv_ao/edit#gid=283051997'

def getresponse(url):
    e = 'export?format=xlsx&'
    excel_url =  url.replace('edit',e)
    df = pd.read_excel(excel_url,encoding= 'unicode_escape')
    return df

df2 = getresponse(form_url)

#add index column
df['rec_id'] = df.index.astype(int).int(5)
df_en = df

# Edit column header to code
for col in df_en.columns:
    if col.startswith('Q'):
        df_en.rename({col: str(col[0:3])}, axis=1, inplace=True)
    if col.startswith('Unname'):  #drop unnamed column
        del df_en[str(col)]

df_en.columns

# Edit main column header
df_en.rename({
    "Timestamp": "timestamp",
    "ชื่อสถานีที่สำรวจ": "stn_name_th",
    "ชื่อผู้บันทึกข้อมูล": "agent_name",
    "เลือกสิ่งอำนวยความสะดวก": "r_id",
    "ตั้งชื่อสิ่งอำนวยความสะดวก": "acc_name",
    "ระบุตำแหน่งของสิ่งอำนวยความสะดวก": "acc_loc",
    "อัพโหลดรูปภาพสิ่งอำนวยความสะดวกที่ตรวจสอบ (ไม่เกิน 10 รูป)": "acc_img",
    "ความคิดเห็นเพิ่มเติมถึงสิ่งอำนวยความสะดวกนี้": "acc_comment",
    "Form Response Edit URL": "rec_ref"
}, axis=1, inplace=True)
print(df_en.columns)

# Simplify R Response
df_en['r_id'] = df_en['r_id'].str.slice_replace(3, repl='')
print(df_en['r_id'])

print(df_en.columns)

#separate df
#df_main for df_stn
df_main = df_en[['rec_id','timestamp', 'stn_name_th', 'agent_name', 'r_id', 'acc_name', 'acc_loc','acc_img','acc_comment']]
print(df_main)


# Match Station ID
df_main2 = df_main.merge(df_stn[['stn_name_th','s_id','stn_id','stn_mode']],on='stn_name_th',how='left')

#Check null data
df_main2['s_id'].isnull().sum()

#Question Cleansing
df_ans = df_en.loc[:,df_en.columns.str.contains('rec_id')|df_en.columns.str.contains('Q') | df_en.columns.str.contains('r_id')| df_en.columns.str.contains('stn')]

#Clean Question and Answer of each record
df_ans = df_ans.head(10)
for row in range(len(df_ans)):
    for col in df_ans.columns:
        print(df_ans.loc[row,str(col)])

#Clean answer
list = df_ans.to_numpy().tolist()



df_ans['result'] =

#Export as excel to check
#df_main2.to_excel(r'C:\Users\nngna\OneDrive\Documents\MAYDAY_NATI\T4A_GGFORM\temp\test.xlsx', index = False)


print(df_main2)
'''
#Get Response column
df_en['readed'] = 0


for row,col in df_en.iterrows():
    if df_en.at[row,col].str.notNull():
        print(df_en.at[row,col])
'''
