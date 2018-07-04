from spacy import displacy
import re

class entClass(object):
    ''' Entity class for myDoc classes, similarly to spacy, it contains the string, the offsets and the label for one entity
    '''
    
    def __init__(self, word, start, end, label):
        self.word = word
        self.start = start
        self.end = end
        self.label = label
        return
    
    def __repr__(self):
        return self.word+':'+self.label+' ('+str(self.start)+','+str(self.end)+')'
    
    def __str__(self):
        return self.word
    
class mlt_doc(object):
    ''' myDoc class that takes brat-like files as input and return structured object
    '''    

    def __init__(self, file):
        with open(file+'.txt', 'r') as f:
            text = f.read()
        with open(file+'.ann', 'r') as f:
            annots = f.read().splitlines()
        self.text = text
        self.entities = self.create_ents(annots)
        return 
    
    def create_ents(self, entities):
        ents = []
        for ent in entities:
            #check that this is an anootation and not a comment
            if ent[0] == 'T':
                line = ent.split('\t')
                annot = line[1].split(' ')[0]
                st = int(line[1].split(' ')[1])
                for w in line[2].split(' '):
                    new_ent = entClass(w, st, st+len(w), annot)
                    st = st + len(w) + 1
                    if new_ent != []:
                        ents.append(new_ent)
        ents = sorted(ents, key=lambda ent: ent.start)
        return(ents)
    
    def __repr__(self):
        return self.text
    
    def __str__(self):
        return self.text
    
    def visu(self):
        self.unique_ents = set([ent.label for ent in self.entities])
        visu_data = [{'text':self.text, 'ents':[dict(zip(['start', 'end', 'label'], [ent.start, ent.end, ent.label])) for ent in self.entities], 'title':None}]
        displacy.render(visu_data, jupyter = True, style = 'ent', manual = True)
        return
       
        
class mlt_multi_doc(mlt_doc):
    '''doc class for merlot multi-labels, inherit from med_doc, the only method that changes create_ents
    '''

    def create_ents(self, entities):
        ents = []
        for ent in entities:
            #check that this is an anootation and not a comment
            if ent[0] == 'T':
                line = ent.split('\t')
                annot = line[1].split(' ')[0]
                offsets = line[1].split(' ')[1:]
                # case entity is in several pieces
                if ';' in ' '.join(offsets):
                    offsets = ' '.join(offsets).split(";")
                    for offset in offsets:
                        st = int(offset.split(' ')[0])
                        end = int(offset.split(' ')[1])
                        subtext = self.text[st:end]
                        subtext = re.sub("'", " ", subtext)
                        subtext = re.sub("’", " ", subtext)
                        for w in subtext.split(' '):
                            w = re.sub(' ', '', w)
                            if w != '':
                                new_ent = entClass(w, st, st+len(w), annot)
                                st = st + len(w) + 1
                                if new_ent != []:
                                    ents.append(new_ent)

                else:
                    st = int(offsets[0])
                    line_text = line[2]
                    line_text = re.sub("'", " ", line_text)
                    line_text = re.sub("’", " ", line_text)
                    for w in line_text.split(' '):
                        if w != '':
                            new_ent = entClass(w, st, st+len(w), annot)
                            st = st + len(w) + 1 
                            if new_ent != []:
                                ents.append(new_ent)
        ents = sorted(ents, key=lambda ent: ent.start)
        
        # dealing with the entities with same start/end but different end/start (taking the biggest span)
        end_ents = []
        end_ents.append(ents[0])
        # first passage to eliminate same ends/different starts
        for ent in ents:
            b = True
            for nent in end_ents:
                if ent.end == nent.end:
                    if ent.start > nent.start:
                        #print(ent, ent.start, nent, nent.start)
                        b = False
                        #ent_sub = entClass(nent.word, nent.start, ent.end, ent.label)
            if b:
                end_ents.append(ent)
            #else:
            #    end_ents.append(ent_sub)
        # Second passage to eliminate same starts/different ends
        start_ents = []
        for ent in end_ents:
            b = True
            for nent in start_ents:
                if ent.start == nent.start:
                    if ent.end < nent.end:
                        #print(ent, ent.end, nent, nent.end)
                        b = False
                        #ent_sub = entClass(nent.word, ent.start, nent.end, ent.label)
            if b:
                start_ents.append(ent)
            #else:
            #    start_ents.append(ent_sub)
        #start_ents = ents
        return(start_ents)


class ncbi_doc(object):
    ''' separate class for ncbi_doc, needs a slight pre-processing before applying the method, TODO: put this preprocessing in this class
    '''
    def __init__(self, title, text, entities):
        txt_idx, title = title.split('|t|')
        self.idx = txt_idx
        self.title = title
        self.text = title + ' ' + text.split('|a|')[1]
        self.entities = self.create_ents(entities)
        return 
    
    def create_ents(self, entities):
        ents = []
        for ent in entities:
            line = ent.split('\t')
            all_txt = self.text[int(line[1]):int(line[2])]
            st = int(line[1])
            annot = line[4]
            for w in all_txt.split(' '):
                    new_ent = entClass(w, st, st+len(w), annot)
                    st = st + len(w) + 1
                    if new_ent != []:
                        ents.append(new_ent)
        return(ents)
    
    def __repr__(self):
        return self.text
    
    def __str__(self):
        return self.text
    
    def visu(self):
        self.unique_ents = set([ent.label for ent in self.entities])
        visu_data = [{'text':self.text, 'ents':[dict(zip(['start', 'end', 'label'], [ent.start, ent.end, ent.label])) for ent in self.entities], 'title':None}]
        displacy.render(visu_data, jupyter = True, style = 'ent', manual = True)
        return
