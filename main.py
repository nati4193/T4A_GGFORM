# IMPORT Library
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
    df['rec_id'] = df.index.astype(int)

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

def get_dict_response(df, index_num):  # Get one of accessibility item result
    i = index_num
    r_group = df.loc[i, 'r_id']  # Read r_id group
    ans = df.loc[i, df.columns.str.contains(r_group)]  # Get R-response following R-Group

    for x in range(len(ans)):
        if type(ans[x]) != float:  # Check value in cell is None or not
            if ans[x].count(':') >= 1:  # Find one or multiple choice answer
                ans_list = ans[x].split(", ")
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


test_get = get_dict_response(df_standard, 9)


###FUNCTION :: Get batch responses following index_num range
def batch_response(df, start, end):
    acc_item = {}

    for row in range(start, end):
        one_item = get_dict_response(df, row)
        # s = str(row)
        acc_item[one_item['id']] = one_item
    return acc_item


####TEST FUNCTION
a = get_dict_response(df3, 1)
df_dict_100 = batch_response(df_standard, 0, 100)


##_MERGE


##_EXPORT to JSON
def export2json(dict):
    # acc_json = json.dumps(dict, indent=4, ensure_ascii=False)
    with open('output/data.json', 'w', encoding='utf-8') as f:
        json.dump(dict, f, ensure_ascii=False, indent=4)


export2json(df_dict_100)

# EXPORT QUESTION LIST


# ===============================================================================================================
