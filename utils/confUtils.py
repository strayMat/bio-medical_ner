
def read_conf(path2conf_model, verbose = False):
    '''read and write functions adapted to yaset conf files 
    python format is a dictionnary listing all parameters without any sections (!= yaset format)
    '''
    # read to list
    with open(path2conf_model, 'r') as f:
        conf_model = f.read().splitlines()
        conf_model = [l for l in conf_model if l!='']
        conf_model = [l for l in conf_model if l[0]!='#' ]
    # build dictionnary
    conf_dict = {}
    for l in conf_model:
        if l[0] == '[':
            conf_dict[l] = ''
        else:
            k, v = l.split(" = ")
            conf_dict[k] = v
        if verbose:print(l)
    return conf_dict

def write_conf(conf_dict, path2newconf, verbose = False):
    new_conf = []
    for k,v in conf_dict.items():
        if k[0]=='[':
            new_conf.append(k+'\n')
        else:
            new_conf.append(k+' = '+v+'\n')
    # write the new conv file
    with open(path2newconf, 'w') as f:
            f.writelines(new_conf)
    if verbose:
        [print(l[:-1]) for l in new_conf]
    return 'written new yaset conf file at {}'.format(path2newconf)


def change_conf(model_conf, input_dict):
    '''input:
        model_conf, a dictionnary containing all the parameters for a yaset conf file
        input_dict, a dictionnray containing a subset of the yaset parameters to change
   output: complete changed conf file         
    '''
    # create a copy of the model_conf
    changed_conf = {}
    for k, v in model_conf.items():
        changed_conf[k] = v
    # apply changes
    for k, v in input_dict.items():
        changed_conf[k] = str(v)
    return changed_conf