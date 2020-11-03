
###################################################################################################################
#IMPORT Library
import pandas as pd
import json
import pprint
print("Pandas version", pd.__version__)

###FUNCTION :: Import Question Database
def get_ptai_question(path):
    df_question = pd.read_csv(
        path)
    df_question = df_question.set_index('Code')
    return df_question

#Import Question Database
PATH_QUESTION = 'db\\T4A_PTAI_QA _Q.csv'
df_question_db = get_ptai_question(PATH_QUESTION)
#########################################################################
###FUNCTION :: Extract data from google sheet database
def get_response(url):
    EXCEL_FORMAT = 'export?format=xlsx&'
    excel_url = url.replace('edit', EXCEL_FORMAT)
    df = pd.read_excel(excel_url, encoding='unicode_escape')
    return df
#########################################################################
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
#########################################################################

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
#########################################################################

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
#########################################################################
#Transform dataframe
df_standard = transform_header(df_form)

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
#########################################################################
def create_ptai_dict(df,index_num):
    row = index_num

    # ASSIGN EACH BASIC INFO COLUMN TO DICT VALUE
    ID = str(df.loc[row, 'rec_id'])
    ins = df.loc[row, 'agent_name']
    a_stn = df.loc[row, 'stn_name_th']
    acc_name = df.loc[row, 'acc_name']
    acc_rid = df.loc[row,'r_id']
    acc_loc = df.loc[row, 'acc_loc']
    acc_img = df.loc[row, 'acc_img']
    acc_timestamp = str(df.loc[row, 'timestamp'])  # change for json format
    acc_comment = df.loc[row, 'acc_comment']
    df_ans = get_df_response(df,row)

    # MATCH ANSWER DICT
    for row in range(len(df_ans)):
        ans_dict = {
            "ans_id": ID + "-" + str(df_ans.iat[row, 1]),
            "question_id": str(df_ans.iat[row, 1]),
            "score": df_ans.iat[row, 3],
            "ans_label": df_ans.iat[row, 2],
            "ans_detail": df_ans.iat[row, 0]
            }

    # MATCH VALUE TO KEY
    acc_item = {
        "id": ID,
        "attribute": {
            "station_name": a_stn,
            "inspector": ins,
            "accessibility_name": acc_name,
            "accessibility_group":acc_rid,
            "accessibility_location": acc_loc,
            "image": acc_img,
            "timestamp": acc_timestamp,
            "comment": acc_comment,
            "ans_dict":ans_dict
            }
        }

    return acc_item
#########################################################################

one = create_ptai_dict(df_standard,285)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(one)

###FUNCTION :: Get batch responses following index_num range
def batch_response(df, start, end):
    acc_item = {}

    for row in range(start, end):
        one_item = create_ptai_dict(df, row)
        # s = str(row)
        acc_item[one_item['id']] = one_item
    return acc_item
#########################################################################
dict_some = batch_response(df_standard,1,1000)
pp.pprint(dict_some)

### FUNCTION MERGE QUESTION DATABASE TO DICT
def merge_score(ptai_dict,db_question):
    df = db_question
    for id in ptai_dict:
        q_id = ptai_dict[id]['attribute']['ans_dict']['question_id']
        add_is = df.at[q_id,'IS']
        add_X = df.at[q_id,"X"]
        add_L = df.at[q_id,"L"]
        add_U = df.at[q_id,"U"]
        #Assign value to PTAI Dict
        ptai_dict[id]['attribute']['ans_dict']['IS'] = add_is
        ptai_dict[id]['attribute']['ans_dict']['X'] = add_X
        ptai_dict[id]['attribute']['ans_dict']['L'] = add_L
        ptai_dict[id]['attribute']['ans_dict']['U'] = add_U
    return ptai_dict
#########################################################################
#TEST FUNCTION
merged_dict = merge_score(dict_some,df_question_db)

### FUNCTION GROUPING AS STATION
def get_station_set(merged_dict):
    station_list = []
    for id in merged_dict:
        station_list.append(merged_dict[id]['attribute']['station_name'])
    stn_set = sorted(list(set(station_list))               )
    return stn_set
#########################################################################
station_list = get_station_set(merged_dict)
len(station_list)
###############################################################################################
#Set up score table
score_db = pd.DataFrame(data=[100,100,100,55,60,70,0,20,30],
                        columns=['point'],
                        index=['4P','2P','1P','4M','2M','1M','4D','2D','1D'])


##CALCULATION PART
#Add station name
i = 5
stn_demo = station[i]
print(stn_demo)
r_group = R_active_list[0]
df = df_question_db

'''
#Set up variable following Q_ID
IS = df.at[q_id,'IS']
X = df.at[q_id,"X"]
L = df.at[q_id,"L"]
U = df.at[q_id,"U"]
R_all_oneStation =  dict_some.items()
'''

#GET SCORE LIST FORM ONE R_ID
questionlist_station = []
resultlist_station = []
for id in dict_some:
    if stn_demo in dict_some[id]['attribute']['station_name']:
        if r_group in dict_some[id]['attribute']['accessibility_group']:
            questionlist_station.append(dict_some[id]['attribute']['ans_dict']['question_id'])
            resultlist_station.append(dict_some[id]['attribute']['ans_dict']['score'])
    else:
        pass

xlist_stn = []
for item in questionlist_station:
    xlist_stn.append(df.at[item, "X"])

stn_r_score = []

#Get
for i in range(len(resultlist_station)):
    if resultlist_station[i] != None:
        print(questionlist_station[i]," : ",resultlist_station[i])
        if xlist_stn[i] == 4:
            stn_r_score.append('4'+resultlist_station[i])
        elif xlist_stn[i] == 2:
            stn_r_score.append('2'+resultlist_station[i])
        elif xlist_stn[i] == 1:
            stn_r_score.append('1'+resultlist_station[i])
    else:
        pass

Rpoint_total = 0
Rpoint_count = len(stn_r_score)

for item in stn_r_score:
    Rpoint_total += score_db.loc[item,'point']
print(Rpoint_total)

Rpoint = Rpoint_total/Rpoint_count
print(Rpoint)



score_dict= {
    'station_name':X1,
    'score':{
        'R01_point':
    }
}



##_EXPORT to JSON
def export2json(dict,filename):
    with open(f'output/{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(dict, f, ensure_ascii=False, indent=4)

export2json(dict_some,"dictsome")


# EXPORT QUESTION LIST
