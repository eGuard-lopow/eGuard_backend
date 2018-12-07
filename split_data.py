from localization import Localization

x_range = range(1,10)
y_range = range(1,10)
threshold = 30

fingerprint_db = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'fingerprints3' )
training_db    = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'training' )
test_db        = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'test' )

for x in x_range:
    for y in y_range:
        counter = 0
        for document in fingerprint_db.collection.find({'x':x,'y':y}):
            print('Document: '+str(document))
            if counter < threshold:
                training_db.collection.insert_one(document)
                print('Document copied to training database')
            else:
                test_db.collection.insert_one(document)
                print('Document copied to test database')
            counter+=1
