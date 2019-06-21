import configparser
import multiprocessing as mp
import os
import sys
from functools import partial
from itertools import repeat

import networkx as nx
import pandas as pd

sys.path.append('../')

def remove_impact(df_m, poi_list):
    try:
        workers = (mp.cpu_count()-1)
        pool = mp.Pool(processes=(workers))
        part_func = partial(remove_parallel, df_m=df_m) 
        df_list = pool.map(part_func, poi_list)           
        return pd.concat(df_list)
    except Exception as e:
        print("Unexpected error: {}".format(e))

def remove_parallel(node, df_m):
    try:
        print('\tprocessing node: %s' % node)
        neighbors = list(Graph.neighbors(node))
        df_before = df_m[df_m.poi_id.isin(neighbors)]
        tmp_b = df_before.groupby('poi_id').size().reset_index(name='mean_users_before')
        print('\tremoving trajectories for node: %s' % node)
        df_rem = remove_trajactories(node)
        df_after = df_rem[df_rem.poi_id.isin(neighbors)]
        tmp_a = df_after.groupby('poi_id').size().reset_index(name='mean_users_after')
        df_tmp = pd.merge(tmp_b, tmp_a, how='outer', on="poi_id")
        df_tmp.fillna(0, inplace=True)
        df_tmp['main_poi'] = node
        return df_tmp
    except Exception as e:
        print("Unexpected error: {}".format(e))

def remove_trajactories(node):
    try:
        df_list = list()
        for path_df in trajectories:
            if node not in path_df.poi_id.values:
                df_list.append(path_df)
        return pd.concat(df_list)
    except Exception as e:
        print("Unexpected error: {}".format(e))

def get_trajectories(delta_t, day_group):
    try:
        df_list = list()
        day_group.index = day_group.index-pd.Timedelta(6, unit='h')
        for _, time_df in day_group.groupby(pd.Grouper(freq='D')):
            for name in time_df.user.unique():
                t_user = time_df[time_df.user == name]
                t_user = t_user.loc[t_user.poi_id.shift() != t_user.poi_id]
                # Test if the nodes i and j have a time gap less then delta_t
                diff_t = [True] + list((t_user.iloc[1:, ].index -
                                        t_user.iloc[:-1, ].index).seconds / 3600 <= delta_t)
                # get index for split dataframe in paths
                split_index = [i for i, x in enumerate(diff_t) if not x]
                for path_df in split(t_user, split_index):
                    df_list.append(path_df)
        return df_list    
    except Exception as e:
        print("Unexpected error: {}".format(e))

def split(df, splitters):
    start = 0
    for index in splitters:
        yield df[start:index]
        start = index
    yield df[start:]

if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['dartmouth']
    
    files = ([directory+"graphs/"+file for file in os.listdir(directory+"graphs/") if file.endswith('.pkl')])
    files.sort()
    dic = dict()
    for file in files:
        df =  pd.read_pickle(file)
        dic[df.iloc[1].values[2]] = df.sort_values([df.columns[1]], ascending=False)['poi_id'][:20].values

    dic['random'] = df.poi_id.sample(n=20, random_state=1)
    df_rnk = pd.DataFrame.from_dict(dic, orient = 'index').reset_index()

    Graph = nx.read_gml(directory+"graphs/inf_dartmouth_2004-02-01_test.gml")
    Graph.remove_node('H')
    df_dm = pd.read_pickle(directory+"dartmouth_test.pkl")
    print('Get trajectories')
    trajectories = get_trajectories(6, df_dm)    
    df_list = []
    for i in range(df_rnk.shape[0]):
        metric = df_rnk.iloc[i]['index']
        print('processing metric: %s' % metric)
        df_tmp = remove_impact(df_dm, df_rnk.iloc[i].values[1:])
        df_tmp['metric'] = metric
        df_list.append(df_tmp)
    result = pd.concat(df_list)
    
    result.to_pickle(directory + 'poi_remove_impact.pkl')
