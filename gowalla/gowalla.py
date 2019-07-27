import sys
sys.path.append('../')
import configparser
import os
import pandas as pd

if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['gowalla']
    df = pd.read_csv(directory + 'gowalla_checkins.csv', names=['user','poi_id','timestamp'])
    df.drop(0, inplace=True)
    df.timestamp = pd.to_datetime(df.timestamp)
    df['impact'] = 1
    df.set_index('timestamp', inplace=True)
    df.to_pickle(directory + 'gowalla.pkl')
