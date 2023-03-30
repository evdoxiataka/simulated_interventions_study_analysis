import pymc3 as pm
import numpy as np

def get_times_inference(times_i, times_s, times_a, t_indices_i, t_indices_s, t_indices_a, t_ids):
    """
        times: pandas dataframe
    """
    coords = {"task": t_ids}
    with pm.Model(coords=coords) as model:
        ## priors
        groupIG_mean = pm.Normal("groupIG_mean", mu = 120, sd = 50, dims = 'task')
        groupIG_std = pm.HalfNormal("groupIG_std", sd = 50, dims = 'task')
        
        groupSG_mean = pm.Normal("groupSG_mean", mu = 120, sd = 50, dims = 'task')        
        groupSG_std = pm.HalfNormal("groupSG_std", sd = 50, dims = 'task')
        
        groupAG_mean = pm.Normal("groupAG_mean", mu = 120, sd = 50, dims = 'task')        
        groupAG_std = pm.HalfNormal("groupAG_std", sd = 50, dims = 'task')

        ## likelihood  
        rtIG = pm.Normal("rtIG", mu = groupIG_mean[t_indices_i], sd = groupIG_std[t_indices_i], observed = times_i)# sec
        rtSG = pm.Normal("rtSG", mu = groupSG_mean[t_indices_s], sd = groupSG_std[t_indices_s], observed = times_s)# sec
        rtAG = pm.Normal("rtAG", mu = groupAG_mean[t_indices_a], sd = groupAG_std[t_indices_a], observed = times_a)# sec
        
        ## comparisons
        diff_of_means_IG_SG = pm.Deterministic("difference of means IG-SG", groupIG_mean - groupSG_mean, dims = 'task')
        effect_size_IG_SG = pm.Deterministic("effect size IG-SG", diff_of_means_IG_SG / np.sqrt((groupIG_std ** 2 + groupSG_std ** 2) / 2), dims = 'task')
        
        diff_of_means_IG_AG = pm.Deterministic("difference of means IG-AG", groupIG_mean - groupAG_mean, dims = 'task')
        effect_size_IG_AG = pm.Deterministic("effect size IG-AG", diff_of_means_IG_AG / np.sqrt((groupIG_std ** 2 + groupAG_std ** 2) / 2), dims = 'task')
        
        diff_of_means_SG_AG = pm.Deterministic("difference of means SG-AG", groupSG_mean - groupAG_mean, dims = 'task')
        effect_size_SG_AG = pm.Deterministic("effect size SG-AG", diff_of_means_SG_AG / np.sqrt((groupSG_std ** 2 + groupAG_std ** 2) / 2), dims = 'task')
        
        #inference
        trace = pm.sample(2000)
        posterior_predictive = pm.sample_posterior_predictive(trace, samples=2000)
    return trace, posterior_predictive

def get_confidence_inference(conf_i, conf_s, conf_a, t_indices_i, t_indices_s, t_indices_a, t_ids):
    """
        times: pandas dataframe
    """
    coords = {"task": t_ids}
    with pm.Model(coords=coords) as model:
        ## priors
        groupIG_mean = pm.Normal("groupIG_mean", mu = 0, sd = 1, dims = 'task')
        groupIG_std = pm.HalfNormal("groupIG_std", sd = 1, dims = 'task')
        
        groupSG_mean = pm.Normal("groupSG_mean", mu = 0, sd = 1, dims = 'task')        
        groupSG_std = pm.HalfNormal("groupSG_std", sd = 1, dims = 'task')
        
        groupAG_mean = pm.Normal("groupAG_mean", mu = 0, sd = 1, dims = 'task')        
        groupAG_std = pm.HalfNormal("groupAG_std", sd = 1, dims = 'task')

        ## likelihood  
        confIG = pm.Normal("confIG", mu = groupIG_mean[t_indices_i], sd = groupIG_std[t_indices_i], observed = conf_i)# sec
        confSG = pm.Normal("confSG", mu = groupSG_mean[t_indices_s], sd = groupSG_std[t_indices_s], observed = conf_s)# sec
        confAG = pm.Normal("confAG", mu = groupAG_mean[t_indices_a], sd = groupAG_std[t_indices_a], observed = conf_a)# sec
        
        ## comparisons
        diff_of_means_IG_SG = pm.Deterministic("difference of means IG-SG", groupIG_mean - groupSG_mean, dims = 'task')
        effect_size_IG_SG = pm.Deterministic("effect size IG-SG", diff_of_means_IG_SG / np.sqrt((groupIG_std ** 2 + groupSG_std ** 2) / 2), dims = 'task')
        
        diff_of_means_IG_AG = pm.Deterministic("difference of means IG-AG", groupIG_mean - groupAG_mean, dims = 'task')
        effect_size_IG_AG = pm.Deterministic("effect size IG-AG", diff_of_means_IG_AG / np.sqrt((groupIG_std ** 2 + groupAG_std ** 2) / 2), dims = 'task')
        
        diff_of_means_SG_AG = pm.Deterministic("difference of means SG-AG", groupSG_mean - groupAG_mean, dims = 'task')
        effect_size_SG_AG = pm.Deterministic("effect size SG-AG", diff_of_means_SG_AG / np.sqrt((groupSG_std ** 2 + groupAG_std ** 2) / 2), dims = 'task')
        ## inference
        trace = pm.sample(2000)
        posterior_predictive = pm.sample_posterior_predictive(trace, samples=2000)
    return trace, posterior_predictive

def get_inference_categ(answers_i, answers_s, answers_a, t_indices_i, t_indices_s, t_indices_a, t_ids):
    """
        answers_i: List of success for all tasks in rq1 for all interactive participants
        n:         List of trials size (number of available options) per task in rq1
        t_indices: List of indexes to rq1 tasks for all observations in answers_i or answers_s
        t_ids:     List of Strings with tasks ids
    """    
    coords = {"task": t_ids}
    with pm.Model(coords=coords) as model:
        #priors
        pIG = pm.Dirichlet("pIG", a=np.array([0.5,0.5,0.5]), dims = 'task')#probability of correct choice
        pSG = pm.Dirichlet("pSG", a=np.array([0.5,0.5,0.5]), dims = 'task')
        pAG = pm.Dirichlet("pAG", a=np.array([0.5,0.5,0.5]), dims = 'task')

        #likelihood        
        accuracyIG = pm.Categorical("accuracyIG", p = pIG[t_indices_i], observed = answers_i)
        accuracySG = pm.Categorical("accuracySG", p = pSG[t_indices_s], observed = answers_s)
        accuracyAG = pm.Categorical("accuracyAG", p = pAG[t_indices_a], observed = answers_a)
        
        #comparisons
        # diff_of_thetas_IG_SG = pm.Deterministic("difference of thetas IG-SG", thetaIG - thetaSG, dims='task')
        # diff_of_thetas_IG_AG = pm.Deterministic("difference of thetas IG-AG", thetaIG - thetaAG, dims='task')
        # diff_of_thetas_SG_AG = pm.Deterministic("difference of thetas SG-AG", thetaSG - thetaAG, dims='task')
       
        #inference
        trace = pm.sample(2000)
        posterior_predictive = pm.sample_posterior_predictive(trace, samples=2000)
    return trace, posterior_predictive

def get_inference_multi(answers_i, answers_s, answers_a, n_i, n_s, n_a, t_indices_i, t_indices_s, t_indices_a, t_ids):
    """
        answers_i: List of success for all tasks in rq1 for all interactive participants
        n:         List of trials size (number of available options) per task in rq1
        t_indices: List of indexes to rq1 tasks for all observations in answers_i or answers_s
        t_ids:     List of Strings with tasks ids
    """    
    coords = {"task": t_ids}
    with pm.Model(coords=coords) as model:
        #priors
        thetaIG = pm.Beta("thetaIG", alpha = 1.0, beta = 1.0, dims = 'task')#probability of correct choice
        thetaSG = pm.Beta("thetaSG", alpha = 1.0, beta = 1.0, dims = 'task')
        thetaAG = pm.Beta("thetaAG", alpha = 1.0, beta = 1.0, dims = 'task')

        #likelihood        
        accuracyIG = pm.Binomial("accuracyIG", n = n_i, p = thetaIG[t_indices_i], observed = answers_i)
        accuracySG = pm.Binomial("accuracySG", n = n_s, p = thetaSG[t_indices_s], observed = answers_s)
        accuracyAG = pm.Binomial("accuracyAG", n = n_a, p = thetaAG[t_indices_a], observed = answers_a)
        
        #comparisons
        diff_of_thetas_IG_SG = pm.Deterministic("difference of thetas IG-SG", thetaIG - thetaSG, dims='task')
        diff_of_thetas_IG_AG = pm.Deterministic("difference of thetas IG-AG", thetaIG - thetaAG, dims='task')
        diff_of_thetas_SG_AG = pm.Deterministic("difference of thetas SG-AG", thetaSG - thetaAG, dims='task')
       
        #inference
        trace = pm.sample(2000)
        posterior_predictive = pm.sample_posterior_predictive(trace, samples=2000)
    return trace, posterior_predictive

def get_inference_multi_conf(answers_i, answers_s, answers_a, conf_i, conf_s, conf_a, n_i, n_s, n_a, t_indices_i, t_indices_s, t_indices_a, t_ids):
    """
        answers_i: List of success for all tasks in rq1 for all interactive participants
        n:         List of trials size (number of available options) per task in rq1
        t_indices: List of indexes to rq1 tasks for all observations in answers_i or answers_s
        t_ids:     List of Strings with tasks ids
    """    
    coords = {"task": t_ids}
    with pm.Model(coords=coords) as model:
        ##
        c_i = pm.Data('c_i', conf_i)
        c_s = pm.Data('c_s', conf_s)
        c_a = pm.Data('c_a', conf_a)
        #priors
#         pIG = pm.Beta("pIG", alpha = 1.0, beta = 1.0, dims = 'task')#probability of correct choice
#         pSG = pm.Beta("pSG", alpha = 1.0, beta = 1.0, dims = 'task')
#         pAG = pm.Beta("pAG", alpha = 1.0, beta = 1.0, dims = 'task')
#         k0 = pm.Normal("k0", mu = 0, sd = 20)
#         k1 = pm.Normal("k1", mu = 0, sd = 20)
        
#         thetaIG = pm.Deterministic("thetaIG",pIG[t_indices_i] * pm.math.sigmoid(k1 * c_i[t_indices_i] + k0), dims='task')
#         thetaSG = pm.Deterministic("thetaSG",pSG[t_indices_s] * pm.math.sigmoid(k1 * c_s[t_indices_s] + k0), dims='task')
#         thetaAG = pm.Deterministic("thetaAG",pAG[t_indices_a] * pm.math.sigmoid(k1 * c_a[t_indices_a] + k0), dims='task')
#         #likelihood        
#         accuracyIG = pm.Binomial("accuracyIG", n = n_i, p = thetaIG[t_indices_i], observed = answers_i)
#         accuracySG = pm.Binomial("accuracySG", n = n_s, p = thetaSG[t_indices_s], observed = answers_s)
#         accuracyAG = pm.Binomial("accuracyAG", n = n_a, p = thetaAG[t_indices_a], observed = answers_a)
        thetaIG = pm.Beta("thetaIG", alpha = 1.0, beta = 1.0, dims = 'task')#probability of correct choice
        thetaSG = pm.Beta("thetaSG", alpha = 1.0, beta = 1.0, dims = 'task')
        thetaAG = pm.Beta("thetaAG", alpha = 1.0, beta = 1.0, dims = 'task')
        k0 = pm.Normal("k0", mu = 0, sd = 20)
        k1 = pm.Normal("k1", mu = 0, sd = 20)
        
        # thetaIG = pm.Deterministic("thetaIG",pIG[t_indices_i] * pm.math.sigmoid(k1 * c_i[t_indices_i] + k0), dims='task')
        # thetaSG = pm.Deterministic("thetaSG",pSG[t_indices_s] * pm.math.sigmoid(k1 * c_s[t_indices_s] + k0), dims='task')
        # thetaAG = pm.Deterministic("thetaAG",pAG[t_indices_a] * pm.math.sigmoid(k1 * c_a[t_indices_a] + k0), dims='task')
        #likelihood        
        accuracyIG = pm.Binomial("accuracyIG", n = n_i, p = thetaIG[t_indices_i]* pm.math.sigmoid(k1 * c_i[t_indices_i] + k0), observed = answers_i)
        accuracySG = pm.Binomial("accuracySG", n = n_s, p = thetaSG[t_indices_s]* pm.math.sigmoid(k1 * c_s[t_indices_s] + k0), observed = answers_s)
        accuracyAG = pm.Binomial("accuracyAG", n = n_a, p = thetaAG[t_indices_a]* pm.math.sigmoid(k1 * c_a[t_indices_a] + k0), observed = answers_a)
        
        #comparisons
        diff_of_thetas_IG_SG = pm.Deterministic("difference of thetas IG-SG", thetaIG - thetaSG, dims='task')
        diff_of_thetas_IG_AG = pm.Deterministic("difference of thetas IG-AG", thetaIG - thetaAG, dims='task')
        diff_of_thetas_SG_AG = pm.Deterministic("difference of thetas SG-AG", thetaSG - thetaAG, dims='task')
       
        #inference
        trace = pm.sample(2000)
        posterior_predictive = pm.sample_posterior_predictive(trace, samples=2000)
    return trace, posterior_predictive

def get_inference_sinlg(answers_i, answers_s, answers_a, t_indices_i, t_indices_s, t_indices_a, t_ids):
    """
        answers_i: List of success for all tasks in rq2 or rq3 for all interactive participants
        t_ids: List of Strings with tasks ids
    """    
    coords = {"task": t_ids}
    with pm.Model(coords=coords) as model:
        #priors
        thetaIG = pm.Beta("thetaIG", alpha = 1.0, beta = 1.0, dims = 'task')#probability of correct choice
        thetaSG = pm.Beta("thetaSG", alpha = 1.0, beta = 1.0, dims = 'task')
        thetaAG = pm.Beta("thetaAG", alpha = 1.0, beta = 1.0, dims = 'task')

        #likelihood        
        accuracyIG = pm.Bernoulli("accuracyIG", p = thetaIG[t_indices_i], observed = answers_i)
        accuracySG = pm.Bernoulli("accuracySG", p = thetaSG[t_indices_s], observed = answers_s)
        accuracyAG = pm.Bernoulli("accuracyAG", p = thetaAG[t_indices_a], observed = answers_a)
        
        #comparisons
        diff_of_thetas_IG_SG = pm.Deterministic("difference of thetas IG-SG", thetaIG - thetaSG, dims='task')
        diff_of_thetas_IG_AG = pm.Deterministic("difference of thetas IG-AG", thetaIG - thetaAG, dims='task')
        diff_of_thetas_SG_AG = pm.Deterministic("difference of thetas SG-AG", thetaSG - thetaAG, dims='task')
        
        #inference
        trace = pm.sample(2000)
        posterior_predictive = pm.sample_posterior_predictive(trace, samples=2000)
    return trace, posterior_predictive

def get_inference_sinlg_part(answers, t_indices, t_ids):
    """
        answers_i: List of success for all tasks in rq2 or rq3 for all interactive participants
        t_ids: List of Strings with tasks ids
    """    
    coords = {"participant_id": t_ids}
    with pm.Model(coords=coords) as model:
        #priors
        theta = pm.Beta("theta", alpha = 1.0, beta = 1.0, dims = 'participant_id')#probability of correct choice

        #likelihood        
        accuracy = pm.Bernoulli("accuracy", p = theta[t_indices], observed = answers)
        
        #inference
        trace = pm.sample(2000)
        posterior_predictive = pm.sample_posterior_predictive(trace, samples=2000)
    return trace, posterior_predictive

def get_len_boxes_inference(len_boxes, t_ids,  t_indices):
    """
        len_boxes:    List of length of selectin box for each participant and variable in each task
        t_ids:        List of task ids e.g. t1, t2, t3 ....
        t_indices:    List of indices to task ids for each observation in len_boxes
    """    
    coords = {"task": t_ids}
    with pm.Model(coords=coords) as model:
        #priors
        mu = pm.Normal("mu", mu = 0, sigma = 10, dims='task')
        sigma = pm.HalfNormal("sigma", sd = 10, dims='task')

        #likelihood                
        len_box = pm.Normal("len_box", mu = mu[t_indices], sigma = sigma[t_indices], observed = len_boxes)#length of selection box

        #inference
        trace = pm.sample(2000)
        posterior_predictive = pm.sample_posterior_predictive(trace, samples=2000)
    return trace, posterior_predictive

def get_num_boxes_inference(num_boxes, t_ids,  t_indices):
    """
        num_boxes:    List of number of selectin boxes for each variable in each task
        t_ids:        List of task ids e.g. t1, t2, t3 ....
        t_indices:    List of indices to task ids for each observation in num_boxes
    """    
    coords = {"task": t_ids}
    with pm.Model(coords=coords) as model:
        #priors
        psi = pm.Beta("psi", alpha = 1, beta = 1, dims='task')
        mu = pm.Gamma("mu", alpha = 1, beta = 30, dims='task')

        #likelihood                
        num_box = pm.ZeroInflatedPoisson("num_box", theta = mu[t_indices], psi = psi[t_indices], observed = num_boxes)#number of selection boxes

        #inference
        trace = pm.sample(2000)
        posterior_predictive = pm.sample_posterior_predictive(trace, samples=2000)
    return trace, posterior_predictive