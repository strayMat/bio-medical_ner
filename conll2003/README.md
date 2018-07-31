# NER experiments on CoNNL 2003 shared task dataset

Experiments on the [conll2003 corpus](https://www.clips.uantwerpen.be/conll2003/ner/) with the neural tagger [YASET](http://yaset.readthedocs.io/en/stable/). This corpus contains 592 documents. We got it from [Lample](https://github.com/glample/tagger/tree/master/dataset) (see [Lample et al., 2016](https://arxiv.org/abs/1603.01360)).

## Files:

**Code:**
+ [train_dev_build_conll2003.ipynb](), build train, dev and test sets to the correct format
+ [launch_conll2003.ipynb](), launch in a jupyter multiple trainings
+ [conll2003_hyperopt.ipynb](), launch hyperopt hyper-parameters search on the corpus (dev data)
+ [results_conll2003](), various perfomance analysis on the training experiments 
+ [Decode_visualize_errors](), decode from a pretrained model and visualize labels and errors with the visualizer class.

**data:**
Original data in [iob_data](), and built data with help of [train_dev_build_conll2003.ipynb]().

**results:**
Various pre-trained Yaset models (for different parameters) as well as decoding results in conll_apply folder.

**jsons:**
Extraction of relevant informations in .json for each training (results exploited in [results_conll2003]()).