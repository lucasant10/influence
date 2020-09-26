import sys
sys.path.append('../')
import networkx as nx
import influence
import pandas as pd
import multiprocessing as mp
import logging
import os
import configparser
from datetime import timedelta, date, datetime
import random
from haversine import haversine
import math
import metrics_power
from collections import Counter


def m_haversine(point1, point2):
    return (haversine(point1, point2) * 1000)

def sqrt_diff(row, centroid):
    try:
        if 'lon' in row:
            return m_haversine((row['lat'],row['lon']), (centroid.lat, centroid.lon)) ** 2
        return m_haversine((row['lat'],row['long']), (centroid.lat, centroid.long)) ** 2
    except Exception as e:
        print("sqrt_diff: Unexpected error: {}".format(e))

def radius_of_gyration(df_rg):
    return 0
    df_poi_unique = df_rg.groupby('poi_id', group_keys=False).apply(lambda d: d.sample(1))
    if 'lon' in df_rg.columns:
        centroid = df_poi_unique[['lat','lon']].mean()
    else:
        centroid = df_poi_unique[['lat','long']].mean()
    rg = df_poi_unique.apply(lambda  row: sqrt_diff(row, centroid), axis=1).mean()
    rg = math.sqrt(rg)
    return rg


def join_power(df_p):
    p_dict = dict()
    for i, m  in df_p.query('metric in ["support","attract"]').groupby("poi_id"):
        att= m.iloc[0]['power']
        supp = m.iloc[1]['power']
        mean = 2*(att*supp)/(att + supp)
        p_dict[i] = mean
    df_tmp = pd.DataFrame(p_dict.items(), columns=['poi_id', 'power'])
    df_tmp["metric"] = "joint_f1"
    return df_tmp

def parallel(G):
    try:
        metrics_list = list()
        
        metrics_list.append(metrics_power.df_support(G))
        metrics_list.append(metrics_power.df_attract(G))
        metrics_list.append(metrics_power.df_bozzo_franceschet_power(G))
        metrics_list.append(metrics_power.df_eigenvector_centrality_in(G))
        metrics_list.append(metrics_power.df_eigenvector_centrality_out(G))
        metrics_list.append(metrics_power.df_in_degree_centrality(G))
        metrics_list.append(metrics_power.df_out_degree_centrality(G))        
        metrics_list.append(metrics_power.df_pagerank(G))        
        metrics_list.append(metrics_power.df_betweenness(G))
        df = pd.concat(metrics_list)
        
        df = df.append(join_power(df))
        
        tmp = df.query('metric in ["support","attract"]').groupby("poi_id").sum().reset_index()
        tmp['metric'] = 'joint'
        df = df.append(tmp)
        return df
    except Exception as e:
        print("paralel: Unexpected error: {}".format(e))


def create_graphs(samples, dir_name):
    list_df = list()
    delta_t = 6
    last_date = samples[0]
    df = samples[1]
    M, time = influence.generate_graphs_from_group(
        df, delta_t, last_date.strftime("%d-%m-%y"))
    return M

def metrics(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    try:
        jaccard = float(intersection / union)
    except Exception as e:
        print("metrics: Unexpected error: {}".format(e))
        jaccard = 0
    diff1 = set(list1).difference(set(list2)) 
    diff2 = set(list2).difference(set(list1)) 
    return (jaccard, intersection, len(diff1), len(diff2), len(list1), len(list2))

def infection(top_pois, df_ep):
    df_ep.sort_index(inplace=True)
    list_df = list()
    infected_pois = set()
    infected_users = {str(x):None for x in df_ep.user.unique()}
    for x in top_pois:
        infected_pois.add(str(x))
    for row in df_ep.iterrows():
        poi = str(row[1]['poi_id'])
        user = str(row[1]['user'])
        if (infected_users[user] is not None):
            infected_pois.add(poi)
        elif (poi in infected_pois):
            infected_users[user] = row[0]
    return infected_pois

def epidemic_ng(top_pois, df_ep, G):
    try:
        if 'H' in G.nodes:
            G.remove_node('H')
        #G.remove_nodes_from([n for n, d in G.degree if d<2])
        ng_list = list()
        for node in top_pois:
            ng_list += list(G.neighbors(node))
        return infection2(top_pois, df_ep, ng_list)
    except Exception as e:
            print("Unexpected error: {}".format(e))
            logger.exception(e)

def infection2(top_pois, df_ep, ng_list):
    def infection_test(row):
        poi = str(row['poi_id'])
        user = str(row['user'])
        if (poi in infected_pois):
            infected_users[user] = row.name

    df_ep.sort_index(inplace=True)
    infected_pois = set()
    infected_users = {str(x):None for x in df_ep.user.unique()}
    for x in top_pois:
        infected_pois.add(str(x))
    df_ep.apply(lambda row: infection_test(row), axis=1)
    df_ng = df_ep[df_ep.poi_id.isin(ng_list)]
    df_tmp = pd.DataFrame(infected_users.items(), columns=['user', 'infection_time'])
    users = df_tmp[df_tmp.infection_time.notna()].user.values
    df_inf_users = df_ng[df_ng.user.isin(users)]
    df_inf_pois = df_ng[df_ng.poi_id.isin(df_inf_users.poi_id.unique())]
    rate = df_inf_users.groupby('poi_id').user.nunique() / df_inf_pois.groupby('poi_id').user.nunique()
    return (infected_pois, rate.mean())
    # try:
    #     rate = df_inf_users.user.nunique() / df_inf_pois.user.nunique()
    # except Exception as e:
    #     print("Unexpected error: {}".format(e))
    #     rate = 0
    # return (infected_pois, rate)

def get_pois_from_radius(df, row, radius):
    isin_radius = df.apply(lambda d_row: (m_haversine(d_row, row)<=radius), axis=1)
    return df[isin_radius].poi_id.unique()

# def top_pois(metrics_list, df):
#     poi_dict = dict()
#     cnt = Counter()
#     for m in metric_list:
#         pois = df.query('metric=="%s"' % m).sort_values('power', ascending=False)[:10].poi_id.values
#         poi_dict[m] = pois
#         cnt.update(pois)        
#     duplicates = [el[0] for el in cnt.items() if el[1] > 1]
#     for k, v in poi_dict.items():
#         poi_dict[k] = list(set(v).difference(set(duplicates)))
#     min_val = min([len(v) for k, v in poi_dict.items()])
#     for k, v in poi_dict.items():
#         poi_dict[k] = v[:min_val]

#     return (poi_dict, min_val)

def top_pois(metrics_list, df):
    poi_dict = dict()
    for m in metric_list:
        pois = df.query('metric=="%s"' % m).sort_values('power', ascending=False)[:10].poi_id.values
        poi_dict[m] = pois
    return poi_dict

if __name__ == "__main__":

    logger=logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler=logging.FileHandler('random_flow%s.log' % (
        datetime.now().strftime('%d_%m_%y')))
    handler.setLevel(logging.INFO)
    consoleHandler=logging.StreamHandler()
    # create a logging format
    formatter=logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(consoleHandler)

    cf=configparser.ConfigParser()
    cf.read("../file_path.properties")
    path=dict(cf.items("file_path"))
    directory=path['dartmouth']
    window='M'

    try:
        dir_path=os.path.join(directory, 'case_study')
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)

    # files=([file for file in os.listdir(directory) if file.endswith('.pkl')])
    # files = ['Austin.pkl','Seattle.pkl','Dallas.pkl']
    files = ['dartmouth.pkl']
    for filename in files:
        print('processing: %s' % filename.replace('.pkl', ''))
         # load df
        df=pd.read_pickle(os.path.join(directory, filename))
        # remove pois less than 10 visits
        df_tmp=df.groupby('poi_id').count()
        df=df[df.poi_id.isin(df_tmp[df_tmp.impact > 10].index.unique())]
        df.poi_id = df.poi_id.astype(str)
        df.sort_index(inplace=True)
        # resample by time window
        sampled_list=list(df.resample(window))
        # create location Dir  in case_study folder
        dir_name=os.path.join(dir_path, filename.replace('.pkl', ''))
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        tuple_list = list()
        first_loop = True
        for w1 in sampled_list:
            try:    
                g1 = create_graphs(w1, dir_name)
                df1 = parallel(g1)
                    
                # create the influence graphs
                
                df_w1 = w1[1].copy()
                metric_list = ['support','attract','joint','pagerank','eigcen_in','eigcen_out','betweenness', 'in_dg_cen','out_dg_cen', 'bf_power']
                poi_dict_w1 = top_pois(metric_list, df1)

                for i, m1 in enumerate(metric_list[:-1]):
                    for m2 in metric_list[(i+1):]:
                        if m1==m2:
                            continue                        
                        m1w1 = set(poi_dict_w1[m1]).difference(set(poi_dict_w1[m2]))
                        m2w1 = set(poi_dict_w1[m2]).difference(set(poi_dict_w1[m1]))
                        
                        # list1 = infection(m1w1, df_w1, g1)
                        # list2 = infection(m1w2, df_w2, g2)
                        # list3 = infection(m2w1, df_w1, g1)
                        # list4 = infection(m2w2, df_w2, g2)
                        list1, r1 = epidemic_ng(m1w1, df_w1, g1)
                        list2, r2 = epidemic_ng(m2w1, df_w1, g1)
                        tuple_list.append(('%s'% m1, len(list1), r1, radius_of_gyration(df_w1[df_w1.poi_id.isin(m1w1)])))
                        tuple_list.append(('%s'% m2, len(list2), r2, radius_of_gyration(df_w1[df_w1.poi_id.isin(m2w1)])))

                        # tuple_list.append(metrics(list1,list2) + ('%s_%s'%(m1,m1),))
                        # tuple_list.append(metrics(list1,list3) + ('%s_%s'%(m1,m2),))
                        # tuple_list.append(metrics(list2,list4) + ('%s_%s'%(m1,m2),))
                        # tuple_list.append(metrics(list3,list4) + ('%s_%s'%(m2,m2),))
            except Exception as e:
                print("main: Unexpected error: {}".format(e))
        #df = pd.DataFrame(tuple_list, columns=['jaccard','intersection', 'diff1', 'diff2', 'size1','size2', 'metrics'])
        df = pd.DataFrame(tuple_list, columns=['metrics', 'num-pois', 'rate', 'r_gyration'])
        df.to_pickle(os.path.join(dir_name,'jaccard_%s' % filename))
