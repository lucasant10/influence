import sys
sys.path.append('../')
import re
import configparser
import os
import multiprocessing as mp
import pandas as pd


def create_rows(file):
    print("processing file: %s" %file)
    user = file.split(".")[0]
    try:
        df = pd.read_csv(directory + file, names=['timestamp', 'poi_id'], sep='\t',  header=None)
        df['user'] = user
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.drop(df[df.poi_id=='OFF'].index, inplace=True)
        return df
    except Exception as e:
        print("Unexpected error: {}".format(e))

if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['dartmouth']

    files = ([file for file in os.listdir(directory) if file.endswith('.mv')])
    workers = (mp.cpu_count()-1)
    pool = mp.Pool(processes=(workers))
    data_frames = pool.map(create_rows, files)
    # lista = list()
    # for file in files:
    #     lista.append(create_rows(file))
    df = pd.concat(data_frames) 
    df = df.reset_index(drop=True)
    df['impact'] = 1
    df['poi_id'] = df.poi_id.apply(lambda x: re.split(r'AP\d*',x)[0])
    df.set_index('timestamp', inplace=True)
    df.to_pickle(directory + 'dartmouth.pkl')
