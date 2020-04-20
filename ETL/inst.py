''' define the instant class and some useful scripts related to them '''

class instant:

    __self__ = {'instant': int,
                'zipcode': str,
                'forecasts': list,
                'observations': dict
                }


def islegit(instant):
    ''' check the instant's weathers array for count. if it is 40, then the document should be loaded to the remote database

    :param instant: the instant docuemnt to be legitimized
    :type instant: dictionary
    '''

    if len(instant['weathers']) == 40:
        return True
    else:
        return False

def getlegit(collection):
    ''' find the 'legit' instants within the collection specified

    :param collection: database collection
    :type collection: pymongo.collection.Collection
    :return: list of documents
    '''

    return [item if islegit(item) for item in collection.find({})]

def loadlegit(collection):
    ''' load the 'legit' instants to the remote database 

    :param collection: the collection you want to pull instants from
    :type collection: pymongo.collection.Collection
    '''
    from db_ops import Client, dbncol
    from config import uri

    legit_list = getlegit(collection)
    client = Client(uri)
    col = dbncol(client, 'legit_inst', 'owmap')
    col.insert_many(legit_list)
    