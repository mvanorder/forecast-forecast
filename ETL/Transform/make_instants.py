''' Make the instant documents. Pull all documents from the "forecasted" and the "observed" database collections. Sort those
documents according to the type: forecasted documents get their forecast arrays sorted into forecast lists within the documents 
with having the same zipcode and instant values, observed documents are inserted to the same document corrosponding to the 
zipcode and instant values. '''


import time

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection, ReturnDocument
from pymongo.errors import ConnectionFailure, InvalidDocument, DuplicateKeyError, OperationFailure, ConfigurationError
from urllib.parse import quote

from config import user, password, socket_path


# use the local host and port for all the primary operations
port = 27017
host = 'localhost'
# use the remote host and port when the instant document is complete and is ready for application
password = quote(password)    # url encode the password for the mongodb uri
uri = "mongodb+srv://%s:%s@%s" % (user, password, socket_path)
print(uri)


def Client(host=None, port=None, uri=None):
    ''' Create and return a pymongo MongoClient object. Connect with the given parameters if possible, switch to local if the
    remote connection is not possible, using the default host and port.
    
    :param host: the local host to be used. defaults within to localhost
    :type host: sting
    :param port: the local port to be used. defaults within to 27017
    :type port: int
    :param uri: the remote server URI. must be uri encoded
    type uri: uri encoded sting'''
    
    if host and port:
        try:
            client = MongoClient(host=host, port=port)
            return client
        except ConnectionFailure:
            # connect to the remote server if a valid uri is given
            if uri:
                print('caught ConnectionFailure on local server. Trying to make it with remote')
                client = MongoClient(uri)
                print(f'established remote MongoClient on URI={uri}')
                return client
            print('caught ConnectionFailure on local server. Returning None')
            return None
    elif uri:
        # verify that the connection with the remote server is active and switch to the local server if it's not
        try:
            client = MongoClient(uri)
            return client
        except ConfigurationError:
            print(f'Caught configurationError in client() for URI={uri}. It was likely triggered by a DNS timeout.')
            client = MongoClient(host=host, port=port)
            print('connection made with local server, even though you asked for the remote server')
            return client

def find_data(client, database, collection, filters={}):
    ''' Find the items in the specified database and collection using the filters.

    :param client: a MongoClient instance
    :type client: pymongo.MongoClient
    :param database: the name of the database to be used. It must be a database name present at the client
    :type database: str
    :param collection: the database collection to be used.  It must be a collection name present in the database
    :type collection: str
    :param filters: the parameters used for filtering the returned data. An empty filter parameter returns the full collection
    :type filters: dict
    
    :return: the result of the query
    :type: pymongo.cursor.CursorType
    '''

    db = Database(client, database)
    col = Collection(db, collection)
    return col.find(filters).batch_size(100)

def make_forecasts_list(forecasts):
    ''' This only needs to be used while finding documents previously loaded to collections during the development stage. It
    is intended to take a pymongo coursor object holding forecasts found by the filtered find_data() function from this
    module. If it gets a proper weather-type object it returns it unmodified. If it gets a list of properly formed weather-type 
    objects it checks for the different varieties of objects inserted to the database through the course of developent to 
    create a list of forecast lists. **It was initially intended that the returned list of forecast lists would be pushed into 
    the sort_casts() function.

    :param forecasts: a list of forecasted documents or pymongo coursor object pointing to the find() results from a
        db.forecasted query.
    :type forecasts: list or pymongo.cursor.CursorType
    
    :return casts: the unaltered forecasts object if it's a dict OR the weathers arrays of the argument list items as a list
        of lists
    :type casts: dict or list
    '''

    casts = []
    if type(forecasts) == dict:
        return forecasts
    elif type(forecasts) == list:
        for cast in forecasts:
            if type(cast['weathers'])==list:
                casts.append(cast['weathers'])
                continue
            elif type(cast['five_day'])==list:
                casts.append(cast['five_day'])
                continue
            else:
                casts.append(cast['five_day']['weathers'])
        return casts

def load_weather(data, client, database, collection):
    ''' Load data to specified database collection. This determines the appropriate way to process the load depending on the
    collection to which it should be loaded. Data is expected to be a weather-type dictionary. When the collection is "instants"
    the data is appended the specified object's forecasts array in the instants collection; when the collection is either
    "forecasted" or "observed" the object is insterted uniquely to the specified collection. Also checks for a preexisting
    document with the same instant and zipcode, then updates it in the case that there was already one there.

    :param data: the dictionary created from the api calls
    :type data: dict
    :param client: a MongoClient instance
    :type client: pymongo.MongoClient
    :param database: the database to be used
    :type database: str
    :param collection: the database collection to be used
    :type collection: str
    ''' 
    global code
    # decide how to handle the loading process depending on where the document will be loaded.
    if collection == 'instant' or collection == 'test_instants' or collection == 'instants_temp':
        # set the appropriate database collections, filters and update types
        db = Database(client, database)
        col = Collection(db, collection)
        # check for old version conditions
        if 'reference_time' in data:
            filters = {'zipcode':data['zipcode'], 'instant':data['reference_time']}
            data['time_to_instant'] = data.pop('reference_time') - data.pop('reception_time')
            data.pop('zipcode')
        elif 'zipcode' not in data: #added for old data processing
            filters = {'zipcode': code, 'instant':data['instant']} #added for old data processing
            data['time_to_instant'] = data.pop('instant') - data.pop('reception_time') #added for old data processing
            data.pop('zipcode') #added for old data processing
        else:
            filters = {'zipcode':data['zipcode'], 'instant':data['instant']}            
            data['time_to_instant'] = data.pop('instant') - data.pop('reception_time')
            data.pop('zipcode')
        if 'Weather' in data:
            if 'time_to_instant' not in data['Weather']: #added for old data processing
                data['Weather']['time_to_instant'] = data['time_to_instant'] #added for old data processing
                data['Weather'].pop('reference_time') #added for old data processing
            # add the weather and coordiantes to the instant document
            updates = {'$set': {'weather': data['Weather'], 'coordinates':data['coordinates']}}
        else:
            updates = {'$push': {'forecasts': data}} # append the forecast object to the forecasts list
        try:
            col.find_one_and_update(filters, updates,  upsert=True)
        except DuplicateKeyError:
            return(f'DuplicateKeyError, could not insert data into {collection}.')
    elif collection == 'observed' or collection == 'forecasted':
        db = Database(client, database)
        col = Collection(db, collection)
        try:
            col.insert_one(data)
        except DuplicateKeyError:
            return(f'DuplicateKeyError, could not insert data into {collection}.')

def sort_casts(forecasts, client, database='OWM', collection='instant'):
    ''' Take the array of forecasts from the five_day forecasts and sort them into the documents of the specified database
    collection.

    :param forecasts: the forecasts from five_day()-  They come in a list of 40, one for each of every thrid hour over five days
    :type forecasts: list- expecting a list of forecast objects
    :param code: the zipcode
    :type code: string
    :param client: the mongodb client
    :type client: pymongo.client.MongoClient
    :param database: the name of the database to be used. It must be a database name present at the client
    :type database: string
    :param collection: the database collection to be used.  It must be a collection name present in the database
    :type collection: string
    '''

    # update each forecast and insert it to the instant document with the matching instant_time and zipcode
    for forecast in forecasts:
        load_weather(forecast, client, database, collection)


if __name__ == "__main__":
    client = Client(host=host, port=port)
    # set the database and collection to pull from the database of choice
    database = "OWM"
    collection = "forecasted"
    forecasts = find_data(client, database, collection)
    collection = "observed"
    observations = find_data(client, database, collection)
    collection = 'instants_temp' # set the collection to be updated
    start = time.time()
    f, o = 0, 0
    sorted_casts = []
    sorted_obs = []
    # sort the forecasts into instants
    for forecast in forecasts[:450]:
        if f%1000 == 0:
            print(f)
        casts = forecast['weathers'] # use the weathers array from the forecast
        if 'zipcode': #added for old data processing
            code = forecast['zipcode'] #added for old data processing
            reception_time = forecast['reception_time'] #added for old data processing
        for cast in casts:
            if 'zipcode' not in cast: #added for old data processing
                cast['zipcode'] = code #added for old data processing
                cast['reception_time'] = reception_time #added for old data processing
            load_weather(cast, client, database=database, collection=collection)
        f+=1
        sorted_casts.append(forecast['_id'])
    # set the observations into their respective instants
    for observation in observations[450:]:
        if o%1000 == 0:
            print(o)
        load_weather(observation, client, database=database, collection=collection)
        o+=1
        sorted_obs.append(observation['_id'])
    print(f'{time.time()-start} seconds passed while sorting each weathers array and adding observations to instants')
    with open('sorted_casts_from_testdb.txt', 'w') as f:
        for entry in sorted_casts:
            f.write(str(entry)+'\n')
    with open('sorted_obs_from_testdb.txt', 'w') as f:
        for entry in sorted_obs:
            f.write(str(entry)+'\n')
    print('now move the documents to the archive collections')