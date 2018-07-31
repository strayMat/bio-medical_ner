# Auxiliary functions 

This folder contains different python files regrouping all auxiliary functions used to preprocess the data, conduct and analyze the experiments. Detailed input and output are in the `.py` files.


## [bratUtils.py](https://github.com/strayMat/bio-medical_ner/tree/master/utils_paper/bratUtils.py)

**Main focus:** convert brat files to conll format 

+ `spacy_doc2conll`, Conversion from spacy-doc object to conll with one token per line
+  `lab_vec`, one hot encoding for label list
+ `myDoc2conll`, Conversion from brat to conll format (calling spacy_doc2conll)
+ `myDoc_multi2conll`, Conversion from brat to conll format when brat has multi-annotation
+ `myCorpus_brat2conll`, Wrapper for the brat2conll function applied to a folder containing an entire corpus in the brat format
+ `build_stats`, Create stats from a list of nested documents (class .myDocClass.nested_doc)


## [myDocClass.py](https://github.com/strayMat/bio-medical_ner/tree/master/utils_paper/myDocClass.py)

**Main focus:** Document level classes called in [bratUtils.py](https://github.com/strayMat/bio-medical_ner/tree/master/utils_paper/bratUtils.py)

+ `entClass`, Entity class for Doc classes
+ `mlt_doc`, myDoc class that takes brat-like files as input and return structured object
+ `mlt_multi_doc`, doc class for merlot multi-labels, inherit from mlt_doc
+ `ncbi_doc`, separeted doc class, specific to ncbi strange brat-like format


## [confUtils.py](https://github.com/strayMat/bio-medical_ner/tree/master/utils_paper/confUtils.py)

**Main focus:** read/write/change conf files 

+ `read_conf`, Read function adapted to yaset conf files 
+ `write_conf`, Write function adapted to yaset conf files 
+ `change_conf`, Change some inputs from a conf dictionnary


## [conllUtils.py](https://github.com/strayMat/bio-medical_ner/tree/master/utils_paper/conllUtils.py)

**Main focus:** build, segment and summarize conll files

+ `line2sent`, Cut the dataset in a list of sentences:
+ `sent2line`, Write a  list of sentences as a list of token lines with \n at the end
+ `write_trainfiles`, Segment the dataset on sentences in different chunk sizes and save to disk
+ `group_conll`, Grouping function that takes a conll format and fusionned desired entity classes together
+ `rm_tokens`, Remove totally some tokens (attached to specific labels)
+ `describe_entities`, Describe conll file entities
+ `extract_entities`, Extract entities from a conll


## [resultsUtils.py](https://github.com/strayMat/bio-medical_ner/tree/master/utils_paper/resultsUtils.py)

**Main focus:** Analize experiment results

+ `get_results`, Read a yaset result directory and collect all relevant informations in it
+ `read_log`, Read a yaset log file and return the information of interest
+ `build_jsons`, sA json warper on top of get_result
+ `str2bool`, Convert boolean string to python boolean
+ `json2pandas`, Read json files and return pandas dataframe
+ `plot_traj`, Plot the training progression from a list of trajectories
+ `avg_traj`, Plot the average of a list of trajectories
+ `plot_results`,  Plot the curve of score progression against data size


## [visuClass.py](https://github.com/strayMat/bio-medical_ner/tree/master/utils_paper/visuClass.py)

**Main focus:** Visualizer class

+ `visualizer`, visualizer object that contains internatl scoring functions, as well as error visualization
+ `yaset_pred`, yaset prediction from a gold standard conll file

## [visuUtils.py](https://github.com/strayMat/bio-medical_ner/tree/master/utils_paper/visuUtils.py)

**Main focus:** utilitaries for the Visualizer class

+ `conll2sent_list`, Extract text and tags from a conll file
+ `sent_list2spacy`, Convert a list of text sentences and a list of tags sentences to the spaCy training format
+ `train2myVisu`, Convert a training spaCy format to the manually viewable format of spaCy
+ `build_color_scheme`, Build a cool version of colors for spacy visualization tool
+ `myScores`, Compute scores (precision, recall, f1) given a gold and a predicted conll files
+ `unique_ents`, Given a list of entities, return a set of unique entities
