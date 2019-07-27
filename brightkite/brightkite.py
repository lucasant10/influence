import sys
sys.path.append('../')
import configparser
import os
import pandas as pd

if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['brightkite']
    df = pd.read_csv(directory + 'Brightkite_totalCheckins.txt', sep='\t', names=['user','timestamp','lat','long','poi_id'])
    df.timestamp = pd.to_datetime(df.timestamp)
    df['impact'] = 1
    df.set_index('timestamp', inplace=True)
    df.to_pickle(directory + 'brightkite.pkl')
