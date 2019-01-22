from __future__ import print_function
from localization import Localization

training_db    = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'training2' )
test_db        = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'test2' )

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
    print('{ k: '+str(k)+' } \tCorrect answers: '+str(amount_correct)+' \tWrong answers: '+str(amount_wrong)+' \t=> '+str(round(ratio*100,2))+'%', end='')

    amount_correct = 0
    amount_wrong = 0
    for document in test_db.collection.find():
        location = training_db.localize_exp( document['gateways'], k )
        # print('The estimated location is x:'+str(location['x'])+' y:'+str(location['y']))
        # print('The real location is x:'+str(document['x'])+' y:'+str(document['y']))
        if round(location['x']) == document['x'] and round(location['y']) == document['y']:
            # print('CORRECT')
            amount_correct += 1
        else:
            # print('WRONG')
            amount_wrong += 1
    ratio = float(amount_correct)/(amount_correct+amount_wrong)
    print('\t{ exp } \tCorrect answers: '+str(amount_correct)+' \tWrong answers: '+str(amount_wrong)+' \t=> '+str(round(ratio*100,2))+'%', end='')

    amount_correct = 0
    amount_wrong = 0
    for document in test_db.collection.find():
        location = training_db.localize_log( document['gateways'], k )
        # print('The estimated location is x:'+str(location['x'])+' y:'+str(location['y']))
        # print('The real location is x:'+str(document['x'])+' y:'+str(document['y']))
        if round(location['x']) == document['x'] and round(location['y']) == document['y']:
            # print('CORRECT')
            amount_correct += 1
        else:
            # print('WRONG')
            amount_wrong += 1
    ratio = float(amount_correct)/(amount_correct+amount_wrong)
    print('\t{ log } \tCorrect answers: '+str(amount_correct)+' \tWrong answers: '+str(amount_wrong)+' \t=> '+str(round(ratio*100,2))+'%', end='')

    amount_correct = 0
    amount_wrong = 0
    for document in test_db.collection.find():
        location = training_db.localize_sorensen( document['gateways'], k )
        # print('The estimated location is x:'+str(location['x'])+' y:'+str(location['y']))
        # print('The real location is x:'+str(document['x'])+' y:'+str(document['y']))
        if round(location['x']) == document['x'] and round(location['y']) == document['y']:
            # print('CORRECT')
            amount_correct += 1
        else:
            # print('WRONG')
            amount_wrong += 1
    ratio = float(amount_correct)/(amount_correct+amount_wrong)
    print('\t{ sor } \tCorrect answers: '+str(amount_correct)+' \tWrong answers: '+str(amount_wrong)+' \t=> '+str(round(ratio*100,2))+'%')


for k in range(1,20):
    test(k)
