###################################################################################################################
#IMPORT Library
import pandas as pd
import json
import numpy as np
import difflib

print("Pandas version", pd.__version__)

def convert(o):
    if isinstance(o, np.int64): return int(o)
    raise TypeError


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
###################################################################################################################
# Import response data
form_url = "https://docs.google.com/spreadsheets/d/1SN2lYQLvXx6H9FjYAtdPCpT_L0SJzcxfCGmgI7kv_ao/edit#gid=283051997"
df_form = get_response(form_url)
len(df_form)

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
###################################################################################################################
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

##Import station database
path_station = 'db\\m_station_db.csv'

###FUNCTION :: Import station db
def get_station_db(path):
    df_stn = pd.read_csv(
        path)
    df_stn = df_stn.rename(columns={"name_th": "stn_name_th"})
    df_stn.info()
    return df_stn
###################################################################################################################
#Set up score table
def score_setting():
    score_db = pd.DataFrame(data=[100, 100, 100, 55,60,70,0,20,30],
                            columns=['point'],
                            index=['4P','2P','1P','4M','2M','1M','4D','2D','1D'])
    return score_db

score_db = score_setting()

# FUNCTION :: Get R-ID set form response dataFrame
def get_rgform_set(df=df_form):
    rg_set = sorted(set(list(df['r_id'])))
    return rg_set

# FUNCTION :: Get U-type set form response dataFrame ('NW','AA','TA',...)
def get_utype_set(df=df_question_db):
    utype_set = sorted(set(list(df['U'])))
    return utype_set
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
###################################################################################################################
#Transform dataframe
df_transformed = transform_header(df_form)

print('Complete Preparing Section!')
'''
###################################################################################################################
#Upload image to cloud storage
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os

credentials_dict = {
    'type': 'service_account',
    'client_id': os.environ['BACKUP_CLIENT_ID'],
    'client_email': os.environ['BACKUP_CLIENT_EMAIL'],
    'private_key_id': os.environ['BACKUP_PRIVATE_KEY_ID'],
    'private_key': os.environ['BACKUP_PRIVATE_KEY'],
}
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credentials_dict
)
client = storage.Client(credentials=credentials, project='myproject')
bucket = client.get_bucket('mybucket')
blob = bucket.blob('myfile')
blob.upload_from_filename('myfile')

###################################################################################################################
#Download image to cloud storage

from google.cloud import storage


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )
'''

###FUNCTION :: Get one response as DataFrame following index_num with answer detail
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

###################################################################################################################
# FUNCTION :: Create one response as dictionary format
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
    ans_dict = {}       #For store all answers of one response
    ans_name = []       #For assign each answer in format : RxxQxx-XXXXX
    question_id = []    #For store question id as RxxQxx
    score = []          #For store score as 'P','M','D','X'
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


###################################################################################################################

###FUNCTION :: Get batch responses following index_num range
def batch_response(df, start, end):
    acc_item = {}

    for row in range(start, end):
        one_item = create_ptai_dict(df, row)
        # s = str(row)
        acc_item[one_item['id']] = one_item
    return acc_item

###################################################################################################################

ptai_dict_some = batch_response(df_transformed, 1, len(df_form))
#ptai_dict_all = batch_response(df_standard,1,1512)

### FUNCTION MERGE QUESTION and SCORE DATABASE TO DICT

def merge_score(ptai_dict,df=df_question_db,sc=score_db):
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
            ptai_dict[id]['attribute']['ans_dict'][ans_id]['point'] = int(a_point)

    return ptai_dict

#########################################################################
#TEST FUNCTION
merged_dict = merge_score(ptai_dict_some,df_question_db)

##_EXPORT Database to JSON
def export2json(dict,filename):
    with open(f'output/{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(dict,f, ensure_ascii=False, indent=4,default=convert)

#export2json(ptai_dict_some,"dictsome3")
export2json(merged_dict,"PTAI_DB")

######################################################################################################\

#IMPORT PTAI_DB.json
with open('output/PTAI_DB.json') as json_file:
    merged_dict = json.load(json_file)

    # Print the type of data variable
    print("Imported PTAI_DB.json as Type:", type(merged_dict))

print('Complete Import Section!')


#########################################################################
### FUNCTION GROUPING AS STATION
def get_stationform_set(ptai_dict):
    station_list = []
    for id in ptai_dict:
        station_list.append(ptai_dict[id]['attribute']['station_name'])
    stn_set = sorted(list(set(station_list)))
    return stn_set

station_list = get_stationform_set(merged_dict)
len(station_list)

#FUNCTION DICT DB TO CSV DATAFRAME

###############################################################################################
'''
Query data form dict
- Snippet for get data
    for id in ptai_dict:
        ans_list = list(ptai_dict[id]['attribute']['ans_dict'].keys())
        #Assign answer criteria to dict
        for ans_id in ans_list:
            itemX = ptai_dict[id]['attribute']['ans_dict'][ans_id]['X']
- Request variable
    station name : ptai_dict[id]['attribute']['station_name']
    R group      : ptai_dict[id]['attribute']['accessibility_group']
    L            : ptai_dict[id]['attribute']['ans_dict'][ans_id]['L']
    U type       : ptai_dict[id]['attribute']['ans_dict'][ans_id]['U']
    point        : ptai_dict[id]['attribute']['ans_dict'][ans_id]['point']
'''
#FUNCTION FOR SEARCHING KEY IN DICT
def recursive_lookup(k, d):
    if k in d: return d[k]
    for v in d.values():
        if isinstance(v, dict):
            a = recursive_lookup(k, v)
            if a is not None: return a
    return None

#FUNCTION >>> check station location
def check_stationlist():
    stn_db_list = df_stn_db['stn_name_th'].tolist()
    for station in station_list:
        stn_similar = difflib.get_close_matches(station,stn_db_list)
        #print('Find station : {} = Station : {}'.format(station,stn_similar))
        #print(stn_similar[0])
        if station != stn_similar[0]:
            print('Station missing form station database : {}'.format(station))
        else:
            pass
    print("All station matched completed")

#TEST >>
check_stationlist()

#FUNCTION >> Get Ri Point for each R-Group in a Station (Average score for one response) >>> get_ai_station
def get_item_point(rec_id,lv,option):
    a1 = recursive_lookup(rec_id, merged_dict)
    a2 = recursive_lookup('ans_dict', a1)
    a_list = list(a2.keys())  # Get all answer in one response
    point_list = []
    count_list = []
    countIS = []
    countX = []
    for item in a_list:  # Looping item in answer-id list (ans_dict)
        a3 = recursive_lookup(item, a2)
        s = recursive_lookup('score', a3)
        p = recursive_lookup('point', a3)
        IS = recursive_lookup('IS', a3)
        X = recursive_lookup('X', a3)
        l = recursive_lookup('L', a3)
        if s != 'X' and "U" != 'SK':
            if l <= lv:
                point_list.append(p)
                count_list.append(s)
                countIS.append(IS)
                countX.append(X)
            else:
                pass

        # print('{},{},{}'.format(item,point_list,count_list))
    if len(point_list) > 0:
        point_rec_avg = np.mean(point_list)
    else:
        point_rec_avg = 0

    point_rec_total = np.sum(point_list)
    point_count = len(count_list)

    if str(option) == 'point':
        return point_rec_avg
    elif str(option) == 'dataframe':
        qcount = len(point_list)
        pcount = sum(map(lambda x : x == 'P', count_list))
        mcount = sum(map(lambda x : x == 'M', count_list))
        dcount = sum(map(lambda x : x == 'D', count_list))
        IS3_count = sum(map(lambda x : x == 3,countIS))
        IS2_count = sum(map(lambda x : x == 2,countIS))
        IS1_count = sum(map(lambda x : x == 1,countIS))
        X4_count = sum(map(lambda x : x == 4,countX))
        X2_count = sum(map(lambda x : x == 2,countX))
        X1_count = sum(map(lambda x : x == 1,countX))

        d = [(rec_id,point_rec_total,point_rec_avg,lv,
              qcount,pcount,mcount,dcount,
              IS1_count,IS2_count,IS3_count,
              X1_count,X2_count,X4_count)]
        df_rec = pd.DataFrame(d,columns=['REC_ID','Total point','AVG POINT','Lv.',
                                         'Q count','P count','M Count','D Count',
                                         'IS1','IS2','IS3','X4','X2','X1'])

        return df_rec
    else:
        return print("Input option for get data")

rec_id = '00534'
lv = 1
t7 = get_item_point(rec_id,lv,'dataframe')


#FUNCTION >> GET AI Point for Station (Average score for many responses in one group)
# #Refer : get_item_point(rec_id,lv,option) , merged_dict
station = station_list[0]
lv = 1
rgroup = 'R03'

def get_ai_station(station, rgroup, lv, option):
    rg = rgroup
    ai_id_list = [] # collect all rec_id in Rx
    ai_point_list = []  # store score from each answer as list
    #Loop each item in dict
    for id in merged_dict:
       si = merged_dict[id]['attribute']['station_name']
       ri = merged_dict[id]['attribute']['accessibility_group']
       if si == station and ri == rg:
           ai_id_list.append(id) #Get rec_id list by selecting station name and R Group
       else:
           pass

    df_ai = pd.DataFrame(columns=['REC_ID','Total point','AVG POINT','Lv.',
                                  'Q count','P count','M Count','D Count',
                                  'IS1','IS2','IS3','X4','X2','X1'])
    for id in ai_id_list:
        d = get_item_point(id,lv,'point')
        df_oneitem = get_item_point(id,lv,'dataframe')
        row = df_oneitem.values.flatten().tolist()

        df_ai.loc[len(df_ai.index)] = row
        ai_point_list.append(d)

    if len(ai_point_list) > 0:
        ai_avg = round(np.mean(ai_point_list),2)
    else:
        ai_avg = None

    ai_ans_count = df_ai['Q count'].sum()
    ai_ans_countP =  df_ai['P count'].sum()
    ai_ans_countM =  df_ai['M Count'].sum()
    ai_ans_countD =  df_ai['D Count'].sum()
    ai_ans_countIS1 =  df_ai['IS1'].sum()
    ai_ans_countIS2 =  df_ai['IS2'].sum()
    ai_ans_countIS3 =  df_ai['IS3'].sum()
    ai_ans_countX1 =  df_ai['X1'].sum()
    ai_ans_countX2 =  df_ai['X2'].sum()
    ai_ans_countX4 =  df_ai['X4'].sum()

    ai_item_count = len(ai_point_list)
    ai_total = np.sum(ai_point_list)
    ai_info_list = [station,rgroup,ai_avg,ai_item_count,
                    ai_ans_count,ai_ans_countP,ai_ans_countM,ai_ans_countD,
                    ai_ans_countIS1,ai_ans_countIS2,ai_ans_countIS3,
                    ai_ans_countX1,ai_ans_countX2,ai_ans_countX4
                    ]
    if option == 'point':
        return ai_avg
    elif option == 'list':
        return ai_info_list
    elif option == 'dataframe':
        return  df_ai

#TEST def get_ai_station(station, rgroup, lv, option):
station = station_list[0]
lv = 1
rgroup = 'R03'
t8 = get_ai_station(station,rgroup,lv,'list')
t9 = get_ai_station(station,rgroup,lv,'dataframe')

### FUNCTION >> Find IU_point for station each R_Group
def get_iu_point(station,rg,utype,lv):

    a_rq_list = [] # collect all rec_id in Rx
    a_rq_score = []

    for id in merged_dict:
       si = merged_dict[id]['attribute']['station_name']
       ri = merged_dict[id]['attribute']['accessibility_group']
       if si == station and ri == rg:
           a_rq_list.append(id)
       else:
           pass

    for id in a_rq_list:
        ans_list = list(merged_dict[id]['attribute']['ans_dict'].keys())
        for ans_id in ans_list:
            u_score = merged_dict[id]['attribute']['ans_dict'][ans_id]['score']
            u_point = merged_dict[id]['attribute']['ans_dict'][ans_id]['point']
            u_id = merged_dict[id]['attribute']['ans_dict'][ans_id]['U']
            l = merged_dict[id]['attribute']['ans_dict'][ans_id]['L']

            if u_id == utype and u_score != 'X' and l <= lv:
                a_rq_score.append(u_point)
            else:
                pass

    if len(a_rq_score) == 0:
        #print("There is no this type of access need")
        iu_point = None
    else:
        iu_point = round(np.average(a_rq_score),2)
        #print("iu_point : " + str(iu_point))

    return iu_point

### FUNCTION >> Find IU_point for a Station group by User Access Need
def get_up_point(station,utype,lv):
    a_rq_list = []
    a_rq_score = []
    u_list = []
    u_score = []

    for id in merged_dict:
       si = merged_dict[id]['attribute']['station_name']
       if si == station:
           a_rq_list.append(id)
       else:
           pass

    for id in a_rq_list:
        ans_list = list(merged_dict[id]['attribute']['ans_dict'].keys())
        for ans_id in ans_list:
            u_score = merged_dict[id]['attribute']['ans_dict'][ans_id]['score']
            u_point = merged_dict[id]['attribute']['ans_dict'][ans_id]['point']
            u_id = merged_dict[id]['attribute']['ans_dict'][ans_id]['U']
            l = merged_dict[id]['attribute']['ans_dict'][ans_id]['L']

            if u_id == utype and u_score != 'X' and l <= lv:
                a_rq_score.append(u_point)
                #print(ans_id,u_score,u_point,u_id,l)
            else:
                pass

    if len(a_rq_score) == 0:
        #print("There is no this type of access need")
        up_point = 0
    else:
        up_point = round(np.average(a_rq_score),2)
        #print("iu_point : " + str(up_point))

    return up_point

### FUNCTION >> Find I-point for station each R_Group
def get_irx_point(station,rg,lv):
    u_list = []
    i_list = []

    for id in merged_dict:
        si = merged_dict[id]['attribute']['station_name']
        ri = merged_dict[id]['attribute']['accessibility_group']
        if si == station and ri == rg:
            i_list.append(id)
        else:
            pass

        for id in i_list:
            ans_list = list(merged_dict[id]['attribute']['ans_dict'].keys())
            for ans_id in ans_list:
                ui = merged_dict[id]['attribute']['ans_dict'][ans_id]['U']
                u_list.append(ui)
    u_set = set(u_list)
    i_point_list = []

    for u in u_set:
        iu = get_iu_point(station,rg,u,lv)
        if iu != None:
            i_point_list.append(iu)
        else: pass
    if len(i_point_list) > 0:
        i_rx_point = round(np.average(i_point_list),2) #Get i point for each R access need
        i_rx_total = np.sum(i_point_list)
    else:
        i_rx_point = 0
    count = len(i_point_list)
    print(station,i_rx_point,i_rx_total,count)

    return i_rx_point

### FUNCTION >> GET Overall point (OAP) for each R-Group in a station
def get_oap(station,rg,lv,option):
    oa = get_ai_station(station, rg, lv, 'point')
    oi = get_irx_point(station,rg,lv)
    overall = (oa + oi)/2
    print(station,rg,lv,overall)
    overall_list = [station,rg,lv,oa,oi,overall]
    if option == 'point':
        return overall
    elif option == 'list':
        return overall_list

### FUNCTION >> CREATE Accessible Facilities (AF) DataFrame for a station
def get_af_table(station,lv,option):
    rg_set = get_rgform_set(df_transformed)
    af_df = pd.DataFrame(columns=['station','rg','af_point',
                                  'Q_Count','A Count','P count','M count','D count',
                                  'IS1','IS2','IS3','X1','X2','X4'])
    for rg in rg_set:
        af_list = []
        af = get_ai_station(station,rg, lv,'list')
        af_df.loc[len(af_df)] = af

    oap_list = af_df['af_point'].dropna().astype(int).tolist()

    oap = -1
    oap_msx = -1

    if len(oap_list) > 1:
        oap = np.mean(oap_list)
        if (oap-50)/10 > 0 :
            oapx = (oap-50)/10
        else:
            oapx = 0
        oap_med = np.median(oap_list)
        oap_std = np.std(oap_list)
        if ((oap_med - oap_std) - 50)/10 > 0:
            oap_msx = ((oap_med - oap_std) - 50)/10
        else:
            oap_msx = 0

    else:
        oap = 0
        oapx = 0
        oap_med = 0
        oap_std = 0
        oap_msx = 0

    ai_score =round(((oapx + oap_msx)*0.5),2)

    if ai_score < 0:
        ai_score = 0
    else:
        ai_score = ai_score

    if option == 'dataframe':
        return af_df
    elif option == 'point':
        return oap
    elif option == 'AI':
        return ai_score
#TEST

### FUNCTION >> CREATE Accessible User need (AU) DataFrame for a station
def get_up_table(station,lv,option):
    utype_set = get_utype_set()
    an_df = pd.DataFrame(columns=['station','U type','an_point'])
    for u in utype_set:
        an_list = []
        an = get_up_point(station,u,lv)
        an_list = [station,u,an]
        an_df.loc[len(an_df)] = an_list

    oupx = -1
    oup_msx = -1
    oup_list = an_df['an_point'].dropna().astype(int).tolist()
    oup = np.mean(oup_list)
    if (oup-50)/10 > 0:
        oupx = (oup-50)/10
    else:
        oupx = 0

    oup_med = np.median(oup_list)
    oup_std = np.std(oup_list)
    if ((oup_med - oup_std) - 50)/10 > 0:
        oup_msx = ((oup_med - oup_std) - 50)/10
    else:
        oup_msx = 0

    ii_score = round((oupx + oup_msx) * 0.5,2)
    if ii_score < 0:
        ii_score = 0
    else:
        ii_score = ii_score

    if option == 'dataframe':
        return an_df
    elif option == 'point':
        return  oup
    elif option == 'II':
        return ii_score

#FUNCTION GET ALL STATION SCORE TABLE
def get_scoresummary_allstation(lv,option):

    df_oap_all = pd.DataFrame()
    df_oup_all = pd.DataFrame()

    for stn in station_list:
        df_oap = get_af_table(stn,lv,'dataframe')
        df_oup = get_up_table(stn,lv,'dataframe')

        df_oap_all = df_oap_all.append(df_oap,ignore_index=True)
        df_oup_all = df_oup_all.append(df_oup,ignore_index=True)
    if option == 'oap':
        return df_oap_all
    elif option == 'oup':
        return df_oup_all
    else:
        print("Please check input argument")
#TEST
t4 = get_scoresummary_allstation(1,'oap')

def get_overall_station(station,lv,option):
    oap = get_af_table(station,lv,'point')
    oup = get_up_table(station,lv,'point')
    op = (oap + oup)/2

    if option == 'oap':
       # print('Result : {},{},OAP Output = {}'.format(station,lv,oap))
        return oap
    elif option == 'oup':
        #print('Result : {},{},OUP Output = {}'.format(station,lv,oup))
        return oup
    elif option == 'op':
        #print('Result : {},{},OVERALL Output = {}'.format(station,lv,op))
        return op
    else:
        print('Check argument')

###FUNCTION >> Calculate IFI (Improvement Feasibility Index) for a station
def get_ifi(station,lv):

    id_list = []
    is_list = []
    u_list = []
    u_score = []

    for id in merged_dict:
        si = merged_dict[id]['attribute']['station_name']
        if si == station:
            id_list.append(id)
        else:
            pass

    for id in id_list:
        ans_list = list(merged_dict[id]['attribute']['ans_dict'].keys())
        for ans_id in ans_list:
            is_value = merged_dict[id]['attribute']['ans_dict'][ans_id]['IS']
            l = merged_dict[id]['attribute']['ans_dict'][ans_id]['L']
            if l <= lv:
                is_list.append(is_value)
            else:
                pass
        is_total = len(is_list)
        is_low = is_list.count(1.0)
        is_med = is_list.count(2.0)
        is_high = is_list.count(3.0)

    IS_point = (((0.9*is_low*100)/is_total) + ((0.5*is_med*100)/is_total) + ((0.1*is_high*100)/is_total))
    IFI = np.round((IS_point/100)*5,2)

    #print('IFI Index for station : {} = {}'.format(station,IFI))

    return IFI

### Calculate PTAI score
def get_ptai_all():
    df_ptai = pd.DataFrame(columns=[
        'Station Name',
        'Station Type',
        'Province',
        'Lat',
        'Lon',
        'Coordinate',
        'PTAI',
        'AI',
        'II',
        'IFI',
        'OVERALL',
        'OA',
        'OI',
        'Level',
        'All item checked',
        'Facilites checked',
        'Area checked',
        'P items',
        'M items',
        'D items',
        'IS1 items',
        'IS2 items',
        'IS3 items',
        'X1 items',
        'X2 items',
        'X4 items',

    ])
    #Looping all level
    for lv in range (1,4,1):
        #Looping all station
        for station in station_list:
            ai = get_af_table(station,lv,'AI')
            ii = get_up_table(station,lv,'II')
            ifi = get_ifi(station,lv)
            ptai = round((ai + ii)*0.5,1)

            oa = get_overall_station(station,lv,'oap')
            oi = get_overall_station(station,lv,'oup')
            overall = round(get_overall_station(station,lv,'op'),2)

            s = df_stn_db[[station in x for x in df_stn_db['stn_name_th']]]
            s_lat = str(s.iloc[0,16])
            s_lon = str(s.iloc[0,17])
            s_coordinate = ('{},{}'.format(s_lat,s_lon))
            province = str(s.iloc[0,8])
            station_type = str(s.iloc[0,6])
            level = lv

            df_stat = get_af_table(station,lv,'dataframe')
            count_item_checked = df_stat['A Count'].sum()
            count_facilities_checked = np.sum(df_stat['Q_Count']>0)
            count_area_checked = df_stat['Q_Count'].sum()
            count_item_P = df_stat['P count'].sum()
            count_item_M = df_stat['M count'].sum()
            count_item_D = df_stat['D count'].sum()
            count_item_is1  = df_stat['IS1'].sum()
            count_item_is2  = df_stat['IS2'].sum()
            count_item_is3  = df_stat['IS3'].sum()
            count_item_x4  = df_stat['X4'].sum()
            count_item_x2  = df_stat['X2'].sum()
            count_item_x1  = df_stat['X1'].sum()

            h1 = [
                station,
                station_type,
                province,
                s_lat,
                s_lon,
                s_coordinate,
                ptai,
                ai,
                ii,
                ifi,
                overall,
                oa,
                oi,
                level,
                count_item_checked,
                count_facilities_checked,
                count_area_checked,
                count_item_P,
                count_item_M,
                count_item_D,
                count_item_is1,
                count_item_is2,
                count_item_is3,
                count_item_x4,
                count_item_x2,
                count_item_x1            ]

            df_ptai.loc[len(df_ptai.index)] = h1
    return df_ptai

###
def get_ptai_report():
    rg_set = get_rgform_set(df_transformed)
    utype_set = get_utype_set()
    h1 = ['station', 'level']
    h2 = rg_set
    h3 = utype_set
    head = h1 + h2 + h3
    df_report = pd.DataFrame(columns=head)
    #Looping all level
    for lv in range (1,4,1):
        #Looping all station
        for station in station_list:
            s = station
            level = lv
            af = []
            ua = []
            for rg in rg_set:
                af.append(get_ai_station(station, rg, lv, 'point'))
            for u in utype_set:
                ua.append(get_up_point(station,u,lv))
            row = [s,level] + af + ua
            df_report.loc[len(df_report.index)] = row
    return df_report

def get_station_summary(option):
    df_oap = pd.DataFrame(columns=['station','rg','af_point',
                                  'Q_Count','A Count','P count','M count','D count',
                                  'IS1','IS2','IS3','X1','X2','X4','lv'])
    df_oup = pd.DataFrame(columns=['station','U type','an_point'])

    for lv in range(1,4,1):
        df_name_ap = 'df_ap_lv{}'.format(lv)
        df_name_ap = pd.DataFrame()
        df_name_ap = get_scoresummary_allstation(lv,'oap')
        df_name_ap['lv'] = lv
        df_oap = df_oap.append(df_name_ap,ignore_index = True)

        df_name_up = 'df_up_lv{}'.format(lv)
        df_name_up = pd.DataFrame()
        df_name_up = get_scoresummary_allstation(lv, 'oup')
        df_name_up['lv'] = lv
        df_oup = df_oup.append(df_name_up, ignore_index=True)


    if option == 'OAI':
        return  df_oap
    elif option == 'OUP':
        return df_oup


def get_record_db():
    df_record = pd.DataFrame(columns=['Station Name',
                                      'Record ID',
                                      'InspectorName',
                                      'Accessiblity Name',
                                      'R Group',
                                      'Accessibility Position',
                                      'Image',
                                      'Timestamp',
                                      'Question Record ID'
                                      ])
    question_rec_id = []
    for id in merged_dict:
        station_name = merged_dict[id]['attribute']['station_name']
        rec_id = id
        inspector = merged_dict[id]['attribute']['inspector']
        acc_name = merged_dict[id]['attribute']['accessibility_name']
        acc_group = merged_dict[id]['attribute']['accessibility_group']
        acc_location = merged_dict[id]['attribute']['accessibility_location']
        acc_img = merged_dict[id]['attribute']['image']
        acc_time = merged_dict[id]['attribute']['timestamp']
        question_rec_id = list(merged_dict[id]['attribute']['ans_dict'].keys())

        row = [station_name,rec_id,inspector,
               acc_name,acc_group,acc_location,
               acc_img,acc_time,acc_comment,question_rec_id
               ]
        df_record.loc[len(df_record.index)] = row
    return df_record

print('Complete Calculation Function part!')

df_export_oap = get_station_summary('OAI')
df_export_oup = get_station_summary('OUP')
df_export_record = get_record_db()

def get_ptai_excelreport():
    df_export_overview = get_ptai_all()
    df_export_report = get_ptai_report()

    df_export_report['key'] = df_export_report["station"] + df_export_report["level"].astype(str)
    df_export_overview['key'] = df_export_overview["Station Name"] + df_export_overview["Level"].astype(str)
    # JOIN TABLE
    df_merge_report = df_export_overview.join(df_export_report.set_index('key'), on='key')

    df_merge_report['PTAI100'] = df_merge_report['PTAI']*10+50
    # create a list of our conditions
    conditions = [
        (df_merge_report['PTAI100'] <= 49),
        (df_merge_report['PTAI100'] > 49) & (df_merge_report['PTAI100'] <= 54),
        (df_merge_report['PTAI100'] > 54) & (df_merge_report['PTAI100'] <= 59),
        (df_merge_report['PTAI100'] > 59) & (df_merge_report['PTAI100'] <= 64),
        (df_merge_report['PTAI100'] > 64) & (df_merge_report['PTAI100'] <= 69),
        (df_merge_report['PTAI100'] > 69) & (df_merge_report['PTAI100'] <= 74),
        (df_merge_report['PTAI100'] > 74) & (df_merge_report['PTAI100'] <= 79),
        (df_merge_report['PTAI100'] > 79) & (df_merge_report['PTAI100'] <= 84),
        (df_merge_report['PTAI100'] > 84) & (df_merge_report['PTAI100'] <= 89),
        (df_merge_report['PTAI100'] > 84) & (df_merge_report['PTAI100'] <= 89),
        (df_merge_report['PTAI100'] > 89) & (df_merge_report['PTAI100'] <= 94),
        (df_merge_report['PTAI100'] > 94)
        ]

    # create a list of the values we want to assign for each condition
    values = [
        'ไม่สามารถใช้งานได้|Unusable',
        'ใช้งานด้วยตัวเองได้ 0%',
        'ใช้งานด้วยตัวเองได้ 10%',
        'ใช้งานด้วยตัวเองได้ 20%',
        'ใช้งานด้วยตัวเองได้ 30%',
        'ใช้งานด้วยตัวเองได้ 40%',
        'ใช้งานด้วยตัวเองได้ 50%',
        'ใช้งานด้วยตัวเองได้ 60%',
        'ใช้งานด้วยตัวเองได้ 70%',
        'ใช้งานด้วยตัวเองได้ 80%',
        'ใช้งานด้วยตัวเองได้ 90%',
        'ใช้งานด้วยตัวเองได้ 99%',
    ]
    values_rating = [
        'ยากมาก',
        'ยาก',
        'ระวัง',
        'พอใช้',
        'พอใช้',
        'ดี',
        'ดี',
        'ดีมาก',
        'ดีมาก',
        'ดีเยี่ยม',
        'ดีเยี่ยม',
        'มาตรฐาน',
    ]

    # create a new column and use np.select to assign values to it using our lists as arguments
    df_merge_report['ratings%'] = np.select(conditions, values)
    df_merge_report['ratings'] = np.select(conditions, values_rating)

    filename = 'ptai_report.xlsx'
    df_merge_report.to_excel('output/{}'.format(filename))

    return df_merge_report


# default CSV
def df2csv(df,name):
    df.to_csv('output/{}.csv'.format(name), index = False)

df2csv(df_export_overview, 'ptai_overall')
df2csv(df_export_oap, 'ptai_oap')
df2csv(df_export_oup, 'ptai_oup')
df2csv(df_export_record,'ptai_record')
df2csv(df_export_report,'ptai_report')





