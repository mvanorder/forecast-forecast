def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings.
    *credit to some stackoverflow respondant*
    """
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v)) 
        for k, v in dictionary.items())

def convert(data):
    ''' Convert data from one type to another
    *credit to some stackoverflow respondant*
    ### this has never been tested ###
    '''
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, int):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

