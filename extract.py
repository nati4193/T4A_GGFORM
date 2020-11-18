
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

#Set up score table
def score_setting():
    score_db = pd.DataFrame(data=[100, 100, 100, 55,60,70,0,20,30],
                            columns=['point'],
                            index=['4P','2P','1P','4M','2M','1M','4D','2D','1D'])
    return score_db

score_db = score_setting()

# FUNCTION :: Get R-ID set form response dataFrame
def get_rgform_set(df):
    rg_set = sorted(set(list(df['r_id'])))
    return rg_set

# FUNCTION :: Get U-type set form response dataFrame ('NW','AA','TA',...)
def get_utype_set(df=df_question_db):
    utype_set = sorted(set(list(df['U'])))
    return utype_set
df_stn_db = get_station_db(path_station)


ptai_dict_some = batch_response(df_standard,1,len(df_form))
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


def convert(o):
    if isinstance(o, np.int64): return int(o)
    raise TypeError



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
    if len(point_list) > 0:
        point_rec_avg = np.mean(point_list)
    else:
        point_rec_avg = 0
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


#FUNCTION >> GET AI Point for Station
def get_ai_station(station, rgroup, lv, option):
    rg = rgroup
    ai_id_list = [] # collect all rec_id in Rx
    ai_point_list = []

    for id in merged_dict:
       si = merged_dict[id]['attribute']['station_name']
       ri = merged_dict[id]['attribute']['accessibility_group']
       if si == station and ri == rg:
           ai_id_list.append(id)
       else:
           pass

    for id in ai_id_list:
        d = get_item_point(id,lv,'point')
        ai_point_list.append(d)

    if len(ai_point_list) > 0:
        ai_avg = np.mean(ai_point_list)
    else:
        ai_avg = 0
    ai_total = np.sum(ai_point_list)

    ai_info_list = [station,rgroup,ai_avg]

    #print(ai_id_list, ai_point_list)
    #print(ai_total, ai_avg)

    if option == 'point':
        return ai_avg
    elif option == 'list':
        return ai_info_list



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
                #print(ans_id,u_score,u_point,u_id,l)

            else:
                pass

    if len(a_rq_score) == 0:
        #print("There is no this type of access need")
        iu_point = None
    else:
        iu_point = round(np.average(a_rq_score),2)
        #print("iu_point : " + str(iu_point))

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
                #print(ans_id,u_score,u_point,u_id,l)

            else:
                pass

    if len(a_rq_score) == 0:
        #print("There is no this type of access need")
        up_point = None
    else:
        up_point = round(np.average(a_rq_score),2)
        #print("iu_point : " + str(up_point))

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
    oa = get_ai_station(station, rg, lv, 'point')
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
get_ai_station(station, 'R01', 1, 'list')

### FUNCTION >> CREATE Accessible Facilities (AF) DataFrame for a station
station =station_list[5]
#for station in station_list:
lv = 1

station = station_list[12]

def get_af_table(station,lv,option):
    rg_set = get_rgform_set(df_standard)
    af_df = pd.DataFrame(columns=['station','rg','af_point'])
    for rg in rg_set:
        af_list = []
        af = get_ai_station(station, rg, lv, 'list')
        af_df.loc[len(af_df)] = af

    oap_list = af_df['af_point'].dropna().astype(int).tolist()
    if len(oap_list) > 1:
        oap = np.mean(oap_list)
        oapx = (oap - 50) / 10
        oap_med = np.median(oap_list)
        oap_std = np.std(oap_list)
        oap_msx = (oap_med - oap_std - 50) / 10
    else:
        oap = 0
        oapx = 0
        oap_med = 0
        oap_std = 0
        oap_msx = 0

    ai_score = (oapx + oap_msx)*0.5
    if ai_score < 0:
        ai_score = 0

    if option == 'dataframe':
        return af_df
    elif option == 'point':
        return oap
    elif option == 'AI':
        return ai_score

get_af_table(station,1,'point')
get_af_table(station,1,'AI')

### FUNCTION >> CREATE Accessible User need (AU) DataFrame for a station
station = station_list[12]
def get_up_table(station,lv,option):
    utype_set = get_utype_set()
    an_df = pd.DataFrame(columns=['station','U type','an_point'])
    for u in utype_set:
        an_list = []
        an = get_up_point(station,u,lv)
        an_list = [station,u,an]
        an_df.loc[len(an_df)] = an_list

    oup_list = an_df['an_point'].dropna().astype(int).tolist()
    oup = int(np.mean(oup_list))
    oupx = (oup - 50) / 10
    oup_med = np.median(oup_list)
    oup_std = np.std(oup_list)
    oup_msx = (oup_med - oup_std - 50) / 10

    ii_score = (oupx + oup_msx) * 0.5
    if ii_score < 0:
        ii_score = 0


    if option == 'dataframe':
        return an_df
    elif option == 'point':
        return  oup
    elif option == 'II':
        return ii_score

#TEST FUNCTION
get_up_table(station,1,'dataframe')
get_up_table(station,1,'II')
get_up_table(station,1,'point')


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

oa = get_overall_station(station,2,'oap')
op = get_overall_station(station,2,'oup')
overall = get_overall_station(station,2,'op')

print(oa,op,overall)

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

#FUNCTION >> Get Location data


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
    IFI = np.round((IS_point-50)/10,2)

    print('IFI Index for station : {} = {}'.format(station,IFI))

    return IFI

### Calculate PTAI score

def get_ptai_all(lv):
    df_ptai = pd.DataFrame(columns=['Station Name', 'Lat', 'Lon','Coordinate', 'PTAI', 'AI', 'II', 'IFI', 'OVERALL', 'OA', 'OI'])

    for station in station_list:

        ai = int(get_af_table(station,lv,'AI'))
        ii = int(get_up_table(station,lv,'II'))
        ifi = get_ifi(station,lv)
        ptai = (ai + ii)*0.5

        oa = get_overall_station(station,lv,'oap')
        oi = get_overall_station(station,lv,'oup')
        overall = round(get_overall_station(station,lv,'op'),2)
        s = df_stn_db[[station in x for x in df_stn_db['stn_name_th']]]
        s_lat = str(s.iloc[0,16])
        s_lon = str(s.iloc[0,17])
        s_coordinate = ('{},{}'.format(s_lat,s_lon))
        row = [station,s_lat,s_lon,s_coordinate,ptai,ai,ii,ifi,overall,oa,oi]

        df_ptai.loc[len(df_ptai.index)] = row
    return df_ptai

df_export = get_ptai_all(1)

# default CSV
def df2csv(df,name):
    df.to_csv('output/{}.csv'.format(name), index = False)

df2csv(df_export,'ptai_plot3')






