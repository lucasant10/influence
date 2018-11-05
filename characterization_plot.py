import matplotlib matplotlib.use('agg')
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot dataset characterization')
    parser.add_argument('-p', '--place', required=True)
    parser.add_argument('-f', '--file', required=True)
    args = parser.parse_args()
    
    pd_file = args.file 
    place = args.place

    directory = 'figures/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    df = pd.read_pickle(pd_file)

    group = df.groupby(['user']).count()
    f,ax = plt.subplots()
    sns.distplot(group.poi_id,kde=False, hist_kws={'histtype':'stepfilled'}, ax=ax, bins=200)
    ax.set(xscale="log", yscale="log")
    ax.set_ylabel('# user')
    ax.set_xlabel('# tweets per user')
    plt.title('%s histogram' % place)
    plt.savefig(directory +'hist_tw_user_%s.png' % place.replace(' ', '_'))
    plt.clf()

    group = df.groupby(['poi_id']).count()
    f,ax = plt.subplots()
    sns.distplot(group.hour,kde=False, hist_kws={'histtype':'stepfilled'}, ax=ax, bins=200)
    ax.set(xscale="log", yscale="log")
    ax.set_ylabel('# POI')
    ax.set_xlabel('# tweets per POI')
    plt.title('%s histogram' % place)
    plt.savefig(directory +'hist_tw_poi_%s.png' % place.replace(' ', '_'))
    plt.clf()


    group = df.groupby(pd.Grouper(freq='W'))['user'].nunique()
    f,ax = plt.subplots()
    group.plot()
    ax.set(yscale="log")
    ax.set_ylabel('# unique users')
    ax.set_xlabel('Weeks')
    plt.title('%s' % place)
    plt.savefig(directory +'dist_wk_user_unq_%s.png' % place.replace(' ', '_'))
    plt.clf()

    group = df.groupby(pd.Grouper(freq='W'))['poi_id'].unique()
    f,ax = plt.subplots()
    group.apply(lambda x: len(x)).plot()
    ax.set_ylabel('# unique POI')
    ax.set(yscale="log")
    ax.set_xlabel('Weeks')
    plt.title('%s' % place)
    plt.savefig(directory +'dist_wk_poi_unq_%s.png' % place.replace(' ', '_'))
    plt.clf()

    group = df.groupby(['poi_id']).agg({"user": lambda x: x.count()})
    f,ax = plt.subplots()
    sns.distplot(group,kde=False, hist_kws={'histtype':'stepfilled'}, ax=ax, bins=200)
    ax.set(xscale="log")
    ax.set(yscale="log")
    ax.set_xlabel('# visits per POI')
    ax.set_ylabel('# POI')
    plt.title('histogram %s' % place)
    plt.savefig(directory +'hist_visit_poi_%s.png' % place.replace(' ', '_'))
    plt.clf()

    group = df.groupby(['poi_id']).agg({"user": lambda x: x.nunique()})
    f,ax = plt.subplots()
    sns.distplot(group,kde=False, hist_kws={'histtype':'stepfilled'}, ax=ax, bins=200)
    ax.set(xscale="log")
    ax.set(yscale="log")
    ax.set_ylabel('# POI')
    ax.set_xlabel('# unique user per POI')
    plt.title('histogram %s' % place)
    plt.savefig(directory +'hist_user_unq_poi_%s.png' % place.replace(' ', '_'))
    plt.clf()

    group = df.groupby(['amenity']).agg({"poi_id": lambda x: x.nunique()})
    plt.figure(figsize=(12,8))
    group.poi_id.plot.bar(color='salmon')
    plt.xticks(np.arange(group.shape[0]),group.index,rotation='90')
    plt.yscale('log')
    plt.title('%s' % place)
    plt.savefig(directory +'dist_amenity_%s.png' % place.replace(' ', '_'))
    plt.clf()



