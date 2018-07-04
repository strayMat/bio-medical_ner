from tqdm import tqdm
from sklearn.metrics import precision_recall_fscore_support

# Conversion functions from conll to a spaCy friendly format for visualization

def conll2sent_list(path2data, column = -1):
    '''convert a conll formated text file to a list of 
    - text sentences (one sentence =  one list of words)
    - a list of tags sentences (one sentences = one list of tags)
    parameters: 
    - column, select which column is used in the connl file as tag(default is -1 ie last column)
    '''
    # open txt file
    with open(path2data, 'r') as f:
        data = f.read().splitlines()
    text = []
    iob_tags = []
    sent = []
    sent_tags = []
    for l in tqdm(data):
        if l != '':
            if l[0]!='#':
                ll = l.split('\t')
                sent.append(ll[0])
                sent_tags.append(ll[column])
        else:
            text.append(sent)
            iob_tags.append(sent_tags)
            sent = []
            sent_tags = []
    return text, iob_tags


def sent_list2spacy(texts_list, tags_list):
    '''convert a list of text sentences and a list of tags sentences to the spaCy training format
    '''
    spacy_data = []
    for text, tags in zip(texts_list, tags_list):
        tmp_char = 0
        final_text = ' '.join(text)
        final_tags = []
        for w, tag in zip(text, tags):
            if tag != 'O':
                final_tags.append(tuple((tmp_char, tmp_char + len(w), tag[2:])))
            tmp_char += len(w) + 1 
        spacy_data.append(tuple((final_text, {'entities':final_tags})))
    return spacy_data


def train2myVisu(train_format):
    '''Convert a training spaCy format to the manually viewable format of spaCy
    '''
    res = {}
    res['text'] = train_format[0]
    tags = []
    for tup in train_format[1]['entities']:
        dic = {}
        dic['start'] = tup[0]
        dic['end'] = tup[1]
        dic['label'] = tup[2]
        tags.append(dic)
    res['ents'] = tags
    res['title'] = None
    return res


''' Build a cool version of colors for spacy visualization tool and return the visu options dictionnary with these colors
'''
def build_color_scheme(unique_entities, default_cycle = 
                       ['#CCC8BF',
                        '#00CCBF', '#3D9993', '#00FF5E', '#FF4082', '#CC14B0', 
                        '#CC5300', '#99623D', '#FF1D00', '#40FF6A', '#22CC14',
                        '#BA00CC', '#953D99', '#6700FF', '#FFE640', '#CCA72C',
                        '#0037CC', '#3D5699', '#00CBFF', '#FF8040', '#CC3512']):
    colors = {}
    for tag, c in zip(unique_entities, default_cycle[:len(unique_entities)]):
        colors[tag] = c
    return {'ents': list(colors.keys()), 'colors': colors}


# Auxiliary functions to score the results 

def myScores(path2golds, path2preds, average = 'weighted', grouping = None, column = -1, punct_ignore = False, col_sep = '\t', extract_tags = False):
    ''' Compute scores (precision, recall, f1) given a gold and a predicted conll files
    input:  - path2golds, 
            - path2preds,
            - average, string, how to average the scores between classes; None is no averaging, 'weighted' is a weighted macro score (all options can be found here, http://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html)
            - grouping, dictionnary mapping goal labels to a list of labels that should be accounted as the same goal label for evaluation
            - column, integer, column from the prediction file to be selected as the prediction (in case of multiple prediction for example)
            - punct_ignore, should the punctuation be removed from the evaluation
            - col_sep, separator between word and label in the conll file
            - extract_tags, if we want to extract the list of non-O labels in the function output 
    '''
    
    punct = ['_', '-', "'", ',', ';', '.', '(', ')', '/', "\\", ':']
    # open txt file
    with open(path2golds, 'r') as f:
        data = f.read().splitlines()
    gold_tags = []
    for l in tqdm(data):
        if l != '':
            ll = l.split(col_sep)
            g = ll[-1]
            if g != 'O':
                g = g[2:]
                if grouping is not None:
                    for k, v in grouping.items():
                        if g in v:
                            g = k
                # ignore punctuation
                if (ll[0] in punct) & (punct_ignore):
                    g = 'O'
            gold_tags.append(g)
    # open txt file
    with open(path2preds, 'r') as f:
        data = f.read().splitlines()
    pred_tags = []
    for l in tqdm(data):
        if (l != ''):
            ll = l.split(col_sep)
            g = ll[column]
            if g != 'O':
                g = g[2:]
                if grouping is not None:
                    for k, v in grouping.items():
                        if g in v:
                            g = k
                # ignore punctuation
                if (ll[0] in punct) & (punct_ignore):
                    g = 'O'
            pred_tags.append(g)
            
    unique_entities = unique_ents(gold_tags)
    # compute scores
    unique_entities = [ent for ent in unique_entities if ent !='O']
    print('Predicted labels: {}'.format(unique_entities))
    scores = precision_recall_fscore_support(gold_tags, pred_tags, labels = unique_entities, average = average)
    
    if extract_tags:
        return scores, gold_tags, pred_tags
    else:
        return scores

    
def unique_ents(entities):
    ''' Given a list of entities, return a set of unique entities
    '''
    unique_entities = []
    for ent in entities:
        if ent not in unique_entities:
            unique_entities.append(ent)
    return unique_entities
