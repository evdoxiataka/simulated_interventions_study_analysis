from .utils import create_connection, close_connection

from sqlite3 import Error
import numpy as np
import csv

def get_d_questions(conn):
    try:
        cur = conn.cursor()    
        cur.execute("SELECT * FROM d_questions")
        return cur.fetchall()
    except Error as e:
        print(e)
        return [] 

def get_d_options(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT d_name,option FROM d_options")
            r = cur.fetchall()
            close_connection(conn)
        d_options = {}
        for row in r:
            if row[0] not in d_options:
                d_options[row[0]] = []
            d_options[row[0]].append(row[1])
        return d_options
    except Error as e:
        print(e)
        return []
    
def get_participants(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT name,pool_email,results_email FROM participants")
            # cur.execute("SELECT pool_email FROM participants")
            # cur.execute("SELECT results_email FROM participants")
            r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_participants_json(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT * FROM participants")
            r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]     
            # r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_participants_where(db_file, p_id):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT * FROM participants WHERE name=?",(p_id,))
            r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_introduction_page(db_file, page_name, mode):
    try:
        conn = None
        conn = create_connection(db_file)
        page_contents = {}
        if conn:
            ## fetch intro page content
            cur = conn.cursor()    
            cur.execute("SELECT text_content, model_id FROM introduction WHERE name=? and mode=?",(page_name,mode))
            r_pages = cur.fetchall()       
            page_contents["text_content"] = r_pages[0][0]
            page_contents["dag_id"] = r_pages[0][1]
            ## fetch model files 
            cur.execute("SELECT ii, file FROM intro_model_filepaths WHERE name=? and mode=?",(page_name,mode))
            r_files = cur.fetchall()
            for row in r_files: 
                if "files" not in page_contents:
                    page_contents["files"] = []           
                page_contents["files"].insert(row[0],row[1]) 
            ## fetch i_type   
            cur.execute("SELECT i_type FROM intro_i_types WHERE name=? and mode=?",(page_name,mode))
            r_itype = cur.fetchall()
            for i_type in r_itype:
                if "action_vars" not in page_contents:
                    page_contents["action_vars"] = {}
                    page_contents["var_order"] = ["anxiety","tiredness","insomnia"]
                page_contents["action_vars"][i_type[0]] = []                 
            ## fetch i_vars  
            for i_type in r_itype: 
                cur.execute("SELECT i_var FROM intro_i_vars WHERE name=? and mode=? and i_type=?",(page_name,mode,str(i_type[0])))
                r_ivar = cur.fetchall()
                for row in r_ivar:           
                    page_contents["action_vars"][i_type[0]].append(row[0])
            close_connection(conn)
        return page_contents
    except Error as e:
        print(e)
        return {}

def get_interactive_modes_count(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT COUNT(mode) FROM participants WHERE mode='i'")
            r =  cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_animated_modes_count(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT COUNT(mode) FROM participants WHERE mode='a'")
            r =  cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_static_modes_count(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT COUNT(mode) FROM participants WHERE mode='s'")
            r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return [] 

def get_next_participant(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT name FROM participants ORDER BY name DESC")
            rows = cur.fetchall()            
            close_connection(conn)
            r = np.random.randint(0,200,1).item()
            while((r,) in rows):
                r = np.random.randint(0,200,1).item()
            return r
            # if len(rows):
            #     r = rows[0][0] + 1
            # else:
            #     r = 0
        return r
    except Error as e:
        print(e)
        return []

def get_d_answers(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT * FROM d_answers")
            r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_ue_answers(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT * FROM ue_answers")
            r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_t_questions(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT * FROM tasks")
            r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []
    
def get_d_answers_where(db_file, p_id):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT d_name, option, text FROM d_answers WHERE participant_id=?",(p_id,))
            # r = cur.fetchall()
            r = [dict((cur.description[i][0], value) \
            for i, value in enumerate(row)) for row in cur.fetchall()]  
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []
    
def get_ue_answers_where(db_file, p_id):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT ue_name, slider_value, text FROM ue_answers WHERE participant_id=?",(p_id,))
            # r = cur.fetchall()
            r = [dict((cur.description[i][0], value) \
            for i, value in enumerate(row)) for row in cur.fetchall()]  
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_t_answers(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT * FROM t_answers")
            r = cur.fetchall()
            close_connection(conn)            
        return r
    except Error as e:
        print(e)
        return []

def get_t_answers_where(db_file, p_id):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT t_name, response_time, confidence, model_opt, toggle_clicks, ii FROM t_answers WHERE participant_id=?",(p_id,))
            # r = cur.fetchall()
            r = [dict((cur.description[i][0], value) \
            for i, value in enumerate(row)) for row in cur.fetchall()]   
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

# def get_t_answers_selection(db_file, p_id, t_name):
#     try:
#         conn = None
#         conn = create_connection(db_file)
#         r = []
#         if conn:
#             cur = conn.cursor()    
#             cur.execute("SELECT sel_order,var_name,xmin,xmax FROM t_answers_selections WHERE participant_id=? and t_name=?",(p_id,t_name))
#             # r = cur.fetchall()
#             r = [dict((cur.description[i][0], value) \
#             for i, value in enumerate(row)) for row in cur.fetchall()]  
#             close_connection(conn)
#         return r
#     except Error as e:
#         print(e)
#         return []

def get_t_answers_opts_where(db_file, p_id , t_name):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT option FROM t_answers_opts WHERE participant_id=? and t_name=?",(p_id,t_name))
            r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_t_answers_opts(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT * FROM t_answers_opts")
            r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_t_answers_intervention_selection(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT * FROM t_answers_selections")
            r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_task_type_where(db_file,p_id):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT desc FROM task_types WHERE name=?",(p_id,))
            r = cur.fetchall()
            close_connection(conn)
            if len(r):
                return r[0][0]
                # desc = r[0][0]
                # idx = desc.find('.')
                # strs = []
                # while idx > -1:
                #     strs.append(desc[0:idx+1])
                #     desc = desc[idx+1:]
                #     idx = desc.find('.')
                # return strs
        return r
    except Error as e:
        print(e)
        return []

def get_tasks_order(db_file,p_id):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT task_type,t_name,id FROM tasks_order WHERE participant_id=? ORDER BY id ASC",(p_id,))
            r = cur.fetchall()
            close_connection(conn)
            tasks = {}
            for row in r:
                if row[0] not in tasks:
                    tasks[row[0]] = []
                tasks[row[0]].append(row[1])
            r = tasks
        return r
    except Error as e:
        print(e)
        return []
    
def get_t_options(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT t_name,option,iscorrect FROM t_options")
            r = cur.fetchall()
            close_connection(conn)
        return r
    except Error as e:
        print(e)
        return []

def get_p_t(db_file):
    try:
        conn = None
        conn = create_connection(db_file)
        r = []
        if conn:
            cur = conn.cursor()    
            cur.execute("SELECT name, task_type FROM tasks")
            cur.execute("SELECT name, task_type FROM tasks")
            r = cur.fetchall()
            close_connection(conn)
            prob_tasks = {}
            for p_t in r:
                if p_t[1] not in prob_tasks:
                    prob_tasks[p_t[1]] = []
                prob_tasks[p_t[1]].append(p_t[0])
            return prob_tasks
        return r
    except Error as e:
        print(e)
        return []
        
def get_data(db_file):
    with open('data.csv', mode='w') as data:
        writer = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        participants = get_participants(db_file)
        header = ['p_id', 'mode', 'begin_timestamp', 'end_timestamp', 'results_email', 'pool_email']
        row = []
        is_first_row = True
        for p in participants:
            row = list(p)
            t_questions = get_t_answers_where(db_file,p[0])
            for t in t_questions:
                if is_first_row:
                    header.extend(['task_name','response_time','model_opt', 'toggle_clicks', 'ii'])
                row.extend(list(t))
            d_questions = get_d_answers_where(db_file,p[0])
            for d in d_questions:
                if is_first_row:
                    header.extend(['demographics_questions','option','text'])                    
                row.extend(list(d))
            if is_first_row:
                writer.writerow(header)
                is_first_row = False
            writer.writerow(row)

def get_data_json(db_file):
    # conn = None
    # conn = create_connection(db_file)
    # if conn:
    #     cur = conn.cursor()    
    #     query = ('SELECT participants.name, participants.mode, participants.status, participants.begin_timestamp, participants.end_timestamp, participants.results_email, participants.pool_email,' 
    #                 't_answers.t_name, t_answers.response_time, t_answers.confidence, t_answers.w_interactions, t_answers.s_interactions,'
    #                 't_answers_opts.option,'
    #                 't_answers_selections.sel_order, t_answers_selections.var_name,t_answers_selections.xmin,t_answers_selections.xmax,'
    #                 'd_answers.option,d_answers.text '
    #                 'FROM participants '
    #                 'INNER JOIN t_answers ON participants.name = t_answers.participant_id '
    #                 'INNER JOIN t_answers_opts ON t_answers_opts.t_name = t_answers.t_name '
    #                 'INNER JOIN t_answers_selections ON t_answers_selections.t_name = t_answers.t_name '
    #                 'INNER JOIN d_answers ON participants.name = d_answers.participant_id')
    #     cur.execute(query)
    #     rows = cur.fetchall()  
    participants = get_participants_json(db_file)
    r = {} 
    for p in participants:
        if "name" in p:
            p_id = p["name"]
            r[p_id] = {}
            ## t_answers
            t_answers = get_t_answers_where(db_file, p_id)
            p["t_answers"] = {}
            for t_a in t_answers:
                if "t_name" in t_a:
                    t_name = t_a["t_name"]
                    p["t_answers"][t_name] = {}
                    for t_a_k, t_a_v in t_a.items():
                        if t_a_k=="t_name":
                            continue
                        p["t_answers"][t_name][t_a_k] = t_a_v
                    p["t_answers"][t_name]["options"] = []
                    ## t_opts
                    t_opts = get_t_answers_opts_where(db_file, p_id, t_name)
                    for t_opt in t_opts:
                        p["t_answers"][t_name]["options"].append(t_opt[0])
                    p["t_answers"][t_name]["selections"] = {}
                    # ## t_selections
                    # t_selections = get_t_answers_selection(db_file, p_id, t_name)
                    # for t_sel in t_selections:
                    #     for key,value in t_sel.items():
                    #         if key == "sel_order":
                    #             p["t_answers"][t_name]["selections"][t_sel["sel_order"]] = {}
                    #         else:
                    #             p["t_answers"][t_name]["selections"][t_sel["sel_order"]][key] = value 
            ## demographics
            d_answers = get_d_answers_where(db_file, p_id)  
            p["d_answers"] = {} 
            for d_a in d_answers:
                if "d_name" in d_a:
                    d_name = d_a["d_name"]
                    p["d_answers"][d_name] = {}
                    for d_a_k, d_a_v in d_a.items():
                        if d_a_k=="d_name":
                            continue
                        p["d_answers"][d_name][d_a_k] = d_a_v
            # for key,value in p.items():
            #     if key!="name":
            #         r[p_id][key] = value 
            ## user experience
            ue_answers = get_ue_answers_where(db_file, p_id)  
            p["ue_answers"] = {} 
            for ue_a in ue_answers:
                if "ue_name" in ue_a:
                    ue_name = ue_a["ue_name"]
                    p["ue_answers"][ue_name] = {}
                    for d_a_k, d_a_v in ue_a.items():
                        if d_a_k=="ue_name":
                            continue
                        p["ue_answers"][ue_name][d_a_k] = d_a_v
            for key,value in p.items():
                if key!="name":
                    r[p_id][key] = value 
    return r        
    # r = [dict((cur.description[i][0], value) \
    #         for i, value in enumerate(row)) for row in cur.fetchall()]     
    # #     close_connection(conn)
    # return json.dumps( r )
    # return rows

def get_questions(db_file):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    conn = None
    conn = create_connection(db_file)
    qa = {}
    if conn:
        cur = conn.cursor()    
        ## t_questions
        cur.execute("SELECT tasks.name, question, mult_opts, file_id, \
                    task_types.name, \
                    t_options.option, \
                    t_files.file, \
                    t_var_order.var, \
                    t_interventions.i_type, t_interventions.i_var, \
                    t_options.id, t_files.id, t_var_order.id, t_interventions.id \
                    FROM tasks INNER JOIN task_types ON task_types.name = tasks.task_type \
                    INNER JOIN t_options ON t_options.t_name = tasks.name \
                    INNER JOIN t_files ON t_files.t_name = tasks.name \
                    INNER JOIN t_var_order ON t_var_order.t_name = tasks.name \
                    INNER JOIN t_interventions ON t_interventions.t_name = tasks.name \
                    ORDER BY tasks.name ASC, t_options.id ASC, t_files.id ASC, t_var_order.id ASC,t_interventions.id ASC")
        t_qs = cur.fetchall()
        for q in t_qs:
            if q[0] not in qa:
                qa[q[0]] = {}
                qa[q[0]]["question"] = q[1]
                qa[q[0]]["dag_id"] = q[3]
                qa[q[0]]["task_type"] = q[4]
                qa[q[0]]["radio"] = {}
                qa[q[0]]["radio"]["options"] = []
                # qa[q[0]]["radio"]["models"] = []
                qa[q[0]]["radio"]["mult_opts"] = q[2]
                qa[q[0]]["files"] = []
                qa[q[0]]["var_order"] = []
                qa[q[0]]["confidence_radios"] = {}
                qa[q[0]]["confidence_radios"]["options"] = []
                qa[q[0]]["action_vars"] = {}
                conf_opts = ['1 (not at all)','2 (slightly)','3 (somewhat)','4 (fairly)','5 (completely)']
                qa[q[0]]["confidence_radios"]["options"].extend(conf_opts)
            if q[6] not in qa[q[0]]["files"]:
                qa[q[0]]["files"].append(q[6])
            if q[7] not in qa[q[0]]["var_order"]:
                qa[q[0]]["var_order"].append(q[7])
            if q[4] == 'T1' and q[5] not in qa[q[0]]["radio"]["options"]:
                qa[q[0]]["radio"]["options"].append(q[5])
            elif q[4] == 'T2':
                if 'Causal' in q[5]:
                    if "models" not in qa[q[0]]["radio"]:
                        qa[q[0]]["radio"]["models"] = []
                    if q[5] not in qa[q[0]]["radio"]["models"]:
                        qa[q[0]]["radio"]["models"].append(q[5])
                elif 'Causal' not in q[5] and q[5] not in qa[q[0]]["radio"]["options"]:
                    qa[q[0]]["radio"]["options"].append(q[5])
            if q[8] not in qa[q[0]]["action_vars"]:
                qa[q[0]]["action_vars"][q[8]] = []
            if q[9] not in qa[q[0]]["action_vars"][q[8]]:
                qa[q[0]]["action_vars"][q[8]].append(q[9])
        ## d_questions
        cur.execute("SELECT name, question, d_options.option, d_questions.field, d_options.id \
                    FROM d_questions INNER JOIN d_options ON d_options.d_name = d_questions.name \
                    ORDER BY d_questions.name ASC, d_options.id ASC")
        d_qs = cur.fetchall()
        for q in d_qs:
            if q[0] not in qa:
                qa[q[0]] = {}
                qa[q[0]]["question"] = q[1]
                qa[q[0]]["radio"] = {}
                qa[q[0]]["radio"]["options"] = []
                qa[q[0]]["input_field"] = q[3]
            if q[2] not in qa[q[0]]["radio"]["options"]:
                qa[q[0]]["radio"]["options"].append(q[2])
        ## ue_questions
        cur.execute("SELECT name, question, slider, slider_low, slider_high \
                    FROM ue_questions ORDER BY ue_questions.name ASC")
        d_qs = cur.fetchall()
        for q in d_qs:
            if q[0] not in qa:
                qa[q[0]] = {}
                qa[q[0]]["question"] = q[1]
                if q[2]:
                    qa[q[0]]["slider"] = (q[3],q[4])
        close_connection(conn)
    return qa

if __name__ == '__main__':
    database = "/data/study_02.db"
    # print(get_p_t(database))
    print(get_t_answers(database))    
    # print(get_t_answers_opts(database))
    # print(get_t_answers_intervention_selection(database))
    print(get_interactive_modes_count(database))
    print(get_static_modes_count(database))
    print(get_animated_modes_count(database))
#     print(get_data(database))    
#     print(get_questions(conn))
    print(get_participants(database))
    # print(get_t_answers_opts(database,0))
    # print(get_data_json(database))
    print(get_ue_answers(database))
    # print(get_t_questions(database))