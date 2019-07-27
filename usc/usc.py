import sys
sys.path.append('../')
import re
import configparser
import os
import multiprocessing as mp
import pandas as pd


def create_rows(file):
    print("processing file: %s" % file)
    try:
        df = pd.read_csv(directory + file,
                         names=['timestamp', 'poi_id', 'duration'], sep=' ')
        df['impact'] = 1
        df['user'] = file
        return df
    except Exception as e:
        print("Unexpected error: {}".format(e))


def parallel(files):
    workers = (mp.cpu_count()-1)
    pool = mp.Pool(processes=(workers))
    data_frames = pool.map(create_rows, files)
    df = pd.concat(data_frames)
    df = df.reset_index(drop=True)
    return df


if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    dir_path = path['usc']

    directory = dir_path + 'USC_summer/'
    summer = ([file for file in os.listdir(directory)])
    df = parallel(summer)
    df.timestamp = df.timestamp.apply(
        lambda x: pd.to_datetime(int(x) + 1112313600, unit='s'))
    df.set_index('timestamp', inplace=True)
    df.to_pickle(dir_path + 'usc_summer.pkl')

    directory = dir_path + 'USC_spring/'
    spring = ([file for file in os.listdir(directory)])
    df = parallel(spring)
    df.timestamp = df.timestamp.apply(
        lambda x: pd.to_datetime(int(x) + 1136073600, unit='s'))
    df.to_pickle(dir_path + 'usc_spring.pkl')
