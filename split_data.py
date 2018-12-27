from localization import Localization

x_range = range(1,10)
y_range = range(1,10)
threshold = 70

fingerprint_db = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'no_ack_test' )
training_db    = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'training2' )
test_db        = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'test2' )

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
