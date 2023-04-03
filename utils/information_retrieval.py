import pandas as pd
import json
import numpy as np
from utils.db.get_data_db import get_t_options

## RESPONSE TIMES
def get_times_for_tt(participants, t_ids, data):
    """
        participants: List of participants id to consinder
        tt:           String in {'T1','T2'}
        t_ids:        List of task ids corresponding to tt
        data:         Dict with processed data from database
    """
    times = {}
    for p in participants:
        for t in t_ids:
            if t not in times:
                times[t] = []
            if t in data[p]['t_answers']:
                times[t].append(data[p]['t_answers'][t]['response_time'])
    return times

## CORRECT ANSWERS
def _opts_per_task(t_options, t_ids, remove_both = False):
    """
        t_options: task options as retrieved by database (List of tuples)
    """
    opts_per_task={}
    corr_per_task = {}
    for i,row in enumerate(t_options):
        if row[0] in t_ids:
            if row[0] not in opts_per_task:
                opts_per_task[row[0]] = []
            if row[0] not in corr_per_task:
                corr_per_task[row[0]] = []  
            if 'None' not in row[1]:
                if 'Both' in row[1] and row[2] and remove_both:
                    corr_per_task[row[0]].append(t_options[i-2][1])
                    corr_per_task[row[0]].append(t_options[i-1][1])
                else:
                    if not ('Both' in row[1] and remove_both):
                        opts_per_task[row[0]].append(row[1])
                    if row[2]:
                        corr_per_task[row[0]].append(row[1])
    return opts_per_task, corr_per_task

def _opts_per_task_T2(t_options, t_ids):
    """
        t_options: task options as retrieved by database (List of tuples)
    """
    opts_per_task={}
    corr_per_task = {}
    for i,row in enumerate(t_options):
        if row[0] in t_ids:
            if row[0] not in opts_per_task:
                opts_per_task[row[0]] = []
            if row[0] not in corr_per_task:
                corr_per_task[row[0]] = []  
            if 'None' not in row[1] and 'Causal' not in row[1]:
                opts_per_task[row[0]].append(row[1])
                if row[2]:
                    corr_per_task[row[0]].append(row[1])
    return opts_per_task, corr_per_task

def _answers_per_task(participants, t_ids, data, get_from_opt = True):
    """
        participants: List of participants id to consinder
        t_ids:        List of Strings of task ids
        data:         Dict with processed data from database
    """
    answers_per_task = {}
    for p in participants:
        for t in t_ids:
            if t in data[p]['t_answers']:
                if t not in answers_per_task:
                    answers_per_task[t] = []
                if get_from_opt:
                    answers = []
                    for ans in data[p]['t_answers'][t]['options']:
                        if ans not in answers: ## remove cases where users' response was stored in db more than 1 times due to a bug
                            if 'Both' in ans:
                                answers.append('Causal Model 1')
                                answers.append('Causal Model 2')
                            else:
                                answers.append(ans)
                    # answers = data[p]['t_answers'][t]['options']
                else:
                # if data[p]['t_answers'][t]['model_opt'] != "":
                    answers = [data[p]['t_answers'][t]['model_opt']]
                answers_per_task[t].append(answers)
    return answers_per_task

def get_hamming_distance(t_options, participants, t_ids, data, tt):
    """
        Returns hamming distance of participants answers from correct answers of t_ids tasks
        
        t_options:    task options as retrieved by database (List of tuples)
        participants: List of participants id to consinder
        t_ids:        List of task ids we want to get hamming distance for
        data:         Dict with processed data from database
    """
    if tt == 'T1':
        opts_per_task, corr_answ_per_task = _opts_per_task(t_options, t_ids, remove_both = True)
    else:
        opts_per_task, corr_answ_per_task = _opts_per_task_T2(t_options, t_ids)
    # print("opt", opts_per_task)
    # print("corr", corr_answ_per_task)
    answers_per_task = _answers_per_task(participants, t_ids, data)
    # print("ans",answers_per_task)
    return get_hamming_distances_per_task(opts_per_task, corr_answ_per_task, answers_per_task)
    
def get_hamming_distances_per_task(opts_per_task, cor_answ_per_task, answers_per_task):
#     print("opts_per_task",opts_per_task,"cor_answ_per_task",cor_answ_per_task,"answers_per_task",answers_per_task)
    hamming_dist_per_task = {}
    for t in opts_per_task:
        opts_per_task[t].sort()
        binary_vec_corr = ""
        binary_vecs_answ = [""]*len(answers_per_task[t])
        if t not in hamming_dist_per_task:
            hamming_dist_per_task[t] = "" 
        for o in opts_per_task[t]:
            if o in cor_answ_per_task[t]:
                binary_vec_corr = binary_vec_corr+"1"
            else:
                binary_vec_corr = binary_vec_corr+"0"  
            # ans = ""
            for i,answer in enumerate(answers_per_task[t]):
                if o in answer:
                    binary_vecs_answ[i] = binary_vecs_answ[i]+"1"
                else:
                    binary_vecs_answ[i] = binary_vecs_answ[i]+"0"   
#         print("binary_vec_corr",binary_vec_corr,"binary_vecs_answ",binary_vecs_answ)
        hamming_dist_per_task[t] = _hamming_distance(binary_vec_corr, binary_vecs_answ)  
#     print('hamming_dist_per_task',hamming_dist_per_task)
    return hamming_dist_per_task

def _hamming_distance(binary_corr_answer, binary_answers):    
    """
        binary_corr_answer: String of 1s and 0s
        binary_answers:     List of Strings of 1s and 0s
    """
    hamming_distances = []
    for ans in binary_answers:
        hamming_distances.append(sum(c1 == c2 for c1, c2 in zip(ans, binary_corr_answer)))   
    return hamming_distances

def get_p_answers_digital(t_options, participants, t_ids, data):
    """
        t_options:    Task options as retrieved from database
        participants: List of participants id to consinder
        t_ids:        List of task ids corresponding to rq
        data:         Dict with processed data from database
    """
    _, corr_answ_per_task = _opts_per_task(t_options, t_ids)
    # print('corr',corr_answ_per_task)
    p_answ_digital = {}
    for p in participants:
        for t in t_ids:
            if t in data[p]['t_answers']:
                if t not in p_answ_digital:
                    p_answ_digital[t] = []
                # corr_answ = [s for s in corr_answ_per_task[t] if "Causal" in s][0]
                p_answ = [s for s in data[p]['t_answers'][t]['options'] if ("Causal" in s or "Both" in s)]
                if len(p_answ) == 0:
                    p_answ = data[p]['t_answers'][t]['model_opt']
                else:
                    p_answ = p_answ[0]
                # print(t,p,p_answ)
                if p_answ in corr_answ_per_task[t]:
                    p_answ_digital[t].append(1)
                else:
                    p_answ_digital[t].append(0)
    return p_answ_digital
    
# CONFIDENCE
def get_confidence(participants, t_ids, data):
    confidence = {}
    for p in participants:
        for t in t_ids:
            if t not in confidence:
                confidence[t] = []
            if t in data[p]['t_answers']:
                conf = int(data[p]['t_answers'][t]['confidence'][0])
                if conf == 1:
                    confidence[t].append(-2)
                elif conf == 2:
                    confidence[t].append(-1)
                elif conf == 3:
                    confidence[t].append(0)
                elif conf == 4:
                    confidence[t].append(1)
                elif conf == 5:
                    confidence[t].append(2)
    return confidence

## GET TIMES, ACCURACY, CONFIDENCE
def get_times_per_tt(data_processed, t_ids, db_file_path):
    """
        t_ids: Dict <TT: List of task_ids> 
    """
    ## split participants in 3 groups based on condition (interactive, static, animated)
    participants_i = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 'i' ]
    participants_s = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 's']
    participants_a = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 'a']

    ## get response times per TT
    times_i = {}
    times_i['T1'] = get_times_for_tt(participants_i, 
                                      t_ids['T1'], data_processed)
    times_i['T2'] = get_times_for_tt(participants_i, 
                                      t_ids['T2'], data_processed)
    
    times_s = {}
    times_s['T1'] = get_times_for_tt(participants_s, 
                                      t_ids['T1'], data_processed)
    times_s['T2'] = get_times_for_tt(participants_s, 
                                      t_ids['T2'], data_processed)

    times_a = {}
    times_a['T1'] = get_times_for_tt(participants_a, 
                                      t_ids['T1'], data_processed)
    times_a['T2'] = get_times_for_tt(participants_a, 
                                      t_ids['T2'], data_processed)
    return times_i, times_s, times_a

def get_confidence_per_tt(data_processed, t_ids, db_file_path):
    """
        t_ids: Dict <TT: List of task_ids> 
    """
    ## split participants in 3 groups based on condition (interactive, static, animated)
    participants_i = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 'i' ]
    participants_s = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 's']
    participants_a = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 'a']

    ## get confidence responses
    conf_i = {}
    conf_i['T1'] = get_confidence(participants_i, 
                                   t_ids['T1'], data_processed)
    conf_i['T2'] = get_confidence(participants_i, 
                                   t_ids['T2'], data_processed)

    conf_s = {}
    conf_s['T1'] = get_confidence(participants_s, 
                                   t_ids['T1'], data_processed)
    conf_s['T2'] = get_confidence(participants_s, 
                                   t_ids['T2'], data_processed)
    
    conf_a = {}
    conf_a['T1'] = get_confidence(participants_a, 
                                   t_ids['T1'], data_processed)
    conf_a['T2'] = get_confidence(participants_a, 
                                   t_ids['T2'], data_processed)
    return conf_i, conf_s, conf_a

def get_answers_scores_MCO(data_processed, t_ids, db_file_path, tt):
    """
        t_ids: List of task_ids for a specific TT
    """
    ## split participants in 3 groups based on condition (interactive, static, animated)
    participants_i = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 'i' ]
    participants_s = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 's']
    participants_a = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 'a']
    
    ## get correct answers per rq
    t_options = get_t_options(db_file_path)
    corr_answers_i = []
    corr_answers_i = get_hamming_distance(t_options, 
                                                 participants_i, t_ids, 
                                                 data_processed, tt)

    corr_answers_s = []
    corr_answers_s = get_hamming_distance(t_options, 
                                                 participants_s, t_ids, 
                                                 data_processed, tt)
    
    corr_answers_a = []
    corr_answers_a = get_hamming_distance(t_options, 
                                                 participants_a, t_ids, 
                                                 data_processed, tt)
    
    return corr_answers_i, corr_answers_s, corr_answers_a

def get_answers_scores_SCO(data_processed, t_ids, db_file_path):
    """
        t_ids: List of task_ids for a specific TT
    """
    ## split participants in 3 groups based on condition (interactive, static, animated)
    participants_i = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 'i' ]
    participants_s = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 's']
    participants_a = [p for p,p_details in data_processed.items() 
                      if p_details['mode'] == 'a']
    
    ## get correct answers per rq
    t_options = get_t_options(db_file_path)
    corr_answers_i = []
    corr_answers_i = get_p_answers_digital(t_options, 
                                             participants_i, t_ids, 
                                             data_processed)

    corr_answers_s = []
    corr_answers_s = get_p_answers_digital(t_options, 
                                             participants_s, t_ids, 
                                             data_processed)
    
    corr_answers_a = []
    corr_answers_a = get_p_answers_digital(t_options, 
                                             participants_a, t_ids, 
                                             data_processed)
    
    return corr_answers_i, corr_answers_s, corr_answers_a

def add_to_data_T1(data, task_types, answers,answers_multi, answ_demo, times,confidence,mode,participants):
    for t in answers:
        ## 'IG', 'AG', or 'SG'
        data['accuracy'].extend(answers[t])
        data['accuracy_ham'].extend(answers_multi[t])
        data['time'].extend(times[t])
        data['conf'].extend(confidence[t])
        data['condition'].extend([mode]*len(answers[t]))
        data['task'].extend([t]*len(answers[t]))
        data['participant'].extend(participants)
        data['intervention'].extend([task_types[t]]*len(answers[t]))
        data['d1'].extend(answ_demo['d1'])
        data['d2'].extend(answ_demo['d2'])
        data['d3'].extend(answ_demo['d3'])
        data['d4'].extend(answ_demo['d4'])
        data['d5'].extend(answ_demo['d5'])
        ## 'all'
        data['accuracy'].extend(answers[t])
        data['accuracy_ham'].extend(answers_multi[t])
        data['time'].extend(times[t])
        data['conf'].extend(confidence[t])
        data['condition'].extend(['all']*len(answers[t]))
        data['task'].extend([t]*len(answers[t]))
        data['participant'].extend(participants)
        data['intervention'].extend([task_types[t]]*len(answers[t]))
        data['d1'].extend(answ_demo['d1'])
        data['d2'].extend(answ_demo['d2'])
        data['d3'].extend(answ_demo['d3'])
        data['d4'].extend(answ_demo['d4'])
        data['d5'].extend(answ_demo['d5'])
        
def add_to_data_T2_model(data, task_types, answers, answ_intervention, answ_demo, times,confidence,mode,participants):
    for t in answers:
        ## 'IG', 'AG', or 'SG'
        data['accuracy'].extend(answers[t])
        data['accuracy_intervention'].extend(answ_intervention[t])
        data['time'].extend(times[t])
        data['conf'].extend(confidence[t])
        data['condition'].extend([mode]*len(answers[t]))
        data['task'].extend([t]*len(answers[t]))
        data['participant'].extend(participants)
        data['intervention'].extend([task_types[t]]*len(answers[t]))
        data['d1'].extend(answ_demo['d1'])
        data['d2'].extend(answ_demo['d2'])
        data['d3'].extend(answ_demo['d3'])
        data['d4'].extend(answ_demo['d4'])
        data['d5'].extend(answ_demo['d5'])
        ## 'all'
        data['accuracy'].extend(answers[t])
        data['accuracy_intervention'].extend(answ_intervention[t])
        data['time'].extend(times[t])
        data['conf'].extend(confidence[t])
        data['condition'].extend(['all']*len(answers[t]))
        data['task'].extend([t]*len(answers[t]))
        data['participant'].extend(participants)
        data['intervention'].extend([task_types[t]]*len(answers[t]))
        data['d1'].extend(answ_demo['d1'])
        data['d2'].extend(answ_demo['d2'])
        data['d3'].extend(answ_demo['d3'])
        data['d4'].extend(answ_demo['d4'])
        data['d5'].extend(answ_demo['d5'])