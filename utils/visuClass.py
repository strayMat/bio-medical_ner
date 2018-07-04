import re
import random
import os
import pandas as pd

try:
     import torch
except ImportError:
    pass

from tqdm import tqdm

import spacy
from spacy import displacy

from visuUtils import train2myVisu, build_color_scheme
from visuUtils import conll2sent_list, sent_list2spacy, myScores

class visualizer(object):
    ''' Integrate spacy visualization for conll and spacy formats:'''
    def __init__(self, data, predictions, verbose = False, column = -1):
        ''' Input: - data, conll file path, 
                  - prediction, conll file path for predictions
                  - column, the column to be selected as annotation in the conll file (default is lasts column)
        '''
        
        self.path2conll = data
        # convert to spaCy readable json format
        self.data = sent_list2spacy(*conll2sent_list(data, column = column))            
        
        unique_entities = []
        nb_sents = 0
        nb_tokens = 0
        for sent in self.data:
            for ent in sent[1]['entities']:
                if ent[2] not in unique_entities:
                    unique_entities.append(ent[2])
            nb_sents += 1 
            nb_tokens += len(sent[0].split(' '))
        
        # Set summary statistics
        self.nb_sents = nb_sents
        self.nb_tokens = nb_tokens
        self.unique_ents = unique_entities
        # Create a separate container for visualizable data
        self.visu_gold = [train2myVisu(sent) for sent in self.data]
        # Build options for the displayer
        self.options = build_color_scheme([ent.upper() for ent in self.unique_ents])
        self.path2predicted = predictions
        self.pred_data = sent_list2spacy(*conll2sent_list(self.path2predicted))
        self.visu_pred = [train2myVisu(sent) for sent in self.pred_data]        
        if verbose:
            print('Data contains {} sentences with an average of {:.2f} tokens per sentence totalizing {} tokens.'.format(
                self.nb_sents, self.nb_tokens/self.nb_sents, self.nb_tokens))
            print('There are {} entities plus the "O" label: {}'.format(len(self.unique_ents), self.unique_ents))
        return
        
    ''' Apply pre-annotation and get the predictions and scores'''
    def pre_annot_pred(self, column = 6):
        pred_data = sent_list2spacy(*conll2sent_list(self.path2conll, column = column))
        self.pred_data = pred_data
        self.visu_pred = [train2myVisu(sent) for sent in self.pred_data]
        self.path2predicted = self.path2conll
        return
    
    def score_predictions(self, average = 'weighted', grouping = None, column = -1, punct_ignore = False, col_sep = '\t'):
        ''' Score the model on the predicted data
        input:  - average, [None, 'macro', 'micro', 'weighted'] 
        see. http://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html for explanantion
                - grouping, dictionnary with entry of the form {'NAME':[FNAME, LNAME]} (one to many)
                - column, integer, column from the prediction file to be selected as the prediction (in case of multiple prediction for example)
                - punct_ignore, should the punctuation be removed from the evaluation
                - col_sep, separator between word and label in the conll file
        '''

        self.scores = myScores(self.path2conll, self.path2predicted, average = average, grouping = grouping, column = column, punct_ignore = punct_ignore, col_sep = col_sep)
        if column != -1:
            print('Scoring using the {} column of the test set'.format(column))
        
        # build false positive and false negative lists
        self.gold_per_label = {}
        self.pred_per_label = {}
        self.FP_dic = {}
        self.FN_dic = {}

        for lab in self.unique_ents:
            self.gold_per_label[lab] = []
            self.pred_per_label[lab] = []
            self.FP_dic[lab] = []
            self.FN_dic[lab] = []
        
        punct = ['_', '-', "'", ',', ';', '.', '(', ')', '/', '\\', ':']
        # fill gold_ents entities dict
        for i, sents in enumerate(self.data):
            ents = sents[1]['entities']
            for ent in ents:
                if (sents[0][ent[0]:ent[1]] not in punct) & punct_ignore:
                    self.gold_per_label[ent[2]].append((i, *ent))
                elif not punct_ignore:
                    self.gold_per_label[ent[2]].append((i, *ent))

        # fill pred_ents entities dict
        for i, sents in enumerate(self.pred_data):
            ents = sents[1]['entities']
            for ent in ents:
                if (sents[0][ent[0]:ent[1]] not in punct) & punct_ignore:
                    self.pred_per_label[ent[2]].append((i, *ent))
                elif not punct_ignore:
                    self.pred_per_label[ent[2]].append((i, *ent))

        for lab in self.unique_ents:
            for ent in self.pred_per_label[lab]:
                if ent not in self.gold_per_label[lab]:
                    self.FP_dic[lab].append(ent)
            for ent in self.gold_per_label[lab]:
                if ent not in self.pred_per_label[lab]:
                    self.FN_dic[lab].append(ent)
                    
        return self.scores
    
    
   
    def scores2pd(self):
        ''' Wrapper to return scores as dataframe'''
        
        df_scores = pd.DataFrame(data = {'precision':self.scores[0],
                            'recall':self.scores[1],
                            'f1':self.scores[2],
                            'count':self.scores[3]}, index = self.unique_ents)
        df_scores.sort_index(inplace=True)
        return df_scores

    
    
    def visu_gold_sample(self, ix = None, verbose = True, context = 0):
        ''' Visualize a random gold sample'''
        
        if ix is None:
            ix = random.randint(0, len(self.data))
        #elif(ix >= len(self.data)):
         #   print('ix out of bound, please selecte an index smaller than {}'.format(len(self.data)))
         #   return
        if verbose:
            print('sentence {}/{}'.format(ix, len(self.data)))
        displacy.render(self.visu_gold[(ix-context):(ix+context+1)], style = 'ent', jupyter = True, manual = True, options = self.options)
        return
    
    
    def visu_pred_sample(self, ix = None, verbose = True, context = 0):
        ''' Visualize a random pred sample'''
        
        if ix is None:
            ix = random.randint(0, len(self.data))
        elif(ix >= len(self.data)):
            print('ix out of bound, please selecte an index smaller than {}'.format(len(self.data)))
            return
        if verbose:
            print('sentence {}/{}'.format(ix, len(self.data)))
        displacy.render(self.visu_pred[(ix-context):(ix+context+1)], style = 'ent', jupyter = True, manual = True, options = self.options)
        return
    
    
    def visu_compare(self, ix = None, context = 0):
        ''' Visualize the same sample from gold and pred'''
        
        if ix is None:
            ix = random.randint(0, len(self.data))
        print('Gold:')
        self.visu_gold_sample(ix, verbose = True, context = context)
        print('Predicted:')
        self.visu_pred_sample(ix, verbose = False, context = context)
        return
    
    
    def visu_FP_sample(self, lab = None, i = None, context = 0, verbose = True):
        ''' Visualize one False Positive for a given category'''
        
        if lab is None:
            lab = random.choice(self.unique_ents)
        
        nb_errors = len(self.FP_dic[lab])
        if i is None:
            i = random.randint(0, nb_errors)
            ix = self.FP_dic[lab][i][0] 
        if verbose:
            print('There are {} FP for the {} category.'.format(nb_errors, lab))
            print('Displaying FP {}/{}'.format(i, nb_errors))
        self.visu_compare(ix, context = context)
        return
    
    
    def visu_FPs(self, lab = None, context = 0):
        ''' Visualize all FPs of a given category'''
        
        if lab is None:
            lab = random.choice(self.unique_ents)
        nb_errors = len(self.FP_dic[lab])
        print('There are {} FP for the {} category.'.format(nb_errors, lab))
        # little astuce to avoid showing several time the same sentence
        ix_prec = -1
        for i in range(0, nb_errors):
            ix_tmp = self.FP_dic[lab][i][0]
            if ix_prec != ix_tmp:
                self.visu_compare(ix_tmp, context = context)
                ix_prec = ix_tmp
                print('----------------------------------------------\n')

    
    
    
    def visu_FN_sample(self, lab = None, i = None, context = 0, verbose = True):
        ''' Visualize one False Negative for a given category'''
        
        if lab is None:
            lab = random.choice(self.unique_ents)
        
        nb_errors = len(self.FN_dic[lab])
        if i is None:
            i = random.randint(0, nb_errors)
            ix = self.FN_dic[lab][i][0] 
        if verbose:
            print('There are {} FN for the {} category.'.format(nb_errors, lab))
            print('Displaying FN {}/{}'.format(i, nb_errors))
        self.visu_compare(ix, context = context)
        return
    
    
    def visu_FNs(self, lab = None, context = 0):
        ''' Visualize all FNs of a given category'''
        
        if lab is None:
            lab = random.choice(self.unique_ents)
        nb_errors = len(self.FN_dic[lab])
        print('There are {} FN for the {} category.'.format(nb_errors, lab))
        # little astuce to avoid showing several time the same sentence
        ix_prec = -1
        for i in range(0, nb_errors):
            ix_tmp = self.FN_dic[lab][i][0]
            if ix_prec != ix_tmp:
                self.visu_compare(ix_tmp, context = context)
                ix_prec = ix_tmp
                print('----------------------------------------------')
    
    
    
    def group_labs(self, grouping):
        ''' Given a grouping of categories, change the categories of the visu object to perform new visualization and scoring based on these new labels.'''
        
        # change the labels in gold_data
        new_data = []
        for sent in self.data:
            ents = sent[1]['entities']
            new_ents = []
            for ent in ents:
                for k, v in grouping.items():
                    if ent[2] in v:
                        ent = (ent[0], ent[1], k)
                if ent[2]!='O':
                    new_ents.append(ent)
            new_sent = (sent[0], {'entities':new_ents})
            new_data.append(new_sent)
        self.data = new_data
        self.visu_gold = [train2myVisu(sent) for sent in self.data]
        
        # change the label in pred_data
        new_data = []
        for sent in self.pred_data:
            ents = sent[1]['entities']
            new_ents = []
            for ent in ents:
                for k, v in grouping.items():
                    if ent[2] in v:
                        ent = (ent[0], ent[1], k)
                if ent[2]!='O':
                    new_ents.append(ent)
            new_sent = (sent[0], {'entities':new_ents})
            new_data.append(new_sent)
        self.pred_data = new_data
        self.visu_pred = [train2myVisu(sent) for sent in self.pred_data]
        # recompute the unique entities
        unique_entities = []
        for sent in self.data:
            for ent in sent[1]['entities']:
                if ent[2] not in unique_entities:
                    unique_entities.append(ent[2])
        self.unique_ents = unique_entities
        print('New unique entities after grouping:', self.unique_ents)
        self.options = build_color_scheme(self.unique_ents)
        return

# Decoding functions for the different frameworks
# For now on there are Yaset, NCRFpp and spaCy

try:
    from ncrfpp.utils.myUtils import evaluate, load_model_decode
    from ncrfpp.utils.data import Data
except ImportError:
    pass

def ncrf_decoding(decode_conf_dict, verbose = False):
    ''' Perform ncrf decoding from a config file'''
    
    data = Data()
    data.read_config(decode_conf_dict)
    status = data.status.lower()
    data.HP_gpu = torch.cuda.is_available()
    print("MODEL: decode")
    data.load(data.dset_dir)
    ## needed after data.load(data.dset_dir)
    data.read_config(decode_conf_dict)
    print(data.raw_dir)
    # exit(0)
    data.show_data_summary()
    data.generate_instance('raw')
    print("nbest: %s"%(data.nbest))
    decode_results, pred_scores = load_model_decode(data, 'raw')
    if data.nbest:
        data.write_nbest_decoded_results(decode_results, pred_scores, 'raw')
    else:
        data.write_decoded_results(decode_results, 'raw')
    # convert to the same format as yaset
    with open(decode_conf_dict['decode_dir'], 'r') as f:
        predictions = f.read().splitlines()
    new_preds = []
    for l in predictions:
        if l != '':
            if l[0] != '#':
                ll = '\t'.join(l.split(' ')) + '\n'
                new_preds.append(ll)
        elif l == '':
            new_preds.append('\n')
    with open(decode_conf_dict['decode_dir'], 'w') as f:
        f.writelines(new_preds)
    print('end')        
    return


def yaset_pred(path2model, pathgold, path2save):
    ''' Apply yaset and get the predictions and scores'''
    
    print('Applying yaset model...(1 to 2 mins)')
    apply_yaset = 'yaset APPLY --working-dir '+path2save+' --input-file '+pathgold+' --model-path '+ path2model     
    os.system(apply_yaset)
    return 