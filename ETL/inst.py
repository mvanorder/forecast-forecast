''' define the instant class and some useful scripts related to them '''

class instant:

    def __init__(instant, zipcode, forecasts, observation):
        {'instant': instant,
        'zipcode': zipcode,
        'forecasts': forecasts,
        'observation': observation
        }


def itslegit(instant):
    ''' check the instant's weathers array for count. if it is 40, then the document is returned

    :param instant: the instant docuemnt to be legitimized
    :type instant: dictionary
    '''

    if len(instant['weathers']) == 40:
        return True
    else:
        return False

def find_legit(collection):
    ''' find the 'legit' instants within the collection specified

    :param collection: database collection
    :type collection: pymongo.collection.Collection
    :return: list of documents
    '''

    return [item for item in collection.find({}) if islegit(item)]

def load_legit(collection):
    ''' load the 'legit' instants to the remote database 

    :param collection: the collection you want to pull instants from
    :type collection: pymongo.collection.Collection
    '''
    from db_ops import Client, dbncol
    from config import uri, host, port

    legit_list = getlegit(collection)
    client = Client(host, port)
    col = dbncol(client, 'legit_inst', 'owmap')
    col.insert_many(legit_list)

def test_load_legit(collection):
    ''' load the 'legit' instants to the remote database 

    :param collection: the collection you want to pull instants from
    :type collection: pymongo.collection.Collection
    '''
    from db_ops import Client, dbncol
    from config import host, port

    legit_list = getlegit(collection)
    client = Client(uri)
    col = dbncol(client, 'legit_inst', 'owmap')
    col.insert_many(legit_list)
    