import json
import math
import multiprocessing as mp
import argparse
import numpy as np
import osmnx as ox
import pandas as pd
from haversine import haversine
import networkx as nx
from shapely.geometry import Point
import os
DISTANCE = 30
PLACE = ''
FILE = ''


def get_point(point):
    return(point.x, point.y)


def impact(point1, point2):
    imp = 0.5 + \
        (0.5 * math.cos((math.pi * m_haversine(point1, point2) / DISTANCE)))
    return imp


def poi_impact(point):
    tmp = (None, 0, None, None)
    point = Point(point)
    poi_list = pois_from_point(point, distance=(DISTANCE+5))
    # get nearest POI and impact
    for index, poi in poi_list.geometry.centroid.items():
        if DISTANCE >= m_haversine((point.x, point.y), (poi.x, poi.y)):
            imp = impact((point.x, point.y), (poi.x, poi.y))
            if tmp[1] < imp:
                amenity = poi_list.loc[index].amenity
                tmp = (poi, imp, index, amenity)
    return tmp


def m_haversine(point1, point2):
    return (haversine(point1, point2) * 1000)


def pois_from_point(point, distance):
    dist = p_list.apply(lambda place: place.distance(point)*100000)
    return all_pois[dist <= distance]


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

    parser = argparse.ArgumentParser(description='Calculate Impact of POI')
    parser.add_argument('-p', '--place', required=True)
    parser.add_argument('-d', '--distance', default=DISTANCE, required=True)
    parser.add_argument('-f', '--file', required=True)
    args = parser.parse_args()
    
    PLACE = args.place
    DISTANCE = int(args.distance)
    FILE = args.file 

    print('Load POIs')
    all_pois = get_pois(PLACE)
    all_pois = all_pois.groupby('amenity').filter(lambda x: len(x) > 5)
    remove = ['toilets', 'waste_basket', 'telephone','bench','fountain',
              'vending_machine', 'recycling', 'table', 'drinking_water','atm']
    all_pois = all_pois[~all_pois.amenity.isin(remove)]
    p_list = all_pois.geometry.centroid

    print('processing csv file!!')
    tweets = list()
    with open(FILE) as data_file:
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
    df['poi_loc'], df['impact'], df['poi_id'], df['amenity'] = zip(
        *apply_by_multiprocessing(df['location'], poi_impact))

    df = df.drop(df[pd.isna(df.poi_id)].index)

    df.set_index(['timestamp'], inplace=True)
    df['hour'] = df.index.hour

    print('save file')
    df.to_pickle('poi_tw_%s.pkl' % PLACE.replace(' ', '_'))
