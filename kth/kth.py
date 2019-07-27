import sys
sys.path.append('../')
import re
import configparser
import os
import multiprocessing as mp
import pandas as pd


def create_rows(file):
    print("processing file: %s" %file)
    try:
        df = pd.read_csv(directory + file, compression='gzip')
        df.timestamp = pd.to_datetime(df.timestamp)
        return df
    except Exception as e:
        print("Unexpected error: {}".format(e))

if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['kth']
    files = ([file for file in os.listdir(directory) if file.endswith('.gz')])
    workers = (mp.cpu_count()-1)
    pool = mp.Pool(processes=(workers))
    data_frames = pool.map(create_rows, files)
    df = pd.concat(data_frames) 
    df = df.reset_index(drop=True)
    df.rename(columns={"client": "user", "AP": "poi_id"}, inplace=True)
    df['impact'] = 1
    df.set_index('timestamp', inplace=True)
    df.to_pickle(directory + 'kth.pkl')
