import matplotlib 
matplotlib.use('agg')
import networkx as nx
import pandas as pd
import math
from collections import defaultdict, OrderedDict
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

def all_same( items ):
    return len( set( items ) ) == 1

def generate_graphs(delta_t, df, t_frame):
    for group in df.groupby(pd.Grouper(freq=t_frame)):
        # for each time frame
        day_group = group[1]
        time = group[0].strftime("%d-%m-%y")
        M = nx.MultiDiGraph()
        print('generating graph for %s' % time)
        #shift day in -5 hours for day start at 5am
        day_group.index = day_group.index-pd.Timedelta(5, unit='h')
        for _, time_df in day_group.groupby(pd.Grouper(freq='D')):
            for name in time_df.user.unique():
                t_user = time_df[time_df.user == name]
                # Test if the nodes i and j have a time gap less then delta_t
                diff_t = [True] + list((t_user.iloc[1:,].index - t_user.iloc[:-1,].index).seconds / 3600 <= delta_t )
                #get index for split dataframe in paths
                split_index = [i for i, x in enumerate(diff_t) if not x]
                for path_df in split(t_user, split_index):
                    U = nx.MultiDiGraph()
                    edges = create_edges(path_df)
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
        yield (M, time)

def generate_graphs_from_group(group, delta_t):
    # for each time frame
    day_group = group
    #time = "2004-02-01"
    time = "02-11-03"
    M = nx.MultiDiGraph()
    print('generating graph for %s' % time)
    #shift day in -6 hours for day start at 6am
    day_group.index = day_group.index-pd.Timedelta(6, unit='h')
    for _, time_df in day_group.groupby(pd.Grouper(freq='D')):
        for name in time_df.user.unique():
            t_user = time_df[time_df.user == name]
            #remove consecutive duplicated POIs
            t_user = t_user.loc[t_user.poi_id.shift() != t_user.poi_id]
            # Test if the nodes i and j have a time gap less then delta_t
            diff_t = [True] + list((t_user.iloc[1:,].index - t_user.iloc[:-1,].index).seconds / 3600 <= delta_t )
            #get index for split dataframe in paths
            split_index = [i for i, x in enumerate(diff_t) if not x]
            for path_df in split(t_user, split_index):
                U = nx.MultiDiGraph()
                edges = create_edges_path(path_df)
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
    return (M, time)
    
def create_edges_path(df):
    poi_list = list(df.poi_id)
    edge_list = list()
    #checkin in one POI only
    if all_same(poi_list):
        key = '%s_%s'%(poi_list[0],poi_list[0])
        edge_list.append(('H',poi_list[0], key))
        edge_list.append((poi_list[0],'H', key))
    else:
        for path in path_list(poi_list):
            #generate edges from path
            edges = list(zip(path[0::1], path[1::1]))
            #remove cycle in graph and self_loop
            edges = [x for x in list(edges) if (x[0] != x[1])]
            #for split_path in split_list(edges, path[0]):
            key = "_".join(path)
            for edge in edges:
                first = path[0]
                last = path[-1]
                edge_list.append((edge[0],edge[1],key))
                # add 'Home' POI to mean that this person arrives or departs from it.
                edge_list.append(('H',first, key))
                edge_list.append((last,'H', key))
    return edge_list

def create_edges(df):
    path = list(df.poi_id)
    edge_list = list()
    #checkin in one POI only
    if all_same(path):
        key = '%s_%s'%(path[0],path[0])
        edge_list.append(('H',path[0], key))
        edge_list.append((path[0],'H', key))
    else:
        #generate edges from path
        edges = list(zip(path[0::1], path[1::1]))
        #remove cycle in graph and self_loop
        edges = [x for x in list(edges) if (x[0] != x[1])]
        for split_path in split_list(edges, path[0]):
            if split_path:
                first = split_path[0][0]
                last = split_path[-1][1]
                key = '%s_%s'%(first,last)
                for edge in split_path:
                    edge_list.append((edge[0],edge[1],key))
                # add 'Home' POI to mean that this person arrives or departs from it.
                edge_list.append(('H',first, key))
                edge_list.append((last,'H', key))
    return edge_list


def path_list(path):
    try:
        visited = list()
        paths = list()
        for i in path:
            if i not in visited:
                visited.append(i)
            else:
                paths.append(visited)
                visited = list()
                visited.append(i)
        paths.append(visited)
        return paths
    except Exception as e:
        print("Unexpected error: {}".format(e))

def split_list(edges, node):
    try:
        start = 0
        for i, edge in enumerate(edges):
            if (edge[1] == node):
                yield [x for x in edges[start:i] if (x[1] != node)]
                start = i
        yield [x for x in edges[start:] if (x[1] != node)]
    except Exception as e:
        print("Unexpected error: {}".format(e))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Creating Influence Network')
    parser.add_argument('-p', '--place', required=True)
    parser.add_argument('-f', '--file', required=True)
    args = parser.parse_args()

    file = args.file 
    place = args.place

    df = pd.read_pickle(file)
    df['amenity'] = df.amenity.fillna("")
    inf_list = list()
    delta_t = 6
    #t_frame = 'W-MON'
    t_frame = '2QS'
    directory = 'graphs'
    if not os.path.exists(directory):
        os.makedirs(directory)
    has_files = ([file for file in os.listdir(directory) if file.startswith('inf_%s' % place) and file.endswith('.gml')])
    if not has_files:
        for M, time in generate_graphs(delta_t, df, t_frame): 
            M = set_amenities(M,df)
            nx.write_gml(M, "graphs/inf_%s_%s.gml" % (place, time))