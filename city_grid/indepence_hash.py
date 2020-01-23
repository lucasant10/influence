import argparse
import numpy as np
from descartes import PolygonPatch
import matplotlib as mpl
from shapely.geometry import Polygon
import seaborn as sns
import osmnx as ox
import city_to_hash as hs
import geohash as gh
import pandas as pd


def geohash_to_polygon(geohash):
    box = gh.bbox(geohash)
    return Polygon([(box['e'], box['n']), (box['w'], box['n']), (box['w'], box['s']), (box['e'], box['s'])])


def colorFader(mix=0):
    c1 = 'white'
    c2 = 'green'
    c1 = np.array(mpl.colors.to_rgb(c1))
    c2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)


if __name__ == "__main__":

   try:
        parser = argparse.ArgumentParser(
            description='Plot City Independence Grid')
        parser.add_argument('-p', '--place', required=True)
        parser.add_argument('-d', '--directory', required=True)
        parser.add_argument('-t', '--tweet', required=True)

        args = parser.parse_args()
        city_name = args.place
        directory = args.directory
        tw_bool = bool(args.tweet)

        if tw_bool:
            city_name.replace('poi_tw_', '')

        city = ox.gdf_from_place(city_name)
        df = pd.read_pickle(directory + "%s.pkl" % city_name)
        df2 = pd.read_pickle(
            directory + ("{0}/independence_{0}.pkl".format(city_name)))

        df.poi_id = df.poi_id.astype('str')
        df2.poi_id = df2.poi_id.astype('str')

        df3 = pd.merge(df, df2, on='poi_id', how="left")

        df3['geohash'] = df3.apply(lambda x: gh.encode(
            x['lat'], x['long'], precision=6), axis=1)
        df_geo = df3.groupby("geohash").agg("power").sum().reset_index()

        geo_list = hs.geohashes(city.iloc[0].geometry, precision=6)
        df_city = pd.DataFrame(geo_list, columns=["geohash"])
        df_heat = pd.merge(df_city, df_geo, on='geohash', how='left')
        df_heat.rename(columns={"power": "total"}, inplace=True)
        df_heat.fillna(0, inplace=True)

        fig, ax = ox.plot_shape(city)
        higher = df_heat.total.max()
        for index, row in df_heat.iterrows():
            ax.add_patch(PolygonPatch(geohash_to_polygon(row['geohash']), facecolor=colorFader(
                (row['total']/higher)), linewidth=0, alpha=0.7))

        fig.savefig(directory + "{0}/{0}_indep_grid.png".format(city_name))

    except Exception as e:
        print(e)
