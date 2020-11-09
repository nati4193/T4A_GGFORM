
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

##Import Question Database
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

## Import station database
path_station = 'db\\m_station_db.csv'

###FUNCTION :: Import station db
def get_station_db(path):
    df_stn = pd.read_csv(
        path)
    df_stn = df_stn.rename(columns={"name_th": "stn_name_th"})
    df_stn.info()
    return df_stn
#########################################################################
#Set up score table
score_db = pd.DataFrame(data=[100,100,100,55,60,70,0,20,30],
                        columns=['point'],
                        index=['4P','2P','1P','4M','2M','1M','4D','2D','1D'])

#######################################################################################

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
#df = df_standard
#index_num = 1126
def get_df_response(df,index_num):
    r_group = df.loc[index_num, 'r_id']                             # Get r_id group for selecting column
    all_ans = df.loc[index_num, df.columns.str.contains(r_group)]  # Get R-response following R-Group by selected column
    df_item = all_ans.to_frame()
    df_item['Q_ID'] = df_item.index
    df_item['a_trim'] = None
    df_item['a_final'] = None
    df_item.rename(columns={index_num:'full_res'},inplace = True)
    item_list = []
    item_list = df_item['full_res'].tolist()
    ans_list = []
    for item in item_list:
        if type(item) != float:                # Check value in cell is None?
            if str(item).count(':') >= 1:           # If not null -> Find one or multiple choice answer
                if str(item).count(':') > 1:
                    item_split = str(item).split(", ")
                    for i in range(len(item_split)):
                        item_split[i] = str(item_split[i])[0:2]
                    ans_list.append(item_split)
                else:
                    ans_list.append(item[0:2])
            else:
                ans_list.append('X1')
        else:
            ans_list.append('X0')

    df_item['a_trim'] = ans_list
    start_list = []
    start_list = df_item['a_trim'].tolist()
    final_list = []
    for id in range(len(start_list)):
        item = start_list[id]
        if type(item) == list:
            for i in item:
                if i[0] == 'P':
                    item = 'P'
                elif i[0] == 'M':
                    item = 'M'
                elif i[0] == 'D':
                    item = 'D'
                else:
                    item = 'X'
        else:
            item = item[0]
        final_list.append(item)
    df_item['a_final'] = final_list
    return df_item



'''

###FUNCTION :: Get one response following index_num with answer detail
df = df_standard
index_num = 1126
#def get_df_response(df,index_num):
    r_group = df.loc[index_num, 'r_id']                             # Get r_id group for selecting column
    all_ans = df.loc[index_num, df.columns.str.contains(r_group)]  # Get R-response following R-Group by selected column
    df_item = all_ans.to_frame()
    df_item['Q_ID'] = df_item.index
    df_item['a_trim'] = None
    df_item['a_final'] = None
    df_item.rename(columns={index_num:'full_res'},inplace = True)
    item_list = []
    item_list = df_item['full_res'].tolist()
    ans_list = []
    for item in item_list:
        #if type(item) != float:                # Check value in cell is None?
            if str(item).count(':') >= 1:           # If not null -> Find one or multiple choice answer
                if str(item).count(':') > 1:
                    item_split = str(item).split(", ")
                    ans_list.append(item_split)    #Separate Multiple choice to one value with comma
                else:
                    ans_list.append(str(item))
                    
                    
                trim_list = []                 #Set List for get trimmed answer
                for value in ans_list:         #Looping member in list for trimming
                    print(value)
                   if str(value)[0:1] == "P" or "M" or "D":
                       col = 2
                       trim_value = str(value)[0:3]              #Trimming answer
                       trim_list.append(trim_value)              #Join to previoues answer
                       df_item.iat[row,col] = trim_list          #Return trimmed answer back
                       col = 3
                       final_value = str(value)[0]               #LAST score [P,M,D,X] only
                       df_item.iat[row,col] = final_value        #Return trimmed answer back
                   else:
                       df_item.iat[row, col] = "X"
            else:
                pass
        else:
            df_item.iat[row,col] = "X"                        #Return NUll for blank answer
    print(df_item)
    return df_item'''

#########################################################################
#df = df_standard
#index_num = 100
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

    # TRANSFORM DATAFRAME TO ANSWER DICT
    ans_dict = {}
    ans_name = []
    question_id = []
    score = []
    ans_label = []
    ans_detail = []
    for row in range(len(df_ans)):
        ans_name.append((str(ID + "-" + str(df_ans.iat[row, 1]))))
        question_id.append(df_ans.iat[row, 1])
        score.append(df_ans.iat[row, 3])
        ans_label.append(df_ans.iat[row, 2])
        ans_detail.append(df_ans.iat[row, 0])

    for i in range(len(ans_name)):
        ans_info = {
            'question_id':question_id[i],
            'score':score[i],
            'ans_label':ans_label[i],
            'ans_detail':ans_detail[i]
        }
        ans_dict[ans_name[i]] = ans_info

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
ptai_dict_some = batch_response(df_standard,1,100)
#ptai_dict_all = batch_response(df_standard,1,1512)

### FUNCTION MERGE QUESTION DATABASE TO DICT
#Build function >> add variable
df = df_question_db
sc = score_db

def merge_score(ptai_dict,df):
    for id in ptai_dict:
        ans_list = list(ptai_dict[id]['attribute']['ans_dict'].keys())
        #Assign answer criteria to dict
        for ans_id in ans_list:
            q_id = ptai_dict[id]['attribute']['ans_dict'][ans_id]['question_id']
            a_score = ptai_dict[id]['attribute']['ans_dict'][ans_id]['score']

            add_is = df.at[q_id,'IS']
            add_X = df.at[q_id,"X"]
            add_L = df.at[q_id,"L"]
            add_U = df.at[q_id,"U"]
            #Calculate score section
            if a_score != 'X'and add_X > 0:
                a_pointcode = str(int(add_X)) + a_score
                a_point = sc.loc[a_pointcode,'point']
            else:
                a_pointcode = '0X'
                a_point = 0

            #Assign value to PTAI Dict
            ptai_dict[id]['attribute']['ans_dict'][ans_id]['IS'] = add_is
            ptai_dict[id]['attribute']['ans_dict'][ans_id]['X'] = add_X
            ptai_dict[id]['attribute']['ans_dict'][ans_id]['L'] = add_L
            ptai_dict[id]['attribute']['ans_dict'][ans_id]['U'] = add_U
            ptai_dict[id]['attribute']['ans_dict'][ans_id]['point'] = a_point

    return ptai_dict

#########################################################################
#TEST FUNCTION
merged_dict = merge_score(ptai_dict_some,df_question_db)
pp.pprint(merged_dict)
### FUNCTION GROUPING AS STATION
def get_station_set(ptai_dict):
    station_list = []
    for id in ptai_dict:
        station_list.append(ptai_dict[id]['attribute']['station_name'])
    stn_set = sorted(list(set(station_list)))
    return stn_set
#########################################################################
station_list = get_station_set(ptai_dict_some)
len(station_list)

###############################################################################################


##CALCULATION PART
#Add station name
dict = ptai_dict_some
df = df_question_db
i = 2
station = station_list[i]
r_group = "R03"
print(station)

#Get R Active group
r_active_list = []
for id in dict:
    r_active_list.append(dict[id]['attribute']['accessibility_group'])
r_active_list = sorted(set(r_active_list))

score_list = []
for id in dict:
    ans_list = list(dict[id]['attribute']['ans_dict'].keys())
    for ans_id in ans_list:
        score_list.append(dict[id]['attribute']['ans_dict'][ans_id]['score'])

score_set = set(score_list)

#############################################################################
    #GET SCORE FOR ONE RECORD
    #Input data

    dict = ptai_dict_some
    df = df_question_db
    id = '00100'

#Get score list form dict
def get_record_score(dict,id):
    rec_q = []
    rec_r = []
    rec_ans_list = list(dict[id]['attribute']['ans_dict'].keys())
    for ans_id in rec_ans_list:
        rec_q.append(dict[id]['attribute']['ans_dict'][ans_id]['question_id'])
        rec_r.append(dict[id]['attribute']['ans_dict'][ans_id]['score'])

    #Import X score list
    rec_x = []
    for item in rec_q:
        rec_x.append(df.at[item, "X"])

    #Create list to keep transform answer to score format
    rec_score = []
    for i in range(len(rec_r)):
        i = i - 1
        if rec_r[i] != None:
            if rec_x[i] == 4:
                rec_score.append('4'+rec_r[i])
            elif rec_x[i] == 2:
                rec_score.append('2'+rec_r[i])
            elif rec_x[i] == 1:
                rec_score.append('1'+rec_r[i])
        else:
            pass

    Rpoint_total = 0
    Rpoint_count = 1
    for item in rec_score:
        if item[-1] != 'X':
            print(item)
            Rpoint_total += score_db.loc[item,'point']
            Rpoint_count += 1

    Rpoint = round(Rpoint_total/Rpoint_count,2)

    print("Station Name :" + str(station))
    print("R GROUP :" + str(r_group))
    print("Record Answer:" +str(rec_score))
    print("Record ID :" +str(ans_id))
    print("Total score: " + str(Rpoint_total))
    print("Number of survey question: " + str(Rpoint_count))
    print("Average score :" + str(Rpoint))

    return Rpoint

dict = ptai_dict_some
id = '00200'

p = get_record_score(dict,id)

id_list = []
for id in dict:
    id_list.append(dict[id]['id'])

point_list = []
for id in id_list:
    point_list.append(get_record_score(dict,id))


#CALCULATE FOR ALL GROUP IN ONE STATION
stn_score_dict = {}
save = {}


##_EXPORT to JSON
def export2json(dict,filename):
    with open(f'output/{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(dict,f, ensure_ascii=False, indent=4)

export2json(ptai_dict_some,"dictsome3")

export2json(merged_dict,"dict_test")

