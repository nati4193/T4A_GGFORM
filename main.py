# Import Library
import re
import pandas as pd
import numpy as np
import json
print("Pandas version", pd.__version__)

# Import station database
path = 'db\\m_station_db.csv'

def getstationdb(path):
    df_stn = pd.read_csv(
        path)
    df_stn = df_stn.rename(columns={"name_th": "stn_name_th"})
    df_stn.info()
    return df_stn

df1 = getstationdb(path)

# Import response data
form_url = 'https://docs.google.com/spreadsheets/d/1SN2lYQLvXx6H9FjYAtdPCpT_L0SJzcxfCGmgI7kv_ao/edit#gid=283051997'

# Function for read data form google sheet
def getresponse(url):
    e = 'export?format=xlsx&'
    excel_url = url.replace('edit', e)
    df = pd.read_excel(excel_url, encoding='unicode_escape')
    return df


df2 = getresponse(form_url)


# Transform response to standard pattern
def transform(df):  ### Transform dataframe to English format
    # add index column
    df['rec_id'] = df.index.astype(int)

    # Edit column header to code (Q01:xxxxxx >> Q01)
    for col in df.columns:
        if col.startswith('R'):
            df.rename({col: str(col[0:6])}, axis=1, inplace=True)
        if col.startswith('Unname'):  # drop unnamed column
            del df[str(col)]

    # Edit main column header
    df.rename({
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

    # Simplify R Response
    df['r_id'] = df['r_id'].str.slice_replace(3, repl='')
    print(df['r_id'])

    return df


df3 = transform(df2)
#df3 = df3.head(10)

# Get one response following index_num
def getdictresponse(df, index_num):  # Get one of accessibility item result
    i = index_num
    f = df.loc[i, 'r_id']  # Read r_id group
    ans = df.loc[i, df.columns.str.contains(f)]  # Get R-response following R-Group

    for x in range(len(ans)):
        if type(ans[x]) != float:  #Check value in cell is None or not
            if ans[x].count(':') >= 1 : #Find one or multiple choice answer
                a = ans[x]
                ans_list = a.split(", ")
                m_list = []
                for j in ans_list:
                    m_value = str(j)[0:2]
                    m_list.append(m_value)
                ans[x] = m_list
        else:
            ans[x] = None

    A_dict = ans.to_dict()

    ID = str(df.loc[i, 'rec_id'])
    ins = df.loc[i, 'agent_name']
    a_stn = df.loc[i, 'stn_name_th']
    acc_name = df.loc[i, 'acc_name']
    acc_loc = df.loc[i, 'acc_loc']
    acc_img = df.loc[i, 'acc_img']
    acc_timestamp = str(df.loc[i, 'timestamp'])  # change for json format
    acc_comment = df.loc[i, 'acc_comment']

    acc_item = {
        "ID": ID,
        "Attribute": {
            "Station_Name": a_stn,
            "Inspector": ins,
            "AccessibilityName": acc_name,
            "AccessibilityLocation": acc_loc,
            "Image": acc_img,
            "Timestamp": acc_timestamp,
            "Comment": acc_comment,
            "ANS": A_dict
        }
    }

    return acc_item

a = getdictresponse(df3, 9)

# Get batch responses following index_num range
def batchresponse(df, start, end):
    i = start
    j = end
    acc_item = {}

    for row in range(i, j):
        one_item = getdictresponse(df, row)
        # s = str(row)
        acc_item[one_item['ID']] = one_item
    return acc_item


#### TEST FUNCTION
a = getdictresponse(df3, 1)
a = batchresponse(df3, 0, 1509)

## EXPORT JSON
acc_json = json.dumps(a, indent=4, ensure_ascii=False)
print(acc_json)
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(a, f, ensure_ascii=False, indent=4)

# ===============================================================================================================

