import configparser
import json
import math
import multiprocessing as mp
from ctypes import Structure, c_double

import numpy as np
import osmnx as ox
import pandas as pd
from haversine import haversine

DISTANCE = 50


class Point(Structure):
    _fields_ = [('x', c_double), ('y', c_double)]


def get_point(point):
    return(point.x, point.y)


def impact(point1, point2):
    imp = 0.5 + \
        (0.5 * math.cos((math.pi * m_haversine(point1, point2) / DISTANCE)))
    return imp


def poi_impact(point):
    tmp = (None, 0)
    point = geo_to_point(point)
    p_list = pois_from_point(point, distance=DISTANCE)
    # get nearest POI and impact
    for poi in p_list.geometry.centroid.tolist():
        if DISTANCE >= m_haversine((point.x, point.y), (poi.x, poi.y)):
            imp = impact((point.x, point.y), (poi.x, poi.y))
            if tmp[1] < imp:
                tmp = (poi, imp)
    return tmp


def geo_to_point(geo_loc):
    return Point(geo_loc[0], geo_loc[1])


def m_haversine(point1, point2):
    return (haversine(point1, point2) * 1000)


def hav_tweet(point1, point2):
    if DISTANCE >= m_haversine(point1, point2):
        print('entrou!')
        return (point1, impact(point1, point2))


def pois_from_point(point, distance):
    p_list = all_pois.geometry.centroid
    north, south, east, west = ox.bbox_from_point(
        point=(point.y, point.x), distance=distance)
    pois_retrieved = all_pois[(p_list.y <= north) & (
        p_list.y >= south) & (p_list.x <= east) & (p_list.x >= west)]
    return pois_retrieved


def _apply_df(args):
    df, func, num, kwargs = args
    return num, df.apply(func, **kwargs)


def apply_by_multiprocessing(df, func, **kwargs):
    workers = (mp.cpu_count()-1)
    pool = mp.Pool(processes=(workers))
    result = pool.map(_apply_df, [(d, func, i, kwargs)
                                  for i, d in enumerate(np.array_split(df, workers))])
    pool.close()
    result = sorted(result, key=lambda x: x[0])
    return pd.concat([i[1] for i in result])


if __name__ == "__main__":
    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    dir_down = path['dir_down']

    place = "San Francisco"
    all_pois = ox.pois_from_place(place=place)

    filedir = "/Users/lucasso 1/Downloads/view.json"
    tweets = list()
    with open(filedir) as data_file:
        for line in data_file:
            tweet = json.loads(line)
            tweets.append([tweet['created_at'], tweet['user_screen_name'],
                           json.loads(tweet['st_asgeojson'])['coordinates']])

    df = pd.DataFrame(tweets)
    df.rename(columns={0: 'timestamp', 1: 'user', 2: 'location'}, inplace=True)
    del tweets

    # add poi location and impact for each tweet
    df['poi_loc'], df['impact'] = zip(
        *apply_by_multiprocessing(df['location'], poi_impact))

    df.to_pickle('poi_tw.pkl')

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index(['timestamp'], inplace=True)
