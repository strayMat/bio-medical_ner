# NER experiments on MEDPOST

Experiments on the [NCBI-disease corpus](https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/) with the neural tagger [Yaset](http://yaset.readthedocs.io/en/stable/). This corpus contains 592 documents.

## Files:

**Code:**
+ [train_dev_build_ncbi.ipynb](https://github.com/strayMat/bio-medical_ner/blob/master/ncbi/code/train_dev_build_ncbi.ipynb), build train, dev sets to the correct format
+ [launch_ncbi.ipynb](https://github.com/strayMat/bio-medical_ner/blob/master/ncbi/code/launch_ncbi.ipynb), launch in a jupyter multiple trainings
+ [results_ncbi.ipynb](https://github.com/strayMat/bio-medical_ner/blob/master/ncbi/code/results_ncbi.ipynb), various perfomance analysis on the training experiments 

**data:**
Original data in [src](https://github.com/strayMat/bio-medical_ner/tree/master/ncbi/data/src), and built data with help of [train_dev_build_ncbi.ipynb](https://github.com/strayMat/bio-medical_ner/blob/master/ncbi/code/train_dev_build_ncbi.ipynb).

**results:**
Various pre-trained Yaset models (for different parameters) as well as decoding results in ncbi_apply folder.

**jsons:**
Extraction of relevant informations in .json for each training (results exploited in [results_ncbi.ipynb](https://github.com/strayMat/bio-medical_ner/blob/master/ncbi/code/results_ncbi.ipynb)).