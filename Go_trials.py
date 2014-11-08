# -*- coding: utf-8 -*-
"""
Created on Thu Oct 16 10:48:19 2014

@author: Hayley
"""

import numpy as np
from scipy import stats
import scipy.optimize as opt
import matplotlib.pyplot as plt

def get_fac(t, params):
    '''
    Generates a facilitation curve
    
    Parameters
    ----------
    t : array
        sequence of time index
    params : sequence (3,) of float
        k_facGo - scale of fac curve
        tau_facGo - curvature of fac curve
        pre_t - start time before target presentation
        
    Returns
    -------
    res : array
        fac curve values at times `t`
    '''
    k_facGo, tau_facGo, pre_t = params
    res = np.zeros_like(t)
    fac = 1/k_facGo * ((t + pre_t) - tau_facGo * (1 - np.exp(-(t + pre_t)/tau_facGo)))
    idx = (t + pre_t) >= 0
    res[idx] = fac[idx]
    return res
        
def get_trials(params, n_rep=10000):
    '''
    Generates n_rep number of facilitation curves for Go response for all simulated trials required
    
    Parameters
    -------------
    params : sequence (3,) of float
        k_facGo - scale of fac curve
        pre_t_mean - average start time before target presentation
        pre_t_sd - standard deviation of start time before target
        
        Returns
        --------
        fac_i : array
            facilitation curves for all simulated trials
        t : array
            sequence of time index
    '''
    k_facGo, pre_t_mean, pre_t_sd, tau_facGo = params 
    t = np.linspace(-.4, .2, 600, endpoint=False)  # How does this work if pre_t not optimized at -4?
#    tau_facGo = 2  # Currently set, but will need to optomize
    pre_t = np.random.normal(pre_t_mean, pre_t_sd, size=n_rep) # generates n_rep random numbers from a normal distribution of mean, sd that given into function
    fac_i = np.zeros((n_rep, t.size))  # sets up empty array of zeros for all simulated trials
    for i in range(n_rep):  # for each simulated trial
        myparams = k_facGo, tau_facGo, pre_t[i]  # takes parameters passed into model plus pre_t number randomly generated for that simulated trial
        fac_i[i] = get_fac(t, myparams)  # generates curve for that simulated trial
    return fac_i, t
    
def get_fac_tms_vals(t, fac_i, pts=(-.15, -.125, -.1)):
    '''
    Gets values at pre-defined time points on all simulated fac curves
    
    Parameters 
    -------------
    pts : sequence of floats
        time points for comparison to MEP amplitude values from exp data
        
    Returns
    -------------
    vals : value on all simulated curves at time point requested
    '''
    idx150 = np.flatnonzero(np.isclose(t, pts[0]))
    vals150 = fac_i[:,idx150]
    idx125 = np.flatnonzero(np.isclose(t, pts[1]))
    vals125 = fac_i[:,idx125]
    idx100 = np.flatnonzero(np.isclose(t, pts[2]))
    vals100 = fac_i[:,idx100]
    return (vals150, vals125, vals100)  # is this causing the error?
    
def get_chisquare(obs_data, obs_model, nbins=3):
    '''
    Sends into function actual MEP amplitude data at each time point, predicted
    amplitudes from simulated facilitation curves, number of bins to divide
    percentile bins into. Calculates histograms for experimental and predicted
    data. Compares frequencies in each bin. Calculates one-way chi square test.
    
    Parameters
    --------------
    obs_data : array of MEP amplitudes from experimental data
    obs_model : predicted MEP amplitudes from simulated trials (i.e. facilitation curves)
    
    Returns
    ---------------
    chi square statistic for how well predicted data matches experimental data
    
    '''
    percentile_bins = np.linspace(0, 100, nbins + 1)    
    bin_edges = np.percentile(obs_data, list(percentile_bins))
    hist_data, bin_edges  = np.histogram(obs_data,  bins=bin_edges)
    hist_data = hist_data / float(obs_data.size)
    # put in density so that value for each bin is expressed as proportion of total number of observations
    hist_model, bin_edges = np.histogram(obs_model, bins=bin_edges)
    hist_model = hist_model / float(obs_model.size)
    return stats.chisquare(hist_data, hist_model)

def load_exp_data(fname):
    file_contents = np.genfromtxt(fname, dtype=float, delimiter=",", skiprows=1)  # loads the csv file as a float, skipping the first row as only subject codes
    MEP_amps_mV  = file_contents.flatten()
    no_nan_MEP_amps_mV = MEP_amps_mV[~np.isnan(MEP_amps_mV)] # Creates array of True False for whether is NaN - then indexes out of MEP_amps_mV array only with corresponding returned True
    return no_nan_MEP_amps_mV

def error_function(params, data150, data125, data100):  #
#    data150, data125, data100 = data 
    print "Trying with values: " + str(params)
    fac_i, t = get_trials(params)  # n_rep=data.size
    pred150, pred125, pred100 = get_fac_tms_vals(t, fac_i)
    X2_150 = get_chisquare(data150, pred150, nbins=2)[0]
    print "X2_150: ", X2_150
    X2_125 = get_chisquare(data125, pred125, nbins=2)[0]
    print "X2_125: ", X2_125
    X2_100 = get_chisquare(data100, pred100, nbins=2)[0]
    print "X2_100: ", X2_100
    X2_summed = X2_150 + X2_125 + X2_100
    print "X2 summed: ", X2_summed
    return X2_summed # (X2_150, X2_125, X2_100)

def visualize_params(params, data):
    data150, data125, data100 = data
    fac_i, t = get_trials(params)
    plt.plot(t, fac_i.T, 'k-', alpha=0.4)
    plt.plot(np.ones_like(data150) * -0.15, data150, 'rx')
    plt.plot(np.ones_like(data125) * -0.125, data125, 'rx')
    plt.plot(np.ones_like(data100) * -0.100, data100, 'rx')
    
data_dir = 'C:\Users\Hayley\Documents\University\PhD\PhD\Modeling\Experimental data for model'
fname150 = data_dir + '\Go_trial_MEP_amplitudes_150ms.csv'
fname125 = data_dir + '\Go_trial_MEP_amplitudes_125ms.csv'
fname100 = data_dir + '\Go_trial_MEP_amplitudes_100ms.csv'
exp_MEPs_150 = load_exp_data(fname150)
exp_MEPs_125 = load_exp_data(fname125)
exp_MEPs_100 = load_exp_data(fname100)
#exp_data_all_points = (exp_MEPs_150, exp_MEPs_125, exp_MEPs_100)

if __name__ == "__main__":  
    optobj = opt.minimize(error_function, [0.06, 0.4, 0.1, 2], args=(exp_MEPs_150, exp_MEPs_125, exp_MEPs_100), method='Nelder-Mead') #method="SLSQP", bounds=[(0,None),(0,None),(0,None),(None,None)])  
