import sys
from localization import Localization

x_range = range(0,10)
y_range = range(0,10)

if len(sys.argv) > 1:
    collection_name = str(sys.argv[1])
else:
    collection_name = 'full2'

fingerprint_db = Localization( 'mongodb://localhost:27017/', 'd7mockup', collection_name )

for x in x_range:
    for y in y_range:
        counter = 0
        amount_gateways = { 1:0, 2:0, 3:0, 4:0 }
        for document in fingerprint_db.collection.find({'x':x,'y':y}):
            counter += 1
            amount_gateways[len(document['gateways'])] += 1
        if counter > 0:
            print('location ['+str(x)+','+str(y)+'] has '+str(counter)+' values')
            for gateways in range(1,5):
                print('    '+str(gateways)+' gateways: '+str(amount_gateways[gateways]))
