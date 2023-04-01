import pandas as pd
import json
import numpy as np
# import arviz as az
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
# def _opts_per_task(t_options, t_ids):
#     """
#         t_options: task options as retrieved by database (List of tuples)
#     """
#     opts_per_task={}
#     corr_per_task = {}
#     for row in t_options:
#         if row[0] in t_ids:
#             if row[0] not in opts_per_task:
#                 opts_per_task[row[0]] = []
#             if row[0] not in corr_per_task:
#                 corr_per_task[row[0]] = []
#             if row[1] != 'non':
#                 opts_per_task[row[0]].append(row[1])
#                 if row[2]:
#                     corr_per_task[row[0]].append(row[1])
#     return opts_per_task, corr_per_task

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

def get_answers_scores_multiple_sel(data_processed, t_ids, db_file_path, tt):
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

def get_answers_scores_single_sel(data_processed, t_ids, db_file_path):
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

# ## PAIR PLOTS
# def get_means_from_traces(traces_dict):
#     metric = 'mean'
#     means = {}
#     for tr_id, data in traces_dict.items():
#         # convert traces and posterior predictive samples to ArviZ InferenceData objs
#         infdata = az.from_pymc3(data[0], posterior_predictive = data[1])
#         # get mean of posteriors
#         means[tr_id] = az.summary(infdata, var_names=[data[2]], kind='stats')[metric].tolist()
#     return means
    
# def get_data_response_pair_plot(t_ids, traces_dict): 
#     #means of traces
#     means_from_traces = get_means_from_traces(traces_dict)
#     #prepare data
#     pp_data = {}
#     pp_data = {'accuracy':means_from_traces['acc_rq1'][:], 
#                'response_time':means_from_traces['rt_rq1'][:],
#                'confidence':means_from_traces['conf_rq1'][:],
#               "Task Type":["T1"]*len(means_from_traces['acc_rq1']),
#               "task":t_ids['T1'][:],
#               "color":["skyblue"]*len(t_ids['T1'])
#               }
#     pp_data['accuracy'].extend(means_from_traces['acc_rq2'])
#     pp_data['response_time'].extend(means_from_traces['rt_rq2'])
#     pp_data['confidence'].extend(means_from_traces['conf_rq2'])
#     pp_data['task'].extend(t_ids['T2'])
#     pp_data['color'].extend(["blue"]*len(t_ids['T2']))
#     pp_data['Task Type'].extend(["T2"]*len(means_from_traces['acc_rq2']))
    
#     return pd.DataFrame(pp_data), pp_data

# def get_data_response_interaction_pair_plot(means_from_traces):
#     # mean of posteriors
#     mean_acc_rq1 = means_from_traces['acc_rq1']
#     mean_acc_rq2 = means_from_traces['acc_rq2']
#     mean_acc_rq3 = means_from_traces['acc_rq3']
#     mean_rt_rq1  = means_from_traces['rt_rq1']
#     mean_rt_rq2  = means_from_traces['rt_rq2']
#     mean_rt_rq3  = means_from_traces['rt_rq3']
#     mean_conf_rq1 = means_from_traces['conf_rq1']
#     mean_conf_rq2 = means_from_traces['conf_rq2']
#     mean_conf_rq3 = means_from_traces['conf_rq3']
    
#     mean_acc = [mean_acc_rq1[0],mean_acc_rq2[0],mean_acc_rq2[1],mean_acc_rq2[2], mean_acc_rq3[0],
#                mean_acc_rq1[1],mean_acc_rq2[3],mean_acc_rq2[4],mean_acc_rq2[5],mean_acc_rq3[1],mean_acc_rq3[2],
#                mean_acc_rq1[2], mean_acc_rq1[3],mean_acc_rq2[6],mean_acc_rq2[7],mean_acc_rq2[8],mean_acc_rq2[9],mean_acc_rq3[3],mean_acc_rq3[4]]
#     mean_conf = [mean_conf_rq1[0],mean_conf_rq2[0],mean_conf_rq2[1],mean_conf_rq2[2],mean_conf_rq3[0],
#                mean_conf_rq1[1],mean_conf_rq2[3],mean_conf_rq2[4],mean_conf_rq2[5],mean_conf_rq3[1],mean_conf_rq3[2],
#                mean_conf_rq1[2], mean_conf_rq1[3],mean_conf_rq2[6],mean_conf_rq2[7],mean_conf_rq2[8],mean_conf_rq2[9],mean_conf_rq3[3],mean_conf_rq3[4]]
#     mean_rt = [mean_rt_rq1[0],mean_rt_rq2[0],mean_rt_rq2[1],mean_rt_rq2[2],mean_rt_rq3[0],
#                mean_rt_rq1[1],mean_rt_rq2[3],mean_rt_rq2[4],mean_rt_rq2[5],mean_rt_rq3[1],mean_rt_rq3[2],
#                mean_rt_rq1[2], mean_rt_rq1[3],mean_rt_rq2[6],mean_rt_rq2[7],mean_rt_rq2[8],mean_rt_rq2[9],mean_rt_rq3[3],mean_rt_rq3[4]]
#     #prepare data
#     #indices = [0,0,0,1,2,3,4,4,4,5,5,5,6,7,8,9,9,9,10,10,10,11,11,11,11,12,12,12,12,13,14,15,16,17,17,18,18]
#     rq = ["T1"] + ["T2"]*3 + ["T3"] + ["T1"] + ["T2"]*3 + ["T3"]*2 + ["T1"]*2 + ["T2"]*4 + ["T3"]*2
#     color = ['skyblue','blue','blue','blue',"navy",
#             'skyblue','blue','blue','blue',"navy","navy",
#             'skyblue','skyblue','blue','blue','blue','blue',"navy","navy"]
#     pp_data = {}
#     pp_data = {'num_boxes':means_from_traces['num_boxes'],
#                'len_boxes':means_from_traces['len_boxes'],
#                'accuracy': mean_acc, 
#                'response_time': mean_rt,
#                'confidence': mean_conf,
#                 "Task Type":rq,
#               'color':color}

#     return pd.DataFrame(pp_data), pp_data

# def get_data_interaction_scatter_plot(means_from_traces):
#     # prepare data
#     rq = ["T1"] + ["T2"]*3 + ["T3"] + ["T1"] + ["T2"]*3 + ["T3"]*2 + ["T1"]*2 + ["T2"]*4 + ["T3"]*2
#     color = ['skyblue','blue','blue','blue',"navy",
#             'skyblue','blue','blue','blue',"navy","navy",
#             'skyblue','skyblue','blue','blue','blue','blue',"navy","navy"]
#     pp_data = {}
#     pp_data = {'num_boxes':means_from_traces['num_boxes'], 
#                'len_boxes':means_from_traces['len_boxes'],
#               'Task Type':rq,
#               'color':color}
#     return pd.DataFrame(pp_data)

# ## FOREST PLOT
# # select the relevant task from the dataset, by name
# def get_task(datasets, task):    
#     for s in datasets:        
#         try:
#             return s.sel(task=task)
#         except KeyError:
#             continue            

# # return a list of flat numpy traces, one per task
# def join_rqs(rqs, var_name):
#     datasets = [az.convert_to_dataset(rq)[var_name] 
#                 for rq in rqs]    
#     tasks = [np.array(get_task(datasets,  
#                                task=f"t{i+1}")).ravel() 
#              for i in range(19)]
#     return tasks

# def get_data_forest_plot(traces_dict):
#     # prepare data
#     forrest_plot_data = {}
#     forrest_plot_data[0] = {}
#     forrest_plot_data[0]['title'] = "1.Accuracy IG\n $\it{thetaIG}$"
#     forrest_plot_data[0]['traces'] = traces_dict['acc']
#     forrest_plot_data[0]['var'] = "thetaIG"
#     forrest_plot_data[0]['ref_val'] = 0.5
#     forrest_plot_data[1] = {}
#     forrest_plot_data[1]['title'] = "2.Accuracy SG\n $\it{thetaSG}$"
#     forrest_plot_data[1]['traces'] = traces_dict['acc']
#     forrest_plot_data[1]['var'] = "thetaSG"
#     forrest_plot_data[1]['ref_val'] = 0.5
#     forrest_plot_data[2] = {}
#     forrest_plot_data[2]['title'] = "3.Accuracy IG-SG\n $\it{diff\_of\_thetas}$"
#     forrest_plot_data[2]['traces'] = traces_dict['acc']
#     forrest_plot_data[2]['var'] = "difference of thetas"
#     forrest_plot_data[2]['ref_val'] = 0
# #     ####
# #     forrest_plot_data[3] = {}
# #     forrest_plot_data[3]['title'] = "Response Times IG\n $\it{groupIG\_mean}$"
# #     forrest_plot_data[3]['traces'] = traces_dict['rt']
# #     forrest_plot_data[3]['var'] = "groupIG_mean"
# #     forrest_plot_data[3]['ref_val'] = 0
# #     forrest_plot_data[4] = {}
# #     forrest_plot_data[4]['title'] = "Response Times SG\n $\it{groupSG\_mean}$"
# #     forrest_plot_data[4]['traces'] = traces_dict['rt']
# #     forrest_plot_data[4]['var'] = "groupSG_mean"
# #     forrest_plot_data[4]['ref_val'] = 0
# #     forrest_plot_data[5] = {}
# #     forrest_plot_data[5]['title'] = "Response Times IG-SG\n $\it{effect\_size}$"
# #     forrest_plot_data[5]['traces'] = traces_dict['rt']
# #     forrest_plot_data[5]['var'] = "effect size"
# #     forrest_plot_data[5]['ref_val'] = 0
# #     forrest_plot_data[6] = {}
# #     forrest_plot_data[6]['title'] = "Confidence IG\n $\it{groupIG\_mean}$"
# #     forrest_plot_data[6]['traces'] = traces_dict['conf']
# #     forrest_plot_data[6]['var'] = "groupIG_mean"
# #     forrest_plot_data[6]['ref_val'] = 0
# #     forrest_plot_data[7] = {}
# #     forrest_plot_data[7]['title'] = "Confidence SG\n $\it{groupSG\_mean}$"
# #     forrest_plot_data[7]['traces'] = traces_dict['conf']
# #     forrest_plot_data[7]['var'] = "groupSG_mean"
# #     forrest_plot_data[7]['ref_val'] = 0
# #     forrest_plot_data[8] = {}
# #     forrest_plot_data[8]['title'] = "Confidence IG-SG\n $\it{diff\_of\_means}$"
# #     forrest_plot_data[8]['traces'] = traces_dict['conf']
# #     forrest_plot_data[8]['var'] = "difference of means"
# #     forrest_plot_data[8]['ref_val'] = 0
# #     ####
#     forrest_plot_data[3] = {}
#     forrest_plot_data[3]['title'] = "4.Response Times IG-SG\n $\it{effect\_size}$"
#     forrest_plot_data[3]['traces'] = traces_dict['rt']
#     forrest_plot_data[3]['var'] = "effect size"
#     forrest_plot_data[3]['ref_val'] = 0
#     forrest_plot_data[4] = {}
#     forrest_plot_data[4]['title'] = "5.Confidence IG-SG\n $\it{diff\_of\_means}$"
#     forrest_plot_data[4]['traces'] = traces_dict['conf']
#     forrest_plot_data[4]['var'] = "difference of means"
#     forrest_plot_data[4]['ref_val'] = 0
    
#     if 'num_boxes' in traces_dict:
#         forrest_plot_data[5] = {}
#         forrest_plot_data[5]['title'] = "Num Boxes \n mu"
#         forrest_plot_data[5]['traces'] = traces_dict['num_boxes']
#         forrest_plot_data[5]['var'] = "mu"
#         forrest_plot_data[5]['ref_val'] = None

#         forrest_plot_data[6] = {}
#         forrest_plot_data[6]['title'] = "Num Boxes Obs"
#         forrest_plot_data[6]['data'] = traces_dict['num_boxes_obs']
#         forrest_plot_data[6]['ref_val'] = None

#         forrest_plot_data[7] = {}
#         forrest_plot_data[7]['title'] = "Len Boxes \n mu"
#         forrest_plot_data[7]['traces'] = traces_dict['len_boxes']
#         forrest_plot_data[7]['var'] = "mu"
#         forrest_plot_data[7]['ref_val'] = None

#         forrest_plot_data[8] = {}
#         forrest_plot_data[8]['title'] = "Len Boxes Obs"
#         forrest_plot_data[8]['data'] = traces_dict['len_boxes_obs']
#         forrest_plot_data[8]['ref_val'] = None

#     return forrest_plot_data

# def get_data_ordered_forest_plot(traces_dict):
#     # prepare data
#     forrest_plot_data = {}
#     forrest_plot_data[0] = {}
#     forrest_plot_data[0] = {}
#     forrest_plot_data[0]['title'] = "6.Accuracy IG-SG (ordered)\n $\it{diff\_of\_thetas}$"
#     forrest_plot_data[0]['traces'] = traces_dict['acc']
#     forrest_plot_data[0]['var'] = "difference of thetas"
#     forrest_plot_data[0]['ref_val'] = 0

#     forrest_plot_data[1] = {}
#     forrest_plot_data[1]['title'] = "7.Response Times IG-SG (ordered)\n $\it{effect\_size}$"
#     forrest_plot_data[1]['traces'] = traces_dict['rt']
#     forrest_plot_data[1]['var'] = "effect size"
#     forrest_plot_data[1]['ref_val'] = 0
    
#     forrest_plot_data[2] = {}
#     forrest_plot_data[2]['title'] = "8.Confidence IG-SG (ordered)\n $\it{diff\_of\_means}$"
#     forrest_plot_data[2]['traces'] = traces_dict['conf']
#     forrest_plot_data[2]['var'] = "difference of means"
#     forrest_plot_data[2]['ref_val'] = 0

#     return forrest_plot_data  

# # INTERACTION LOGS NUM OF BOXES
# def get_num_of_boxes_per_task(data, t_ids):
#     """
#         t_ids:       List of task ids ['t1','t2','t3',...]
#         Returns:     participants number of selection boxes per task {'t1':[],'t2':[],...}
#     """
#     num_boxes = {}
#     for p_id,p in data.items():        
#         if p['mode'] == "i": 
#             for t_id in t_ids: 
#                 if t_id not in num_boxes:
#                     num_boxes[t_id] = []
#                 if t_id in p['t_answers']:
#                     count = 0
#                     for i, sel in p['t_answers'][t_id]['selections'].items():
#                         count = count + 1
#                     num_boxes[t_id].append(count)
#                 else:
#                     num_boxes[t_id].append(0)
#     for t_id in num_boxes:
#         num_boxes[t_id] = np.array(num_boxes[t_id])
#     return list(num_boxes.values())

# def get_num_of_boxes_per_participant_per_task(data, t_ids):
#     """
#         t_ids:       List of task ids ['t1','t2','t3',...]
#         Returns:     participants number of selection boxes per task {'t1':[],'t2':[],...}
#     """
#     num_boxes = {}
#     for p_id,p in data.items():        
#         if p['mode'] == "i": 
#             if p_id not in num_boxes:
#                 num_boxes[p_id] = {}
#             for t_id in t_ids: 
#                 if t_id not in num_boxes[p_id]:
#                     num_boxes[p_id][t_id] = []
#                 if t_id in p['t_answers']:
#                     count = 0
#                     for i, sel in p['t_answers'][t_id]['selections'].items():
#                         count = count + 1
#                     num_boxes[p_id][t_id] = count
#                 else:
#                     num_boxes[p_id][t_id] = 0
#     return num_boxes

# # INTERACTION LOGS LENGTH OF BOXES
# def get_len_of_boxes_per_task(data, p_tasks, p_vars, p_inference):
#     """
#         t_ids:       List of task ids ['t1','t2','t3',...]
#         Returns:     participants number of selection boxes per task {'t1':[],'t2':[],...}
#     """
#     ## estimate normalization factor of each variable in each problem
#     p_norm_factors = {}   
#     for p, inference in p_inference.items():
#         inf_dat = json.loads(inference['header.json'])["inference_data"]
#         if p not in p_norm_factors:
#             p_norm_factors[p] = {}
#         for var in p_vars[p]:
#             if var in inf_dat['prior']['vars']:
#                 p_array_names = inf_dat['prior']["array_names"]
#             elif var in inf_dat['prior_predictive']['vars']:
#                 p_array_names = inf_dat['prior_predictive']["array_names"]
#             prior_samples = np.squeeze(inference[p_array_names[var]])
#             if p == 'p3' and len(prior_samples.shape)>1:
#                 prior_samples = prior_samples[:,2]
#             max_v = prior_samples.max()
#             min_v = prior_samples.min()
#             diff = max_v - min_v
#             p_norm_factors[p][var] =  (max_v+0.1*diff) - (min_v - 0.1*diff)
# #             hdi = az.hdi(prior_samples, hdi_prob=.94)
# #             p_norm_factors[p][var] =  hdi[1] - hdi[0]
#     len_boxes = {}
#     for p_id,p in data.items():        
#         if p['mode'] == "i": 
#             for prob in p_tasks:
#                 for t_id in p_tasks[prob]: 
#                     if t_id not in len_boxes:
#                         len_boxes[t_id] = []
#                     if t_id in p['t_answers']:
#                         for i, sel in p['t_answers'][t_id]['selections'].items():
#                             len_boxes[t_id].append((sel['xmax']-sel['xmin'])/p_norm_factors[prob][sel["var_name"]])
#                     else:
#                         len_boxes[t_id].append(0.)
#     for t_id in len_boxes:
#         len_boxes[t_id] = np.array(len_boxes[t_id])
#     return list(len_boxes.values())