# Import Library
from googletrans import Translator
import re
import pandas as pd
import numpy as np

print("Pandas version", pd.__version__)

translator = Translator()

# Import database
df_stn = pd.read_csv(
    r'C:\Users\nngna\OneDrive\Documents\MAYDAY_NATI\T4A_GGFORM\db\m_station_db.csv')
df_stn = df_stn.rename(columns={"name_th": "stn_name_th"})
df_stn.info()
df_stn

# Import file
form_url = 'https://docs.google.com/spreadsheets/d/1qfNAL6iQ_gHhRkUn7QTZ88pjTUGHn2L_eLMQ_9yp_kQ/edit#gid=1736157131'
def gsheet2excel(x):
    e = 'export?format=xlsx&'
    excel_url =  x.replace('edit',e)
    print(excel_url)
    return excel_url
x = gsheet2excel(form_url)
df = pd.read_excel(x)
'''
#Translate column head
df_en = df.copy()
df_en
df_en.rename(columns=lambda x: translator.translate(x).text, inplace=True)
col_head = df_en.columns
print(col_head)
'''

df_en = df
# Edit column header to code
for col in df_en.columns:
    if col.startswith('Q'):
        df_en.rename({col: str(col[0:3])}, axis=1, inplace=True)
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
    "ความคิดเห็นเพิ่มเติมถึงสิ่งอำนวยความสะดวกนี้": "acc_comment"
}, axis=1, inplace=True)

print(df_en.columns)
df_en.info()
df_stn.info()



# Generate unique_response_id
# df_en['res_id'] = df_en['r_id'] + "-" +


# Simplify R Response
df_en['r_id'] = df_en['r_id'].str.slice_replace(3, repl='')
print(df_en['r_id'])
df_en

# Match Station ID
df_en = pd.merge(df_en,df_stn[['s_id','stn_id']], on=['stn_name_th'])