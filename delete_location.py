import pymongo

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['d7mockup']
mycol = mydb['dipole']

myquery = { 'x': 4, 'y': 0 }

mycol.delete_many(myquery)
