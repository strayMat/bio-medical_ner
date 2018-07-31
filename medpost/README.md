# NER experiments on MEDPOST

Experiments on [medpost corpus](http://biocreative.sourceforge.net/bio_corpora_links.html) ([download link](ftp://ftp.ncbi.nlm.nih.gov/pub/lsmith/MedTag/medtag.tar.gz)) with the neural tagger [Yaset](http://yaset.readthedocs.io/en/stable/). The MedPost corpus consists of 6 700 sentences, and is annotated with parts of speech, and gerund arguments. It is based on MEDLINE abstracts, the original paper describing the construction of the corpus can be found [here](https://academic.oup.com/bioinformatics/article/20/14/2320/213968).

## Files:

**Code:**
+ [train_dev_build_medpost.ipynb](https://github.com/strayMat/bio-medical_ner/blob/master/medpost/code/train_dev_build_medpost.ipynb), build train, dev sets to the correct format
+ [launch_medpost.ipynb](https://github.com/strayMat/bio-medical_ner/blob/master/medpost/code/launch_medpost.ipynb), launch in a jupyter multiple trainings
+ [results_medpost.ipynb](https://github.com/strayMat/bio-medical_ner/blob/master/medpost/code/results_medpost.ipynb), various perfomance analysis on the training experiments 

**data:**
Original data in [medtag](https://github.com/strayMat/bio-medical_ner/tree/master/medpost/data/medtag), and built data with help of [train_dev_build_medpost.ipynb](https://github.com/strayMat/bio-medical_ner/blob/master/medpost/code/train_dev_build_medpost.ipynb).

**results:**
Various pre-trained Yaset models (for different parameters) as well as decoding results in conll_apply folder.

**jsons:**
Extraction of relevant informations in .json for each training (results exploited in [results_medpost.ipynb](https://github.com/strayMat/bio-medical_ner/blob/master/medpost/code/results_medpost.ipynb)).