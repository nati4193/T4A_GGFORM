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

#IMPORT Library
import pandas as pd
import json

print("Pandas version", pd.__version__)


###FUNCTION :: Import Question Database
def get_ptai_question(path):
    df_question = pd.read_csv(
        path)
    return df_question


PATH_QUESTION = 'db\\T4A_PTAI_QA _Q.csv'
df_question_db = get_ptai_question(PATH_QUESTION)

###GET only question list form DB
df_questionlist = df_question_db.drop_duplicates(subset=['Code']).reset_index()
print(len(df_questionlist))


###FUNCTION :: Extract data from google sheet database
def get_response(url):
    EXCEL_FORMAT = 'export?format=xlsx&'
    excel_url = url.replace('edit', EXCEL_FORMAT)
    df = pd.read_excel(excel_url, encoding='unicode_escape')
    return df


# Import response data
form_url = "https://docs.google.com/spreadsheets/d/1SN2lYQLvXx6H9FjYAtdPCpT_L0SJzcxfCGmgI7kv_ao/edit#gid=283051997"
df_form = get_response(form_url)


###FUNCTION :: Import Question form Google Form for recheck
def get_formquestion(df):
    # Get Question's form column header begin with R
    ggform_question = []
    for col in df.columns:
        if col.startswith('R'):
            ggform_question.append(col)
        if col.startswith('Unname'):  # drop unnamed column
            del df[str(col)]

    cell = {'question': ggform_question}
    question_df = pd.DataFrame(cell)
    question_df.sort_values(by=['question'], inplace=True)
    split_table = question_df['question'].str.split(' : ', n=1, expand=True)
    question_df['q_code'] = split_table[0]
    question_df['q_name'] = split_table[1]
    question_df.sort_values(by=['q_code'], inplace=True)
    return question_df


##Get Question list
df_formquestion = get_formquestion(df_form)
df_formquestion.to_csv('output/formquestion.csv')

add_question = []
# CHECK form's question is in PTAI question DB
for row in df_formquestion['q_code']:
    if row in df_question_db.values:
        pass
    else:
        add_question.append(row)

# Import station database
path_station = 'db\\m_station_db.csv'


###FUNCTION :: Import station db
def get_station_db(path):
    df_stn = pd.read_csv(
        path)
    df_stn = df_stn.rename(columns={"name_th": "stn_name_th"})
    df_stn.info()
    return df_stn


df_stn_db = get_station_db(path_station)

# FUNCTION :: Transform google form's header response to standard pattern
def transform_header(df):  ###Transform_header dataframe to English format
    # add index column
    df['rec_id'] = df.index.astype(int).map('{:05d}'.format)

    # TRIM column header to question code (Q01:xxxxxx >> Q01)
    for col in df.columns:
        if col.startswith('R'):
            df.rename({col: str(col[0:6])}, axis=1, inplace=True)
        if col.startswith('Unname'):  # drop unnamed column
            del df[str(col)]

    # CHANGE main column header name
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


df_standard = transform_header(df_form)


# df = df3.head(10)

###FUNCTION :: Get one response following index_num
'''
def get_dict_response(df, index_num):  # Get one of accessibility item result
    row = index_num
    r_group = df.loc[row, 'r_id']  # Get r_id group for selecting column
    ans = df.loc[row, df.columns.str.contains(r_group)]  # Get R-response following R-Group by selected column

    for col_head in range(len(ans)):                    #Looping Each Column in R-column
        if type(ans[col_head]) != float:                # Check value in cell is None?
            if ans[col_head].count(':') >= 1:           # If not null -> Find one or multiple choice answer
                ans_list = ans[col_head].split(", ")    #Separate Multiple choice to one value with comma
                m_list = []                             #Set List for get trimmed answer
                for j in ans_list:                      #Looping member in list for trimming
                    m_value = str(j)[0:2]               #Trimming answer
                    m_list.append(m_value)              #Join to previoues answer
                ans[col_head] = m_list                  #Return trimmed answer back
        else:
            ans[col_head] = None                        #Return NUll for blank answer

    A_dict = ans.to_dict()                              #Create answer's dict to get value

    # ASSIGN EACH BASIC INFO COLUMN TO DICT VALUE
    ID = str(df.loc[row, 'rec_id'])
    ins = df.loc[row, 'agent_name']
    a_stn = df.loc[row, 'stn_name_th']
    acc_name = df.loc[row, 'acc_name']
    acc_loc = df.loc[row, 'acc_loc']
    acc_img = df.loc[row, 'acc_img']
    acc_timestamp = str(df.loc[row, 'timestamp'])  # change for json format
    acc_comment = df.loc[row, 'acc_comment']

    # MATCH VALUE TO KEY
    acc_item = {
        "id": ID,
        "attribute": {
            "station_name": a_stn,
            "inspector": ins,
            "accessibility_name": acc_name,
            "accessibility_location": acc_loc,
            "image": acc_img,
            "timestamp": acc_timestamp,
            "comment": acc_comment,
            "ans": A_dict
        }
    }

    return acc_item
'''
###FUNCTION :: Get one response following index_num with answer detail
def get_df_response(df,index_num):
    r_group = df.loc[index_num, 'r_id']                        # Get r_id group for selecting column
    all_ans = df.loc[index_num, df.columns.str.contains(r_group)]  # Get R-response following R-Group by selected column
    df_item = all_ans.to_frame()
    df_item['Q_ID'] = df_item.index
    df_item['a_trim'] = None
    df_item['a_final'] = None
    df_item.rename(columns={index_num:'full_res'},inplace = True)

    for row in range(len(df_item)):                                #Looping Each Column in R-column
        col = 0
        item = df_item.iloc[row, col]
        if type(item) != float:                # Check value in cell is None?
            if item.count(':') >= 1:           # If not null -> Find one or multiple choice answer
                ans_list = item.split(", ")    #Separate Multiple choice to one value with comma
                trim_list = []                 #Set List for get trimmed answer
                #final_list = []
                for value in ans_list:         #Looping member in list for trimming
                   col = 2
                   trim_value = str(value)[0:2]              #Trimming answer
                   trim_list.append(trim_value)              #Join to previoues answer
                   df_item.iat[row,col] = trim_list          #Return trimmed answer back
                   col = 3
                   final_value = str(value)[0]               #LAST score [P,M,D,X] only
                   df_item.iat[row,col] = final_value        #Return trimmed answer back
            else:
                pass
        else:
            df_item.iat[row,col] = "X"                        #Return NUll for blank answer
    return df_item

oneitem = get_df_response(df_standard,285)

#def create_ptai_dict(df,index_num):
#demo input
df = df_standard
row = 285

    # ASSIGN EACH BASIC INFO COLUMN TO DICT VALUE
    ID = str(df.loc[row, 'rec_id'])
    ins = df.loc[row, 'agent_name']
    a_stn = df.loc[row, 'stn_name_th']
    acc_name = df.loc[row, 'acc_name']
    acc_loc = df.loc[row, 'acc_loc']
    acc_img = df.loc[row, 'acc_img']
    acc_timestamp = str(df.loc[row, 'timestamp'])  # change for json format
    acc_comment = df.loc[row, 'acc_comment']
    df_ans = get_df_response(df,row)

    # MATCH VALUE TO KEY
    acc_item = {
        "id": ID,
        "attribute": {
            "station_name": a_stn,
            "inspector": ins,
            "accessibility_name": acc_name,
            "accessibility_location": acc_loc,
            "image": acc_img,
            "timestamp": acc_timestamp,
            "comment": acc_comment
            }
        }
    print(acc_item)

row = 1
df_ans.iat[row,1]

    #MATCH ANSWER DICT
    for row in range(len(df_ans)):
        ans_dict = {
            "ans_id": acc_item.get("id") + "-" + str(df_ans.iat[row,1]),
            "ans_attribute": {
                "question_id": str(df_ans.iat[row,1]),
                "score": df_ans.iat[row,3],
                "ans_label": df_ans.iat[row,2],
                "ans_detail": df_ans.iat[row,0]
            }
        }


###FUNCTION :: Get batch responses following index_num range
def batch_response(df, start, end):
    acc_item = {}

    for row in range(start, end):
        one_item = get_dict_response(df, row)
        # s = str(row)
        acc_item[one_item['id']] = one_item
    return acc_item


####TEST FUNCTION
test_get = get_dict_response(df_standard, 9)
df_dict_100 = batch_response(df_standard, 0, 100)

test_get_detail = get_dict_response_detail(df_standard, 9)


##_MERGE PTAI SCORE TO RECORD


##_EXPORT to JSON
def export2json(dict,filename):
    # acc_json = json.dumps(dict, indent=4, ensure_ascii=False)
    with open('output/data.json', 'w', encoding='utf-8') as f:
        json.dump(dict, f, ensure_ascii=False, indent=4)


export2json(df_dict_100)


# EXPORT QUESTION LIST


# ===============================================================================================================
