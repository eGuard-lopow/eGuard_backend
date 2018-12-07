from localization import Localization

training_db    = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'training' )
test_db        = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'test' )

def test(k):
    amount_correct = 0
    amount_wrong = 0
    for document in test_db.collection.find():
        location = training_db.localize( document['gateways'], k )
        # print('The estimated location is x:'+str(location['x'])+' y:'+str(location['y']))
        # print('The real location is x:'+str(document['x'])+' y:'+str(document['y']))
        if round(location['x']) == document['x'] and round(location['y']) == document['y']:
            # print('CORRECT')
            amount_correct += 1
        else:
            # print('WRONG')
            amount_wrong += 1
    ratio = float(amount_correct)/(amount_correct+amount_wrong)
    print('{ k: '+str(k)+' } \tCorrect answers: '+str(amount_correct)+' \tWrong answers: '+str(amount_wrong)+' \t=> '+str(round(ratio*100,2))+'%')

for k in range(1,20):
    test(k)
