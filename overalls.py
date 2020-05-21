''' general use functions and classes '''

def read_list_from_file(filename):
    """ Read the zip codes list from the csv file.
        
    :param filename: the name of the file
    :type filename: sting
    """
    with open(filename, "r") as z_list:
        return z_list.read().strip().split(',')
    
def key_list(d=dict):
    ''' Write the dict keys to a list and return that list 
    
    :param d: A python dictionary
    :return: A list fo the keys from the python dictionary
    '''
    
    keys = d.keys()
    key_list = []
    for k in keys:
        key_list.append(k)
    return key_list

def all_keys(d):
    ''' Get all the dicitonary and nested "dot format" nested dictionary keys
    from a dict, add them to a list, return the list.
    
    :param d: A python dictionary
    :return: A list of every key in the dictionary
    '''
    keys = []    
    for key, value in d.items():
        if isinstance(d[key], dict):
            for sub_key in all_keys(value):
                keys.append(f'{key}.{sub_key}')
        else:
            keys.append(str(key))
    return keys

def compare_dicts(one, the_other):
    ''' Compare the values of two dicts, key by common key. When the values are numbers
    return the difference, when strings return 0 if the strings are equal and 1
    if they are different, when dicts run this function, when NoneType set the
    value to None.
    *** When there is a key present in one and not the_other 
    :params one, the_other: dictionaries with the same set of keys and sub-keys
    :type one, the_other: dict
    '''
    
    delta = {}  # The delta document. Contains all the forecast errors
    
    for (k, v) in one.items():
        try:
            # Check and compare dictionaries according to their value type
            if type(v) == int or type(v) == float:
                if type(the_other[k]) == int or type(the_other[k]) == float:
                    delta[k] = v - the_other[k]
            elif type(v) == dict:
                delta[k] = make_delta(v, the_other[k])
            elif type(v) == str:
                if v == the_other[k]:
                    delta[k] = 0
                else:
                    delta[k] = 1
            elif type(v):
                delta[k] = None
        except KeyError as e:
            print(f'missing key..... {e}')
    return delta