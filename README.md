# Evaluation of YASET on various bio-medical datasets

This repo describes the code and the processes used to evaluate [Yaset](), a neural model for NER on differents datasets. These experiences and their interpretations are precisely discribed in the following paper []().

## Corpora

The different corpora are:
+ [conll2003]()
+ [medpost]()
+ [ncbi]()

+ [merlot_medic]()
+ [merlot_study]()

Each of the folder contains a README.md, commented jupyter notebooks, a data folder, partial summary of the results in a json directory and pretrained yaset models in a resutls directory.  

## Utils

The auxilliary functions used in notebooks are discribed in [utils_paper](http://yaset.readthedocs.io/en/stable/).

## Embeddings

The origin and construction of word embeddings used by the model are in [en_word_emb](), a notebook describes how they are constructed.


## Requirements:

Install the Python dependencies with :
`pip install -r requirements.txt`

Install Yaset following [the instructions](http://yaset.readthedocs.io/en/stable/getting_started.html#installation)

