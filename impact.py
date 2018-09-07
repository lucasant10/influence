import json
import math
import multiprocessing as mp

import numpy as np
import osmnx as ox
import pandas as pd
from haversine import haversine
import networkx as nx
from shapely.geometry import Point
import os
DISTANCE = 50


def get_point(point):
    return(point.x, point.y)


def impact(point1, point2):
    imp = 0.5 + \
        (0.5 * math.cos((math.pi * m_haversine(point1, point2) / DISTANCE)))
    return imp


def poi_impact(point):
    tmp = (None, 0, None)
    point = Point(point)
    poi_list = pois_from_point(point, distance=(DISTANCE+5))
    # get nearest POI and impact
    for index, poi in poi_list.geometry.centroid.items():
        if DISTANCE >= haversine((point.x, point.y), (poi.x, poi.y)):
            imp = impact((point.x, point.y), (poi.x, poi.y))
            if tmp[1] < imp:
                tmp = (poi, imp, index)
    return tmp

def m_haversine(point1, point2):
    return (haversine(point1, point2) * 1000)

def pois_from_point(point, distance):
    dist = p_list.apply(lambda place: place.distance(point)*100000)
    return all_pois[dist <= distance]
    # xmin, ymin, xmax, ymax= ox.bbox_from_point(point=(point.y, point.x), distance=distance)
    # dist = p_list.cx[xmin:xmax, ymin:ymax].index
    # return all_pois.loc[dist]

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

def get_pois(place):
    poi_file = "%s_pois.pkl" % place.replace(' ', '_')
    if os.path.exists(poi_file):
        return pd.read_pickle(poi_file)
    else:
        return ox.pois_from_place(place=place)

if __name__ == "__main__":
    print('Load POIs')
    place = "San Francisco"
    all_pois = get_pois(place)
    p_list = all_pois.geometry.centroid

    print('processing csv file!!')
    filedir = "/Users/lucasso 1/Downloads/view.json"
    tweets = list()
    with open(filedir) as data_file:
        for line in data_file:
            tweet = json.loads(line)
            tweets.append([tweet['created_at'], tweet['user_screen_name'],
                           json.loads(tweet['st_asgeojson'])['coordinates']])

    df = pd.DataFrame(tweets)
    df.rename(columns={0: 'timestamp', 1: 'user', 2: 'location'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    del tweets

    # add poi location and impact for each tweet
    print('add poi location!')
    #df['poi_loc'], df['impact'], df['poi_id'] = zip(*df.apply(lambda row: poi_impact(row['location']), axis=1))
    df['poi_loc'], df['impact'], df['poi_id'] = zip(
        *apply_by_multiprocessing(df['location'], poi_impact))

    df = df.drop(df[pd.isna(df.poi_id)].index)

    df.set_index(['timestamp'], inplace=True)
    df['hour'] = df.index.hour

    print('save file')
    df.to_pickle('poi_tw.pkl')