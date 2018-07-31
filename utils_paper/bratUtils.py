# Implement conversion functions for brat format 
import re 
import os
from tqdm import tqdm
import numpy as np 

import spacy
from collections import Counter
from myDocClass import mlt_doc, ncbi_doc, entClass


PUNCT = ['.']
def spacy_doc2conll(spacy_doc, ann_dict, sent_sep = PUNCT, sent_sep_token='', sep_col = '\t'):
    '''Conversion from spacy doc to conll with on etoken per line
        Input:  
            doc, spacy processed document (with sentences and tokens separation)
            ann_dict, a dictionnary containing unilabel entities {start_offset : entClass object}
            sent_sep_token, a separator token to insert between sentences (default is an empty line)
    '''
    conll = []
    prev_ent = ''
    for sent in spacy_doc.sents:
        for w in sent:
            ent_found = False
            w_txt = re.sub(' ','', w.string)
            for i in range(len(w_txt)):
                if (w.idx + i) in ann_dict.keys():
                    cleaned_word = ann_dict[w.idx+i].word
                    if prev_ent==ann_dict[w.idx+i].label:
                        l = cleaned_word + '\tI-'+ann_dict[w.idx+i].label
                    else:
                        l = cleaned_word + '\tB-'+ann_dict[w.idx+i].label
                        prev_ent = ann_dict[w.idx+i].label
                    if len(l) > 0:
                        conll.append(l+'\n')
                    ent_found = True
            # Token is not a label
            if not ent_found:
                # spot paragraop ends
                #if re.search('\n\n*', w.string) is not None:
                #   l = sent_sep_token
                #else:
                # handle undesired tabs (could also handle other )
                l = w.string
                l = re.sub(' ', '', l)
                l = re.sub('\n', '', l)
                l = re.sub('\t', '', l)
                #if l != w.string:print('tab detected')
                prev_ent = 'O'
                if len(l) > 0:
                    conll.append(l+'\tO'+'\n')
        conll.append('\n')
    return conll

def lab_vec(ent_list, lab2lab_ix):
    ''' from a list of multiple entities attached toi a given token and a dict labels2labels_ix, create a vector with ones only for entities attached to the current token
    '''
    label_vec = np.zeros(len(lab2lab_ix))
    for ent in ent_list:
        label_vec[lab2lab_ix[ent.label]] = 1 
    return label_vec

def myDoc2conll(doc, nlp_model, path2save = None, sent_sep_token='', sep_col = '\t'):
    '''Conversion from brat to conll format
        Input:  
            doc, name of the myDoc file (without extension)
            nlp_model, tokenizer, exclusively spacy language model for now (nlp = spacy.load('fr'))
            path2save, path (and name) if we want to save the conll format
            sent_sep_token, optionnal token to separate sentences (default is an empty line)
        Output: 
            doc.text, raw text
            doc.entities, raw annotations (entity objects)
            connl, a .conll file with one token per line with the word and its token separated by a tab, eg: 'Camus\tAuthor\n' 
    '''

    ann_dict = {}
    for ent in doc.entities:
        st = ent.start
        for w in ent.word.split(' '):
            ann_dict[st] = ent
            st = st + len(w) + 1 
    spacy_doc = nlp_model(doc.text) 
    conll = spacy_doc2conll(spacy_doc, ann_dict, sent_sep_token, sep_col)
    if path2save is not None:
        with open(path2save+'.conll', 'w') as f:
            f.writelines(conll)
    return doc.text, doc.entities, conll


def myDoc_multi2conll(doc, nlp_model, path2save = None, sent_sep_token='', sep_col = '\t'):
    '''Conversion from brat to conll format when brat has multi-annotation
        Input:  
            doc, name of the myDoc file (without extension)
            nlp_model, tokenizer, exclusevley spacy language model for now (nlp = spacy.load('fr'))
            path2save, path (and name) if we want to save the conll format
            sent_sep_token, optionnal token to separate sentences (default is an empty line)
        Output: 
            doc.text, raw text
            doc.entities, raw annotations (entity objects)
            connl, a .conll file with one token per line with the word and its token separated by a tab, eg: 'Camus\tAuthor\n' 
    '''

    lab2lab_ix = {}
    start_dict = {}
    for i, ent in enumerate(doc.entities):
        st = ent.start
        end = ent.end
        if st not in start_dict.keys():
            start_dict[st] = []
            start_dict[st].append(ent)
        else:
            start_dict[st].append(ent)
            
        # create dictionnary to have label indices    
        if ent.label not in lab2lab_ix.keys():
            lab2lab_ix[ent.label] = len(lab2lab_ix) 
    lab_ix2lab = {}
    for k, v in lab2lab_ix.items():
        lab_ix2lab[v] = k
    
    # create an order for every multiple token
    window_size = 1
    current_token = np.sum([lab_vec(ent_list, lab2lab_ix) for ent_list in list(start_dict.values())[:window_size]], axis = 0)
    for i, (k, multi_ent) in enumerate(start_dict.items()):
        #print(multi_ent)
        # take the maximal or minimal continuous label over the window :does not take inot account the discontinuities !!!!!!!!!!!!!!!!!!!!
        if len(multi_ent)>1:
            label = lab_ix2lab[np.argmax(current_token, axis = 0)]
        else:
            label = multi_ent[0].label
        start_dict[k] = [entClass(multi_ent[0].word, multi_ent[0].start, multi_ent[0].end, label)]
        # update
        if i - window_size >= 0:
            #print(list(start_dict.values())[i - window_size])
            left_window = lab_vec(list(start_dict.values())[i - window_size], lab2lab_ix)
        else:
            left_window = np.zeros(len(lab2lab_ix))
        if i + window_size < len(start_dict):
            #print(list(start_dict.values())[i + window_size])
            right_window = lab_vec(list(start_dict.values())[i + window_size], lab2lab_ix)
        else:
            right_window = np.zeros(len(lab2lab_ix))
        if multi_ent[0].word == 'née':
            print(lab_vec(multi_ent, lab2lab_ix))
            print(lab_vec(multi_ent, lab2lab_ix) * (current_token - left_window + right_window))
        current_token = lab_vec(multi_ent, lab2lab_ix) * (current_token - left_window + right_window)
        current_token[current_token < 0] = 0
    
    # unlist the elemnts in start_dict
    for k, v in start_dict.items():
        start_dict[k] = v[0]
    # convert text to spacy then to conll 
    spacy_doc = nlp_model(doc.text) 
    conll = spacy_doc2conll(spacy_doc, start_dict, sent_sep_token, sep_col)
    if path2save is not None:
        with open(path2save+'.conll', 'w') as f:
            f.writelines(conll)
    return doc.text, doc.entities, conll


def myCorpus_brat2conll(docs, nlp_model, path2save = None, sent_sep_token = '', doc_sep_token = '', sep_col = '\t'):
    ''' Wrapper for the brat2conll function applied to a folder containing an entire corpus in the brat format
        Input:  
            docs, list of doc objects
            nlp_model, tokenizer, exclusevley spacy language model for now (nlp = spacy.load('fr'))
            path2save, path (and name) if we want to save the conll format
            sent_sep_token, optionnal token to separate sentences (default is an empty line)
            doc_sep_token, optionnal token to separate documents (default is an empty line)
        Output: 
            corpus_conll, a .conll file with the entire corpus with one token per line with the word and its token separated by a tab, eg: 'Camus\tAuthor\n' 
    '''
    corpus_conll = []
    print('Found {} documents. Processing conversion...'.format(len(docs)))
    errors = []
    for d in tqdm(docs):
        t, a, doc = myDoc2conll(d, nlp_model, path2save=path2save, sent_sep_token=sent_sep_token, sep_col = sep_col)
        corpus_conll = corpus_conll + doc
        corpus_conll += doc_sep_token+'\n'
    if path2save is not None:
        with open(path2save + '.conll', 'w') as f:
            f.writelines(corpus_conll)
    return corpus_conll


def build_stats(doc_list):
    ''' Create stats from a list of nested documents (class .myDocClass.nested_doc)
    '''
    corpus_stats = {}
    for doc in doc_list:
        tmp_stats = doc.nested_stats
        for k in tmp_stats.keys():
            if k not in corpus_stats:
                corpus_stats[k] = 0
            corpus_stats[k] += tmp_stats[k]
    return corpus_stats
