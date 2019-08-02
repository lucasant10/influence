import argparse
import reverse_geocode
import pandas as pd
import os
import configparser
import sys
sys.path.append('../')


def get_location(lat, long):
    try:
        loc = reverse_geocode.get((lat, long))
        return (loc['city'], loc['country'])
    except Exception as e:
        print("Unexpected error: {}".format(e))
        return (None, None)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Get offline locations from coordinate')
    parser.add_argument('-d', '--dir', required=True)
    parser.add_argument('-f', '--file', required=True)
    args = parser.parse_args()

    directory = args.dir
    file = args.file

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    try:
        directory = path[directory]
        df = pd.read_pickle(directory + file)
        print("processing file: %s" % file)
        df['city'], df['country'] = zip(
            *df.apply(lambda x: get_location(str(x['lat']), str(x['long'])), axis=1))
        print("saving file: %s" % file)
        df.to_pickle(directory + file)
    except Exception as e:
        print("Unexpected error: {}".format(e))
    
    #python coord_2_locations.py -f 'foursquare.pkl' -d 'foursquare'