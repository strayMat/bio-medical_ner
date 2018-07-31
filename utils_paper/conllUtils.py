# Conll files

import re
from collections import Counter
import numpy as np

def line2sent(data):
    ''' Cut the dataset in a list of sentences:
    input: list of token lines (conll format) with sentences separated by  an empty line ('')
    output: list of sentences as list of lines 
    ''' 
    sent_data = []
    sent = []
    for l in data:
        if l != '':
            sent.append(l)
        else:
            sent_data.append(sent)
            sent = []
    return(sent_data)

def sent2line(sent_data):
    ''' The inverse operation: write a  list of sentences as a list of token lines with \n at the end,
    Separate the sentences by an empty line '\n'
    '''
    data2write = []
    for sent in sent_data:
        for l in sent:
            data2write.append(l+'\n')
        data2write.append('\n')
    return data2write

def write_trainfiles(path2data, write_dir, chunk_to_save = -1, nb_chunks = 20, shuffle = False, verbose = True, save = True):
    ''' Segment the dataset on sentences in different chunk sizes and save to disk
    Input:  - path2data, location of the original dataset
            - write_dir, directory location of the new chunks
            - chunk_to_save, default is -1 and will save all chunks, if one desired chunk only is wanted enter the chunk number (<nb_chunks)
            - nb_chunks, number of subdivision in the data
            - shuffle, default false, shuffle the chunks
            - verbose, more information when processing
    Output, the list of the chunks
    '''
    with open(path2data, 'r') as f:
        data = f.read().splitlines()
    
    nb_patients = np.sum([1 for l in data if re.match('Pat\t*', l) is not None])
    nb_sent = np.sum([1 for l in data if l==''])
    nb_tokens = len(data) - nb_sent 
    print('Total number of patients {}'.format(nb_patients))
    # the pat + : tokens are not real sentences 
    print('Total number of sentences {}'.format(nb_sent- nb_patients))
    all_train = []
    sent_data = line2sent(data)
    cut_on_sent = nb_sent//nb_chunks
    cut_on_pat = nb_patients//nb_chunks
    if verbose:
        print(cut_on_sent)
    # loop on the desired lengths of the datasets
    for i in range(nb_chunks):
        sub_sent = sent_data[i*cut_on_sent:(i+1)*cut_on_sent]
        sub_train = sent2line(sub_sent)
        #ratio = len(sub_train)/len(data)
        all_train.append(sub_train)
        # shuffle the blocks
        if shuffle:
            random.shuffle(all_train)
        
    to_save = []
    if chunk_to_save != -1:
        for i in np.arange(chunk_to_save+1):
            to_save += all_train[i]
        #to_save.append(i_mail)
        #to_save.append(i_nir)
        #to_save.append(b_nir)
        ratio = len(to_save)/len(data)
        path2write = write_dir+'chunk_'+str(i)+'_ratio_'+str(int(100*np.round(ratio,2)))+'.conll'
        if save:
            with open(path2write, 'w') as f:
                f.writelines(to_save)
        if verbose:
            print('number of tokens {}/{}'.format(len(to_save), len(data)))
    else:
        for i in np.arange(nb_chunks):
            to_save = []
            for j in np.arange(i+1):
                to_save += all_train[j]
            #to_save.append(i_mail)
            #to_save.append(i_nir)
            #to_save.append(b_nir)
            ratio = len(to_save)/len(data)
            path2write = write_dir+'chunk_'+str(i)+'_ratio_'+str(int(100*np.round(ratio,2)))+'.conll'
            if save:
                with open(path2write, 'w') as f:
                    f.writelines(to_save)
            if verbose:
                print('number of tokens {}/{}'.format(len(to_save), len(data)))
    
    if save:
        print('wrote {} training sets at location {}'.format(nb_chunks, path2write))
    return all_train


def group_conll(path2original_data, path2grouped_data, grouping: list):
    ''' Grouping function that takes a conll format and fusionned desired entity classes together. Entity labels in the grouping parameter should be provided WITHOUT the iob format.
        input:  - path2original_data, original conll file
                - path2grouped, path where to save fusionned file
                - grouping, dictionnary with entry of the form {'NAME':[FNAME, LNAME]} (one to many)
        output: None, only save new conll document
    '''
    with open(path2original_data, 'r') as f:
        data = f.read().splitlines()
    grouped_data = [] 
    prev = ''
    for l in data:
        ll = l.split('\t')
        for k, v in grouping.items():
            if ll[-1][2:] in v:
                ll[-1] = k
        if (ll[-1] not in ['', 'O']):
            if (ll[-1][1] == '-'):
                ll[-1] = ll[-1][2:]
        # correct bio scheme
        if l != '':
            if ll[-1] != 'O':
                if ll[-1] == prev:
                    ll[-1] = 'I-'+ll[-1]
                else:
                    ll[-1] = 'B-'+ll[-1]
                prev = ll[-1][2:]
            else:
                prev = 'O'

        grouped_data.append('\t'.join(ll) + '\n')
    print(data[10:13])
    print(grouped_data[10:13])

    with open(path2grouped_data, 'w') as f:
        f.writelines(grouped_data)
    return grouped_data


def rm_tokens(path2original_data, path2rm_data, entities2rm: list):
    ''' Remove totally some tokens (lines in the conll format) in regard to their labels (if some labels is only noise but ahas been tagged, e.g. tagged header and footers)
    '''
    with open(path2original_data, 'r') as f:
        data = f.read().splitlines()
    rm_data = [] 
    prev = ''
    for l in data:
        ll = l.split('\t')
        if ll[-1][2:] not in entities2rm:
            rm_data.append(l+'\n')
    # save new dataset
    with open(path2rm_data, 'w') as f:
        f.writelines(rm_data)
    return rm_data


def describe_entities(path2conll, iob = False, verbose = True):
    ''' Describe conll file entities (provide the numbers of each unique entity in the corpus)
    '''
    
    with open(path2conll, 'r') as f:
        data = f.read().splitlines()
    nb_tokens = np.sum([1 for l in data if l!=''])
    nb_sents = np.sum([1 for l in data if l==''])
    entities = [e.split('\t')[-1] for e in data if e.split('\t')[-1]!='']
    if not iob:
        entities = [e[2:] if e!='O' else 'O' for e in entities]
    nb_tagged = np.sum([1 for e in entities if e!='O'])
    if verbose:
        print('Corpus containing {} tokens in {} sentences with {} non-O tags'.format(nb_tokens, nb_sents, nb_tagged))
    return Counter(entities)
    
def extract_entities(path2conll):
    ''' Extract entities from a conll (BIO format) file and return a dictionnary with unique entities as key and lists of entity wods as values
    ''' 
    with open(path2conll, 'r') as f:
        data = f.read().splitlines()
    ents_set = [e.split('\t')[-1] for e in data if e.split('\t')[-1]!='']
    ents_set = set([e[2:] for e in ents_set if e!='O'])
    ents_dict = {}
    for ent in ents_set:
        ents_dict[ent] = []
    print(ents_set)
    whole_entity = []
    prev = ''
    for l in data:
        if l != '':
            ll = l.split('\t')
            w = ll[0]
            ent = ll[-1]
            if (ent == 'O') | (ent[0]=='B'):
                if len(whole_entity) > 0:
                    ents_dict[prev].append(' '.join(whole_entity))
                    whole_entity = []
                    prev = ent[2:]
            if ent[0] in ['B', 'I']:
                whole_entity.append(w)
                prev = ent[2:]

    return ents_dict
