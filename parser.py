import sys, os
import argparse

from bitstring import ConstBitStream
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'pyd7a'))
from pyd7a.d7a.alp.parser import Parser as AlpParser

def parse_alp(raw):

    output = {}     # create empty dictionary

    # ------------------------------
    # Decode message and cleanup
    # ------------------------------
    hex = raw.strip().replace(' ', '')      # cleaning up of raw data
    bin = bytearray(hex.decode('hex'))     # decode of raw data
    message = str(AlpParser().parse(ConstBitStream(bin), len(bin))) # parse binary data readable message
    # print('message_input',message)
    message = message.split('ReturnFileData: ')[1]  # remove 'Command with tag xxx (executing)\n\tactions:\n\t\taction: ReturnFileData: ' at front of string
    message = message.replace('\n\tinterface status: ', ', ')
    message = message[:-1] # remove '\n' at end
    # print('message_filtered',message)

    # ------------------------------
    # Extract data
    # ------------------------------
    data = message.split('[')[1].split(']')[0] # ['stuff1=foo, data=','1, 2, 3',', stuff2=bar']
    data = data.split(', ')    # ['1', '2', '3']
    data = map(int, data)   # cast str to int [1, 2, 3]
    output['data']=data # add to dictionary
    # print('data',data)
    message = message.split('[')[0][:-7]+message.split(']')[1] # cleaning up after data extraction ['stuff1=foo, stuff2=bar']
    # print('message_after_data_extraction',message)

    # ------------------------------
    # Add other fields to dictionary
    # ------------------------------
    message = message.split(', ') # ['stuff1=foo','stuff2=bar']
    for item in message:
        item_split = item.split('=',1) # split key and value ['stuff1','foo']
        output[item_split[0]]=item_split[1] # add to dictionary

    return output   # return dictionary
