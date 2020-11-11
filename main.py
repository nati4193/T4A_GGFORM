
###################################################################################################################
#IMPORT Library
import pandas as pd
import json
import numpy as np
import difflib


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
###################################################################################################################
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
score_db = pd.DataFrame(data=[100, 100, 100, 55,60,70,0,20,30],
                        columns=['point'],
                        index=['4P','2P','1P','4M','2M','1M','4D','2D','1D'])

###################################################################################################################
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
df_standard = transform_header(df_form)

def get_rgform_set(df):
    rg_set = sorted(set(list(df['r_id'])))
    return rg_set

def get_utype_set(df=df_question_db):
    utype_set = sorted(set(list(df['U'])))
    return utype_set



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

###################################################################################################################
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
ptai_dict_some = batch_response(df_standard,1,1512)
#ptai_dict_all = batch_response(df_standard,1,1512)

### FUNCTION MERGE QUESTION and SCORE DATABASE TO DICT
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
            ptai_dict[id]['attribute']['ans_dict'][ans_id]['point'] = int(a_point)

    return ptai_dict

#########################################################################
#TEST FUNCTION
merged_dict = merge_score(ptai_dict_some,df_question_db)

##_EXPORT Database to JSON
def export2json(dict,filename):
    with open(f'output/{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(dict,f, ensure_ascii=False, indent=4)

#export2json(ptai_dict_some,"dictsome3")
export2json(merged_dict,"PTAI_DB")

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
'''
#GET AVERAGE ONE RECORD POINT
rec_id = '00077'
lv = 3
option = 'Dataframe'
'''

#FUNCTION >> Get Ri Point for each R-Group in a Station
def get_item_point(rec_id,lv,option):
    a1 = recursive_lookup(rec_id,merged_dict)
    a2 = recursive_lookup('ans_dict',a1)
    a_list = list(a2.keys())
    point_list = []
    count_list = []
    for item in a_list:
        a3 = recursive_lookup(item,a2)
        s = recursive_lookup('score',a3)
        p = recursive_lookup('point',a3)
        l = recursive_lookup('L',a3)
        if s != 'X':
            if l <= lv :
                point_list.append(p)
                count_list.append(s)
            else:
                pass
        else:
            pass

    point_rec_avg = np.average(point_list)
    point_rec_total = np.sum(point_list)

    if str(option) == 'point':
        return point_rec_avg
    elif str(option) == 'dataframe':
        qcount = len(point_list)
        pcount = sum(map(lambda x : x == 'P', count_list))
        mcount = sum(map(lambda x : x == 'M', count_list))
        dcount = sum(map(lambda x : x == 'D', count_list))

        d = [(rec_id,point_rec_total,point_rec_avg,lv,qcount,pcount,mcount,dcount)]
        df_rec = pd.DataFrame(d,columns=['REC_ID','Total point','AVG POINT','Lv.','Q count','P count','M Count','D Count'])

        return df_rec
    else:
        return print("Input option for get data")

#FUNCTION >> GET AVERAGE RX Point for Station
def get_rx_point(station,rgroup,lv,option):
    rg = rgroup
    a_rx_list = [] # collect all rec_id in Rx
    a_rx_score = []

    for id in merged_dict:
       si = merged_dict[id]['attribute']['station_name']
       ri = merged_dict[id]['attribute']['accessibility_group']
       if si == station and ri == rg:
           a_rx_list.append(id)
       else:
           pass

    for id in a_rx_list:
        d = get_item_point(id,lv,'point')
        a_rx_score.append(d)


    point_rx_avg = round(np.average(a_rx_score),2)
    point_rx_total = np.sum(a_rx_score)
    print(a_rx_list,a_rx_score)
    print(point_rx_total,point_rx_avg)
    point_rx_list = [station,rgroup,point_rx_avg]

    if option == 'point':
        return point_rx_avg
    elif option == 'list':
        return point_rx_list

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
                print(ans_id,u_score,u_point,u_id,l)

            else:
                pass

    if len(a_rq_score) == 0:
        print("There is no this type of access need")
        iu_point = None
    else:
        iu_point = round(np.average(a_rq_score),2)
        print("iu_point : " + str(iu_point))

    return iu_point

### FUNCTION >> Find IU_point for a Station group bu User Access Need

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
                print(ans_id,u_score,u_point,u_id,l)

            else:
                pass

    if len(a_rq_score) == 0:
        print("There is no this type of access need")
        up_point = None
    else:
        up_point = round(np.average(a_rq_score),2)
        print("iu_point : " + str(up_point))

    return up_point

# >>>>> ASSIGN STATION <<<<<
station = station_list[10]


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
    print(i_rx_point,i_rx_total,count)

    return i_rx_point

#TEST FUNCTION
get_irx_point(station,'R03',1)

### FUNCTION >> GET Overall point (OAP) for each R-Group in a station
def get_oap(station,rg,lv,option):
    oa = get_rx_point(station,rg,lv,'point')
    oi = get_irx_point(station,rg,lv)
    overall = (oa + oi)/2
    print(station,rg,lv,overall)
    overall_list = [station,rg,lv,oa,oi,overall]
    if option == 'point':
        return overall
    elif option == 'list':
        return overall_list


#TEST FUNCTION
get_oap(station,'R01',1,'point')
get_oap(station,'R01',1,'list')
get_rx_point(station,'R01',1,'list')

### FUNCTION >> CREATE Accessible Facilities (AF) DataFrame for a station
def get_af_table(station,lv,option):
    rg_set = get_rgform_set(df_standard)
    af_df = pd.DataFrame(columns=['station','rg','af_point'])
    for rg in rg_set:
        af_list = []
        af = get_rx_point(station,rg,lv,'list')
        af_df.loc[len(af_df)] = af

    oap_list = af_df['af_point'].dropna().astype(int).tolist()
    oap = np.average(oap_list)

    if option == 'dataframe':
        return af_df
    elif option == 'point':
        return oap

get_af_table(station,1,'point')

### FUNCTION >> CREATE Accessible User need (AU) DataFrame for a station
def get_up_table(station,lv,option):
    utype_set = get_utype_set()
    an_df = pd.DataFrame(columns=['station','U type','an_point'])
    for u in utype_set:
        an_list = []
        an = get_up_point(station,u,lv)
        an_list = [station,u,an]
        an_df.loc[len(an_df)] = an_list

    oup_list = an_df['an_point'].dropna().astype(int).tolist()
    oup = np.average(oup_list)

    if option == 'dataframe':
        return an_df
    elif option == 'point':
        return  oup

#TEST FUNCTION
get_up_table(station,1,'dataframe')

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

#TEST FUNCTION
get_scoresummary_allstation(1,'oap')
oup_df = get_scoresummary_allstation(1,'oup')

def get_overall_station(station,lv,option):
    oap = get_af_table(station,lv,'point')
    oup = get_up_table(station,lv,'point')
    op = (oap + oup)/2

    if option == 'oap':
        print('Result : {},{},OAP Output = {}'.format(station,lv,oap))
        return oap
    elif option == 'oup':
        print('Result : {},{},OUP Output = {}'.format(station,lv,oup))
        return oup
    elif option == 'op':
        print('Result : {},{},OVERALL Output = {}'.format(station,lv,op))
        return op
    else:
        print('Check argument')

oa = get_overall_station(station,2,'oap')
op = get_overall_station(station,2,'oup')
overall = get_overall_station(station,2,'op')

print(oa,op,overall)

#check station location
stn_db_list = df_stn_db['stn_name_th'].tolist()
for station in station_list:
    stn_similar = difflib.get_close_matches(station,stn_db_list)
    #print('Find station : {} = Station : {}'.format(station,stn_similar))
    #print(stn_similar[0])
    if station != stn_similar[0]:
        print(station)
    else:
        pass





