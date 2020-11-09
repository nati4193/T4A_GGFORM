
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