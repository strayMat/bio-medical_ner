# Utils to extract inforamtions from logs and present them
from tqdm import tqdm
import re
import os
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 

from confUtils import read_conf

# Dataframe construction functions

def get_results(path2xpDir):
    ''' Read a yaset result directory and collect all relevant informations in it
    input: result directory path
    output: dictionnary (thought as json format) returning all relevant informations about the experience
    '''
    reg_dir = re.compile('yaset-learn-(.*)-(\d\d*)-(\d\d*)')
    reg = reg_dir.search(path2xpDir)
    try:
        # general folder information
        xp_name = str(reg.group(1))
        start_date = int(reg.group(2))
    except AttributeError:
        print('Not a valid yaset result directory !')
        return
    
    dic = {}
    # read log
    log_path = path2xpDir+'/yaset-learn-'+reg.group(2)+'-'+reg.group(3)+'.log'
    log_infos = read_log(log_path)
    if log_infos is not None:
        for k, v in log_infos.items():
            dic[k] = v
        dic['complete'] = True
    else:
        return None
    dic['xp name'] = xp_name
    dic['beginning date'] = start_date
    dic['beginning time'] = int(reg.group(3))
    
    # read config file
    conf = read_conf(path2xpDir+'/config.ini', verbose = False)
    # extract all relevant hyperparameters from conf file
    hyper_params = {}
    # numerics
    hyper_params['patience'] = np.int(conf['patience'])
    hyper_params['dropout_rate'] = np.float(conf['dropout_rate'])
    hyper_params['char_hidden_layer_size'] = np.int(conf['char_hidden_layer_size'])
    hyper_params['char_embedding_size'] = np.int(conf['char_embedding_size'])
    hyper_params['hidden_layer_size'] = np.int(conf['hidden_layer_size'])
    hyper_params['cpu_cores'] = np.int(conf['cpu_cores'])
    # booleans
    hyper_params['word_emb_train'] = str2bool(conf['trainable_word_embeddings'])
    hyper_params['opt_decay_use'] = str2bool(conf['opt_decay_use'])
    hyper_params['feature_data'] = str2bool(conf['feature_data'])
    # get the word embedding dimension
    if os.path.isfile(path2xpDir+'/data_char.json'):
        with open(path2xpDir+'/data_char.json', 'r') as f:
            word_emb_dim = json.load(f)['embedding_matrix_shape'][1]
    hyper_params['word_emb_dim'] = word_emb_dim
    
    # add hyper parameters dict to json 
    dic['hyper parameters'] = hyper_params
    #json_file = json.dump(dic)
    return(dic)


def read_log(path2log, verbose = False, warnings = True):
    ''' Read a yaset log file and extract relevant informations for results analysis
    return dictionnary or None if uncomplete logs
    '''
    infos = {}
    precisions = []
    recalls = []
    f1s = []
    complete = False
    iterations = []
    tokens = []
    iteration = 1
    it_time = '00:00:00'
    with open(path2log, 'r') as f:
        for line in f:
            #print(line)
            reg = re.search('CoNLL \(Overall\)\: precision=(\d\d*\.\d\d)\%\, recall=(\d\d*\.\d\d)\%\, f1-measure=(\d\d*\.\d\d)\%',
                       str(line))
            tmp_time = re.search('----- END - Iteration \#(\d\d*) \(Time elapsed\: (\d\:\d\d\:\d\d)', str(line))
            if tmp_time is not None:
                it_time = tmp_time.group(2)
            
            nb_tokens = re.search('nb\. tokens \(col\. \#0\): (\d{1,3}(,\d{3})*) ', str(line))
            if nb_tokens is not None:
                tokens.append(np.int(nb_tokens.group(1).replace(',', '')))
                
            if reg is not None:
                precisions.append(reg.group(1))
                recalls.append(reg.group(2))
                f1s.append(reg.group(3))
                iterations.append(tuple((iteration, np.float(reg.group(1)), np.float(reg.group(2)), np.float(reg.group(3)), it_time)))
                #print(iteration)
                iteration += 1
                  
            tmp_comp = re.search('END - LEARNING MODEL \#', line)
            if tmp_comp is not None:
                complete = True
            timed = re.search('Time elapsed\: (\d\:\d\d\:\d\d)', line)
            if timed is not None:
                infos['time elapsed'] = timed.group(1)
                
    if not complete:
        if warnings:print('WARNING : Not complete experiment for {}!'.format(path2log))
        return None
    
    best_ix = np.argmax(f1s)
    precision = np.float(precisions[best_ix])
    recall = np.float(recalls[best_ix])
    f1 = np.float(f1s[best_ix])
    
    infos['iterations'] = iterations
    infos['score'] = iterations[best_ix]
    infos['nb train tokens'] = tokens[0]
    if len(tokens) > 1:
        infos['nb dev tokens'] = tokens[1]
    if verbose:
        print('experiment {}'.format(path2log))
        print(infos)
    return infos


def build_jsons(path2xps, path2store, show_path = False):
    ''' A json warper on top of get_result: searches in a given directory all yaset experiment folders and output a json with relevant informations 
    '''
    nb_xps = 0
    for f in tqdm(os.listdir(path2xps)):
        if re.search('yaset-learn-(.*)-(\d\d*)-(\d\d*)', f) is not None:
            tmp_json = get_results(path2xps+f)
            # ignore the uncomplet experiences
            if tmp_json is None:
                pass
            else:
                xp_name = tmp_json['xp name']+'-'+str(tmp_json['beginning date'])+'-'+str(tmp_json['beginning time'])
                with open(path2store + xp_name, 'w') as ff:
                    json.dump(tmp_json, ff)
                nb_xps += 1
            if show_path:
                print(f + ' | fscore = {}'.format(tmp_json['score'][3]))
    print('Collected {} xperiences in {} and stored all in {}'.format(nb_xps, path2xps, path2store))
    return 



def str2bool(st):
    ''' Convert boolean string to python boolean, needed in get_results
    '''
    if st == 'true':
        return True
    elif st == 'false':
        return False
    else:
        return st
    
    
def json2pandas(path2json_dir, verbose = True, trajs = False, fixed_iter = None):
    ''' Read jsons files built with build_jsons and return them as a pandas dataframe for further exploration
    '''
    reg = re.compile('(\d\d*)\:(\d\d)\:(\d\d)')
    modelpath = os.listdir(path2json_dir)[0]
    with open(path2json_dir + modelpath, 'r') as f:
        model = json.load(f)
    if verbose:
        print('json format for analysis')
        print(model)
    hyper_df = pd.DataFrame(columns=list(model['hyper parameters'].keys()) + 
                        ['nb_iter', 'best_iter', 'precision', 'recall', 'f1'])
    for f in os.listdir(path2json_dir):
        with open(path2json_dir+f, 'r') as ff:
            tmp_json = json.load(ff)
            cols = []
            values = []
            df = tmp_json['hyper parameters'].copy()
            df['nb_train_tokens'] = tmp_json['nb train tokens']
            #df['nb_test_tokens'] = tmp_json['nb test tokens']
            df['best_iter'] = tmp_json['score'][0]
            if fixed_iter is not None:
                df['nb_iter'] = min(fixed_iter, len(tmp_json['iterations']))
                # if fixed iter is defined, take the scores at this iteration
                df['precision'] = tmp_json['iterations'][df['nb_iter']-1][1]
                df['recall'] = tmp_json['iterations'][df['nb_iter']-1][2]
                df['f1'] = tmp_json['iterations'][df['nb_iter']-1][3]
            else: # of no fixed iterations, we take nb_iter as the best iter + the patience and we take the best scores
                df['nb_iter'] = len(tmp_json['iterations'])
                df['precision'] = tmp_json['score'][1]
                df['recall'] = tmp_json['score'][2]
                df['f1'] = tmp_json['score'][3]
                
            if trajs:
                df['traj'] = np.array([np.array([e[0] for e in tmp_json['iterations']]), np.array([e[3] for e in tmp_json['iterations']])])
                iter_times = []
                for e in tmp_json['iterations']:
                    reg_iter_time = reg.search(e[4])
                    if reg_iter_time is not None:
                        iter_times.append(int(reg_iter_time.group(1))*3600 + int(reg_iter_time.group(2))*60 + int(reg_iter_time.group(3)))
                df['mean_iter_time_s'] = int(np.mean(iter_times))
            reg_time = reg.search(tmp_json['time elapsed'])
            #print(tmp_json['time elapsed'])
            if reg_time is not None:
                df['time_elapsed'] = int(reg_time.group(1))*60 + int(reg_time.group(2))
                #df['time_elapsed'] = tmp_json['time elapsed']
            else:
                df['time_elapsed'] = np.nan
            for k, v in df.items():
                tmp = []
                tmp.append(v)
                df[k] = tmp
            df = pd.DataFrame.from_dict(df)
        hyper_df = hyper_df.append(df, sort = True)
    if verbose:
        print('Loaded {} jsons succesfully!'.format(hyper_df.shape[0]))
    return hyper_df

# Plot functions

def plot_traj(traj_list, alpha = 0.3, c = 'C0', label = ''):
    ''' Plot the training progression from a list of trajectories that can be extracted from yaset log files (just turn trajs = True in json2pandas)
    '''
    for traj in traj_list:
        plt.plot(traj[0], traj[1], c = c, alpha = alpha, label = label)
    return

def avg_traj(traj_list, plot = True, legend = '', fixed_iter = None):
    ''' Plot the average of a list of trajectories (same sthing as plot_traj but compress information by averaging)
    '''
    max_len = np.max([le.shape[1] for le in traj_list])
    count = np.zeros(max_len) 
    mean = np.zeros(max_len)
    
    for traj in traj_list:
        for i, e in enumerate(traj[1]):
            mean[i] += e
            count[i] +=1
    mean = mean/count     
    if plot == True:
        if fixed_iter is not None:
            plt.plot(np.arange(max_len)[:fixed_iter]+1, mean[:fixed_iter], label = legend)
        else:
            plt.plot(np.arange(max_len)+1, mean, label = legend)
        
    return np.array([np.arange(max_len)+1, mean])


def plot_results(df,
                 crit_str = 'f1s', 
                 verbose = True,
                 get_results = False,
                 log_scale = False,
                 save = None):
    nb_tokens = max(df['nb_train_tokens'])
    ''' plot the curve of score progression against data size when nourished with pandas experiences results
    input:  df, the dataframe containing the results extracted from the jsons result summaries
            criter, string in ['precisions', 'recalls', f1s'], default is 'f1s'
            verbose, true to plot some additional iinformations on the xps (number of experiment for each chunk, etc..)
            get_results, true to return the scores in addition to the plot 
            log_scale, true to add a logscale on the curve
    output: token (or ratio) counts, mean of the criter 
    '''
    precisions = {}
    recalls = {}
    f1s = {}
    ratios = [int(e) for e in df['nb_train_tokens'].value_counts().keys()]
    
    for r in ratios:
        precisions[r] = list(df[df['nb_train_tokens'] == r]['precision'])
        f1s[r] = list(df[df['nb_train_tokens'] == r]['f1'])
        recalls[r] = list(df[df['nb_train_tokens'] == r]['recall'])
    # sort the keys of the criters
    ratios = [int(i) for i in list(f1s.keys())]
    ratios.sort()
    # convert percentage of data to real counts of token
    counts = np.array(ratios)
    # chose the critere
    criter = eval(crit_str)
    
    # plot criter performance
    means = []
    sd_1 = []
    for perc in ratios:
        means.append(np.mean(criter[perc]))
        sd_1.append(np.std(criter[perc]))
    
    if verbose:
        fig, ax1 = plt.subplots(figsize = (20,5))
        nb_experiments = []
        for r,c in zip(ratios, counts):
            nb_experiments+=np.repeat(c, len(criter[r])).tolist()
        ax1.hist(nb_experiments, bins = 50)
        plt.title('Number of experiments for each train chunk')
        # plot the std on top of the experiments counts
        ax2 = ax1.twinx()
        ax2.scatter(counts, sd_1, s = 80, color = 'C1', label = 'standard deviation on f1')
        plt.legend()
        plt.xticks(counts, rotation = 40)
        plt.show()
        # Boxplot
        toBox = []
        for r in ratios:
            toBox.append(criter[r])
        fig, ax = plt.subplots(figsize = (20,5))
        ax.boxplot(toBox)
        plt.xticks(np.arange(20) + 1, counts, rotation = 40)
        plt.title('Boxplot for each train chunk')
        print(crit_str+' means \n', means)
        
    # Criter results
    plt.figure(figsize=(20,8))
    plt.errorbar(counts, means, yerr=sd_1)
    plt.xlabel('Number of training tokens')
    plt.ylabel(crit_str+' score')
    plt.title('Score against data size')
    if log_scale:
        plt.xscale('log')
    plt.xticks(np.arange(min(counts), max(counts)+1, max(counts)/20))
    if save:
        plt.savefig(save)
    plt.show()
    
    if get_results:
        print('Return {} means \n'.format(crit_str))
        return criter
    else:
        return 