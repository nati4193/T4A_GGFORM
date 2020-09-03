#Import Library
import re
import pandas as pd
import numpy as np
import json
print("Pandas version", pd.__version__)

# Import station database
def getstationdb():
    df_stn = pd.read_csv(
        r'C:\Users\nngna\OneDrive\Documents\MAYDAY_NATI\T4A_GGFORM\db\m_station_db.csv')
    df_stn = df_stn.rename(columns={"name_th": "stn_name_th"})
    df_stn.info()
    return df_stn

df1 = getstationdb()

# Import response data
form_url = 'https://docs.google.com/spreadsheets/d/1SN2lYQLvXx6H9FjYAtdPCpT_L0SJzcxfCGmgI7kv_ao/edit#gid=283051997'

def getresponse(url):
    e = 'export?format=xlsx&'
    excel_url =  url.replace('edit',e)
    df = pd.read_excel(excel_url,encoding= 'unicode_escape')
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
        if col.startswith('Unname'):  #drop unnamed column
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
df3 = df3.head(10)

#Get one response following index_num
def getdictresponse(df,index_num): #Get one of accessibility item result
    i = index_num
    f = df.loc[i,'r_id'] #Read r_id group
    ans = df.loc[i,df.columns.str.contains(f)] #Get R-response following R-Group

    for x in range(len(ans)):
        if type(ans[x]) != float:
            ans[x] = ans[x][0:2]
        else: ans[x] = None

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

    return acc_item #

#Get batch responses following index_num range
def batchresponse(df,start,end):
    i = start
    j = end
    acc_item = {}

    for row in range(i,j):
        one_item = getdictresponse(df,row)
        s = str(row)
        acc_item[s] = one_item

    return acc_item

a = getdictresponse(df3,1)
a = batchresponse(df3,0,9)

acc_json = json.dumps(a,indent=4,ensure_ascii=False) ### Missing Null value format

print(acc_json)



#===============================================================================================================








'''


dfA = df3[['rec_id','timestamp', 'stn_name_th', 'agent_name', 'r_id', 'acc_name', 'acc_loc','acc_img','acc_comment']]

for row in range(len(df3)):
    x = df3.loc[row, 'r_id']
    for col in df3.columns:
        dfB = df3.loc[:,df3.columns.str.contains(x)]

def getrecord(df):
    S = df.loc[1]



    print(S)
    return S

getrecord(df3)




def getstation(df):
    dfA = df[['rec_id','timestamp', 'stn_name_th', 'agent_name', 'r_id', 'acc_name', 'acc_loc','acc_img','acc_comment']]
    stn = {
    stn = dfA['stn_name_th'].unique()
    for i in stn:
        for row in range(len(dfA)):
    print(stn)
    return stn


dfB = df.loc[:,df.columns.str.contains('rec_id')|df.columns.str.contains('R') | df.columns.str.contains('r_id')]

def stationdict(self,name_th,name_en,x,y):
    self.name_th = name_th,
    self.name_en = name_en,
    self.geometry = [x,y],
    self.response = [record],



stn1 = getstation(df3)



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

df4 = combine_response(df3)
'''

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
