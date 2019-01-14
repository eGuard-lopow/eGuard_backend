import pymongo
import numpy as np

class Localization:

    gateway_ids = ['4337313400210032', '433731340023003d', '42373436001c0037', '463230390032003e']

    def __init__( self, host, db, collection ):
        self.mongo_client = pymongo.MongoClient(str(host))
        # db_list = self.mongo_client.list_database_names()
        # print(db_list)
        # if str(db) in db_list:
        #     print('The database exists.')
        self.db = self.mongo_client[str(db)]
        # print(self.db.list_collection_names())
        self.collection = self.db[str(collection)]

    def train( self, x_value, y_value, rx_values ):
        document = { 'x': x_value,'y': y_value, 'gateways': rx_values }
        self.collection.insert_one(document)

    def localize( self, rx_values, k ):
        probablistic = []
        for document in self.collection.find():
            diff = []
            for gateway_id in self.gateway_ids:
                if gateway_id not in rx_values:
                    rx_values[gateway_id] = 200 # out of range
                if gateway_id not in document['gateways']:
                    document['gateways'][gateway_id] = 200 # out of range
                diff.append( int(rx_values[gateway_id])-int(document['gateways'][gateway_id]) )
            # print(diff)
            rms = np.sqrt(np.mean(np.square(diff)))
            # print(rms)
            probablistic.append({'x': document['x'],'y': document['y'],'rms':rms})
        # print(probablistic)

        # -------------------------
        # k-nearest neighbors
        # -------------------------
        ordered_locations = sorted(probablistic, key = lambda i: i['rms']) # sort on RMS value
        nearest_neighbors = ordered_locations[:k]
        # print('knn: '+str(nearest_neighbors))

        # -------------------------
        # Weighted Average
        # -------------------------
        x = 0
        y = 0
        total_weight = 0
        for fingerprint in nearest_neighbors:
            if fingerprint['rms']==0:
                weight = 100
            else:
                weight = 1/fingerprint['rms']
            x += int(fingerprint['x']) * weight
            y += int(fingerprint['y']) * weight
            total_weight += weight
        x=x/total_weight
        y=y/total_weight
        return { 'x': x, 'y': y }

    def localize_exp( self, rx_values, k ):
        probablistic = []
        for document in self.collection.find():
            diff = []
            for gateway_id in self.gateway_ids:
                if gateway_id not in rx_values:
                    rx_values[gateway_id] = 200 # out of range
                if gateway_id not in document['gateways']:
                    document['gateways'][gateway_id] = 200 # out of range
                diff.append( int(np.exp(rx_values[gateway_id]))-int(np.exp(document['gateways'][gateway_id])) )
            # print(diff)
            rms = np.sqrt(np.mean(np.square(diff)))
            # print(rms)
            probablistic.append({'x': document['x'],'y': document['y'],'rms':rms})
        # print(probablistic)

        # -------------------------
        # k-nearest neighbors
        # -------------------------
        ordered_locations = sorted(probablistic, key = lambda i: i['rms']) # sort on RMS value
        nearest_neighbors = ordered_locations[:k]
        # print('knn: '+str(nearest_neighbors))

        # -------------------------
        # Weighted Average
        # -------------------------
        x = 0
        y = 0
        total_weight = 0
        for fingerprint in nearest_neighbors:
            if fingerprint['rms']==0:
                weight = 100
            else:
                weight = 1/fingerprint['rms']
            x += int(fingerprint['x']) * weight
            y += int(fingerprint['y']) * weight
            total_weight += weight
        x=x/total_weight
        y=y/total_weight
        return { 'x': x, 'y': y }

    def localize_log( self, rx_values, k ):
        probablistic = []
        for document in self.collection.find():
            diff = []
            for gateway_id in self.gateway_ids:
                if gateway_id not in rx_values:
                    rx_values[gateway_id] = 200 # out of range
                if gateway_id not in document['gateways']:
                    document['gateways'][gateway_id] = 200 # out of range
                diff.append( int(np.log(rx_values[gateway_id]))-int(np.log(document['gateways'][gateway_id])) )
            # print(diff)
            rms = np.sqrt(np.mean(np.square(diff)))
            # print(rms)
            probablistic.append({'x': document['x'],'y': document['y'],'rms':rms})
        # print(probablistic)

        # -------------------------
        # k-nearest neighbors
        # -------------------------
        ordered_locations = sorted(probablistic, key = lambda i: i['rms']) # sort on RMS value
        nearest_neighbors = ordered_locations[:k]
        # print('knn: '+str(nearest_neighbors))

        # -------------------------
        # Weighted Average
        # -------------------------
        x = 0
        y = 0
        total_weight = 0
        for fingerprint in nearest_neighbors:
            if fingerprint['rms']==0:
                weight = 100
            else:
                weight = 1/fingerprint['rms']
            x += int(fingerprint['x']) * weight
            y += int(fingerprint['y']) * weight
            total_weight += weight
        x=x/total_weight
        y=y/total_weight
        return { 'x': x, 'y': y }
