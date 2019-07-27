import sys
sys.path.append('../')
import re
import configparser
import os
import multiprocessing as mp
import pandas as pd


def create_rows(file):
    print("processing file: %s" %file)
    city = file.split('.')[0].split('_')[-1]
    try:
        df = pd.read_table(directory + file, encoding = "ISO-8859-1", names=['user','poi_id','category','catname','lat','long','offset','timestamp'])
        df.timestamp = pd.to_datetime(df.timestamp)
        df.timestamp = df.timestamp + df.offset.apply(lambda x: pd.Timedelta(x, unit='m'))
        df['impact'] = 1
        df.set_index('timestamp', inplace=True)
        return (df,city)
    except Exception as e:
        print("Unexpected error: {}".format(e))

if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['foursquare']

    files = ([file for file in os.listdir(directory) if file.endswith('.tsv')])
    workers = (mp.cpu_count()-1)
    pool = mp.Pool(processes=(workers))
    tuples = pool.map(create_rows, files)
    for df, city in tuples:
        df.to_pickle(directory + '%s.pkl' % city)
