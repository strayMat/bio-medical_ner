# Evaluation of YASET on various bio-medical datasets

This repo describes the code and the processes used to evaluate [Yaset](http://yaset.readthedocs.io/en/stable/), a neural model for NER on differents datasets. These experiences and their interpretations are precisely discribed in the following paper, [Tourille et al., 2018]().

## Corpora

The different corpora are:
+ [conll2003](https://github.com/strayMat/bio-medical_ner/tree/master/conll2003)
+ [medpost](https://github.com/strayMat/bio-medical_ner/tree/master/medpost)
+ [ncbi](https://github.com/strayMat/bio-medical_ner/tree/master/ncbi)

Each of the folder contains a README.md, commented jupyter notebooks, a data folder and partial summary of the results in a json directory.  

## Utils

The auxilliary functions used in notebooks are discribed in [utils_paper](https://github.com/strayMat/bio-medical_ner/tree/master/utils_paper).

## Embeddings

The origin and construction of word embeddings used by the model are in [en_word_emb](https://github.com/strayMat/bio-medical_ner/tree/master/en_word_emb), a notebook describes how they are constructed.


## Requirements:

Install the Python dependencies with :
`pip install -r requirements.txt`

Install Yaset following [the instructions](http://yaset.readthedocs.io/en/stable/getting_started.html#installation)

