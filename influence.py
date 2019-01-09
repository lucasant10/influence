import matplotlib 
matplotlib.use('agg')
import networkx as nx
import pandas as pd
import math
from collections import defaultdict
import itertools
import matplotlib.pyplot as plt
import argparse
import os


def combined_multi_digraphs_edges(G, H):
    for u, v, key, hdata in H.edges(data=True, keys=True):
        attr = dict((key, value) for key, value in hdata.items())
        # get data from G or use empty dict if no edge in G
        if G.has_edge(u, v, key):
            gdata = G[u].get(v)[key]
        else:
            gdata = []
        # add data from g
        # sum shared items
        shared = set(gdata) & set(hdata)
        attr.update(dict((key, attr[key] + gdata[key]) for key in shared))
        # non shared items
        non_shared = set(gdata) - set(hdata)
        attr.update(dict((key, gdata[key]) for key in non_shared))
        yield u, v, key, attr
    return


def harmonic(value1, value2):
    return (2 * value1 * value2 / (value1 + value2))

def set_amenities(G, df):
    attr = dict()
    for node in G.nodes():
        if node != 'H':
            attr[node] = df[df['poi_id'] == node].iloc[0].amenity
    nx.set_node_attributes(G, attr, 'amenity')
    return G

def split(df, splitters):
    start = 0
    for index in splitters:
        yield df[start:index]
        start = index
    yield df[start:]

def generate_graphs(delta_t, df, t_frame, place):
    path_distribution = list()
    for group in df.groupby(pd.Grouper(freq=t_frame)):
        # for each time frame
        time_df = group[1]
        time = group[0].strftime("%d-%m-%y")
        M = nx.MultiDiGraph()
        print('generating graph for %s' % time)
        for name in time_df.user.unique():
            t_user = time_df[time_df.user == name]
            # Test if the nodes i and j have a time gap less then delta_t
            diff_t = [True] + list((t_user.iloc[1:,].index - t_user.iloc[:-1,].index).seconds / 3600 <= delta_t )
            #get index for split dataframe in paths
            split_index = [i for i, x in enumerate(diff_t) if not x]
            for path_df in split(t_user, split_index):
                U = nx.MultiDiGraph()
                edges = create_edges(path_df)
                path_distribution.append(len(edges))
                U.add_edges_from(edges, weight=0)
                # sum egde weight
                for i, j, key in U.edges(keys=True):
                    #if node i is the 'Home' POI 
                    if (i == 'H'):
                    # get impact
                        imp_f = path_df[path_df.poi_id == j].impact.max()
                        imp_t = path_df[path_df.poi_id == j].impact.max()
                    #if node i is the 'Home' POI 
                    elif (j == 'H'):
                        imp_f = path_df[path_df.poi_id == i].impact.max()
                        imp_t = path_df[path_df.poi_id == i].impact.max()
                    #otherwise is a edge between POI
                    else:
                        imp_f = path_df[path_df.poi_id == i].impact.max()
                        imp_t = path_df[path_df.poi_id == j].impact.max()
                    # Calculate the uncertainty mean for edge
                    U[i][j][key]['weight'] += harmonic(imp_f, imp_t)
                M.add_edges_from(combined_multi_digraphs_edges(M, U))
        print('saving graph %s' % time)
        M = set_amenities(M,df)
        yield (M, time)
    plt.hist(path_distribution, bins=100, log=True)
    plt.savefig('dist_path.png')

def create_edges(df):
    path = list(df.poi_id)
    #generate edges from path
    edges = list(zip(path[0::1], path[1::1], itertools.repeat(path[0])))
    #remove cycle in graph and self_loop
    edges = [x for x in list(edges) if (x[0] != x[1]) and (x[1] != path[0])]
    # add 'Home' POI to mean that this person arrives or departs from it.
    edges.append(('H',path[0],path[0]))
    edges.append((path[-1],'H',path[0]))
    return edges


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Creating Influence Network')
    parser.add_argument('-p', '--place', required=True)
    parser.add_argument('-f', '--file', required=True)
    args = parser.parse_args()

    file = args.file 
    place = args.place

    df = pd.read_pickle(file)
    df['amenity'] = df.amenity.fillna("")
    group = df.groupby(['user']).count()
    #df = df[df.user.isin(group[(group.poi_id>6)][3:].index)]
    inf_list = list()
    delta_t = 4
    #t_frame = 'W-MON'
    t_frame = '2QS'
    directory = 'graphs'
    if not os.path.exists(directory):
        os.makedirs(directory)
    has_files = ([file for file in os.listdir(directory) if file.startswith('inf_%s' % place) and file.endswith('.gml')])
    if not has_files:
        for M, time in generate_graphs(delta_t, df, t_frame, place): 
            nx.write_gml(M, "graphs/inf_%s_%s.gml" % (place, time))

    # print('concatenating dataframes')
    # df_inf = pd.concat(inf_list)
    # df_inf = df_inf.rename(columns={0:'imp_f', 1:'imp_t',2:'imp_nb',3:'amenity'})
    # print('saving dataframe influence')
    # df_inf.to_pickle('poi_influnces.pkl')
    # #df_inf = pd.read_pickle('poi_influnces.pkl')

    # df_inf['d_inf'] = df_inf.apply(lambda row: (0.4 * row['imp_f'] + 0.6 * row['imp_t']), axis=1)
    # df_inf.apply(lambda row: (0.4 * row['imp_f'] + 0.6 * row['imp_t']), axis=1)