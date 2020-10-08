# Import Library
import pandas as pd
import json

print("Pandas version", pd.__version__)

###FUNCTION :: Import Question Database
def get_ptai_question(path):
    df_question = pd.read_csv(
        path)
    return df_question

PATH_QUESTION = 'db\\T4A_PTAI_QA.csv'
df_question_db = get_ptai_question(PATH_QUESTION)

###GET only question list form DB
df_questionlist = df_question_db.drop_duplicates(subset=['Q_code']).reset_index()

###FUNCTION :: Extract data from google sheet database
def get_response(url):
    EXCEL_FORMAT = 'export?format=xlsx&'
    excel_url = url.replace('edit', EXCEL_FORMAT)
    df = pd.read_excel(excel_url, encoding='unicode_escape')
    return df

# Import response data
form_url = "https://docs.google.com/spreadsheets/d/1SN2lYQLvXx6H9FjYAtdPCpT_L0SJzcxfCGmgI7kv_ao/edit#gid=283051997"
df2 = get_response(form_url)


###FUNCTION :: Import Question form Google Form for recheck
def get_formquestion(df):
    # Get Question form column header begin with R
    ggform_question = []
    for col in df.columns:
        if col.startswith('R'):
            ggform_question.append(col)
        if col.startswith('Unname'):  # drop unnamed column
            del df[str(col)]

    cell = {'question': ggform_question}
    question_df = pd.DataFrame(cell)
    question_df.sort_values(by=['question'], inplace=True)
    return question_df


##Get Question list
q_df = get_formquestion(df2)

# Split question
split_question = q_df['question'].str.split(' : ', n=1, expand=True)
q_df['q_code'] = split_question[0]
q_df['q_name'] = split_question[1]
print(q_df)

q_df.to_excel('form_question.xlsx', engine='xlsxwriter')

df_question_join = q_df.join(df_question_db, lsuffix='_form', rsuffix='_db')

# Import station database
path_station = 'db\\m_station_db.csv'


###FUNCTION :: Import station db
def get_station_db(path):
    df_stn = pd.read_csv(
        path)
    df_stn = df_stn.rename(columns={"name_th": "stn_name_th"})
    df_stn.info()
    return df_stn


df1 = get_station_db(path_station)



###FUNCTION :: Transform_header response to standard pattern
def transform_header(df):  ###Transform_header dataframe to English format
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

df3 = df2.copy()
df3 = transform_header(df3)

df3['stn_name_th'].unique().shape


# df = df3.head(10)

###FUNCTION :: Get one response following index_num

def get_dict_response(df, index_num):  # Get one of accessibility item result
    i = index_num
    f = df.loc[i, 'r_id']  # Read r_id group
    ans = df.loc[i, df.columns.str.contains(f)]  # Get R-response following R-Group

    for x in range(len(ans)):
        if type(ans[x]) != float:  # Check value in cell is None or not
            if ans[x].count(':') >= 1:  # Find one or multiple choice answer
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

a = get_dict_response(df3, 9)

###FUNCTION :: Get batch responses following index_num range
def batch_response(df, start, end):
    acc_item = {}

    for row in range(start, end):
        one_item = get_dict_response(df, row)
        # s = str(row)
        acc_item[one_item['ID']] = one_item
    return acc_item


####TEST FUNCTION
a = get_dict_response(df3, 1)
a = batch_response(df3, 0, 10)

##EXPORT JSON
acc_json = json.dumps(a, indent=4, ensure_ascii=False)
print(acc_json)
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(a, f, ensure_ascii=False, indent=4)

# EXPORT QUESTION LIST


# ===============================================================================================================
