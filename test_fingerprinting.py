from localization import Localization

training_db    = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'training' )
test_db        = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'test' )
k = 5

for document in test_db.collection.find():
    location = training_db.localize( document['gateways'], k )
    print('The estimated location is x:'+str(location['x'])+' y:'+str(location['y']))
    print('The real location is x:'+str(document['x'])+' y:'+str(document['y']))
    if location['x'] == document['x'] and location['y'] == document['y']:
        print('CORRECT')
    else:
        print('WRONG')
