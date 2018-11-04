import sys, os
import argparse

from bitstring import ConstBitStream
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'pyd7a'))
from pyd7a.d7a.alp.parser import Parser as AlpParser

def parse_alp(raw):
    hexstring = raw.strip().replace(' ', '')
    data = bytearray(hexstring.decode("hex"))
    output = str(AlpParser().parse(ConstBitStream(data), len(data)))
    print("output: ",output)
    output = output.split("\n\t")
    # print('list',output)
    output = output[2]
    output = output.replace("\taction: ReturnFileData: ", "")
    # print('file',output)
    data = output.split(', ', 3)[3]
    # print('data',data)
    data = data.split('=')[1]   # 'data=['1', '2', '3']' to '['1', '2', '3']'
    # data = data.replace('[','').replace(']','')  # remove brackets
    data = data[1:-1]  # remove brackets
    data = data.split(', ')   #
    # print('data',data)
    data = map(int, data)   # cast strings to integers
    return data
