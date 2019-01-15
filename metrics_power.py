import argparse
import datetime
import logging
import multiprocessing as mp
import os

import networkx as nx
import numpy as np
import pandas as pd

from power_influence import power_attract_influence, power_support_influence


def create_df_sp(In_G, Out_G):
    columns = ['in', 'in_amenity', 'in_support', 'in_attract',
               'support', 'out', 'out_amenity', 'out_support', 'out_attract']
    list_of_lists = list()
    for edge in In_G.edges(data=True):
        tmp = list()
        tmp.append(edge[0])
        tmp.append(In_G.node[edge[0]]['amenity'])
        tmp.append(In_G.node[edge[0]]['support'])
        tmp.append(Out_G.node[edge[0]]['attract'])
        tmp.append(edge[2]['weight'])
        tmp.append(edge[1])
        tmp.append(In_G.node[edge[1]]['amenity'])
        tmp.append(In_G.node[edge[1]]['support'])
        tmp.append(Out_G.node[edge[1]]['attract'])
        list_of_lists.append(tmp)
    return pd.DataFrame(list_of_lists, columns=columns)


def create_df_ap(In_G, Out_G):
    columns = ['out', 'out_amenity', 'out_support', 'attract',
               'out_attract', 'in', 'in_amenity', 'in_support', 'in_attract']
    list_of_lists = list()
    for edge in In_G.edges(data=True):
        tmp = list()
        tmp.append(edge[0])
        tmp.append(In_G.node[edge[0]]['amenity'])
        tmp.append(In_G.node[edge[0]]['attract'])
        tmp.append(Out_G.node[edge[0]]['support'])
        tmp.append(edge[2]['weight'])
        tmp.append(edge[1])
        tmp.append(In_G.node[edge[1]]['amenity'])
        tmp.append(In_G.node[edge[1]]['attract'])
        tmp.append(Out_G.node[edge[1]]['support'])
        list_of_lists.append(tmp)
    return pd.DataFrame(list_of_lists, columns=columns)


def create_row(node_tuple, Graph, iteration):
    tmp = list()
    try:
        tmp.append(iteration)
        tmp.append(node_tuple[0])
        tmp.append(node_tuple[1])
        tmp.append(node_tuple[2])
        tmp.append(nx.density(Graph))
        tmp.append(nx.number_strongly_connected_components(Graph))
        if nx.is_weakly_connected(Graph):
            tmp.append(nx.number_weakly_connected_components(Graph))
        else:
            tmp.append(0)
        tmp.append(nx.number_of_nodes(Graph))
        tmp.append(nx.number_of_edges(Graph))
        tmp.append(np.mean(list(dict(Graph.out_degree()).values())))
        tmp.append(np.mean(list(dict(Graph.in_degree()).values())))
        if nx.is_weakly_connected(Graph):
            tmp.append(nx.average_shortest_path_length(Graph))
        else:
            tmp.append(0)
        tmp.append(nx.diameter(Graph.to_undirected()))
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)
    return tmp


def remove_edges(Graph, node):
    G = Graph.copy()
    try:
        for e_in, e_out, k in list(G.edges(keys=True)):
            if node == str(k):
                G.remove_edge(e_in, e_out, key=k)
            elif node == e_out:
                G.remove_edge(e_in, e_out)
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)
    return G


def support(sp_G, n, file_name):
    rows = list()
    for i in range(n):
        try:
            sp = power_support_influence(sp_G)
            ap = power_attract_influence(sp_G)
            df = create_df_sp(sp, ap)
            df['power'] = 'support'
            df.to_pickle('%s_sp_%i.pkl' % (file_name, (i + 1)))
            node = df.sort_values(['in_support'], ascending=False).iloc[0][[
                'in', 'in_amenity']]
            node_tuple = ('support', node['in'], node['in_amenity'])
            rows.append(create_row(node_tuple, sp_G, i))
            sp_G = remove_edges(sp_G, node['in'])
        except Exception as e:
            print("Unexpected error: {}".format(e))
            logger.exception(e)
    return rows


def attract(ap_G, n, file_name):
    rows = list()
    for i in range(n):
        try:
            sp = power_support_influence(ap_G)
            ap = power_attract_influence(ap_G)
            df = create_df_ap(ap, sp)
            df['power'] = 'attract'
            df.to_pickle('%s_ap_%i.pkl' % (file_name, (i + 1)))
            node = df.sort_values(['out_attract'], ascending=False).iloc[0][[
                'out', 'out_amenity']]
            node_tuple = ('attract', node['out'], node['out_amenity'])
            rows.append(create_row(df, ap_G, i))
            ap_G = remove_edges(ap_G, node['out'])
        except Exception as e:
            print("Unexpected error: {}".format(e))
            logger.exception(e)
    return rows


def eigenvector_centrality_in(Graph, n, file_name):
    rows = list()
    for i in range(n):
        try:
            if Graph.has_node('H'):
                Graph.remove_node('H')
            ec = nx.eigenvector_centrality_numpy(Graph)
            columns = ['poi_id', 'eigcen_in']
            df = pd.DataFrame(
                [list(ec.keys()), list(ec.values())], columns=columns)
            df.to_pickle('%s_eigcen_in_%i.pkl' % (file_name, (i + 1)))
            node = sorted(s.items(), key=lambda x: x[1], reverse=True)[0]
            amenity = nx.get_node_attributes(Graph, 'amenity')[node[0]]
            node_tuple = ('eigcen_in', node[0], amenity)
            rows.append(create_row(node_tuple, Graph, i))
            Graph = remove_edges(Graph, node[0])
        except Exception as e:
            print("Unexpected error: {}".format(e))
            logger.exception(e)
    return rows


def eigenvector_centrality_out(Graph, n, file_name):
    rows = list()
    for i in range(n):
        try:
            if Graph.has_node('H'):
                Graph.remove_node('H')
            ec = nx.eigenvector_centrality_numpy(Graph.reverse())
            columns = ['poi_id', 'eigcen_out']
            df = pd.DataFrame(
                [list(ec.keys()), list(ec.values())], columns=columns)
            df.to_pickle('%s_eigcen_out_%i.pkl' % (file_name, (i + 1)))
            node = sorted(s.items(), key=lambda x: x[1], reverse=True)[0]
            amenity = nx.get_node_attributes(Graph, 'amenity')[node[0]]
            node_tuple = ('eigcen_out', node[0], amenity)
            rows.append(create_row(node_tuple, Graph, i))
            Graph = remove_edges(Graph, node[0])
        except Exception as e:
            print("Unexpected error: {}".format(e))
            logger.exception(e)
    return rows


def in_degree_centrality(Graph, n, file_name):
    rows = list()
    for i in range(n):
        try:
            if Graph.has_node('H'):
                Graph.remove_node('H')
            dc = nx.in_degree_centrality(Graph)
            columns = ['poi_id', 'in_dg_cen']
            df = pd.DataFrame(
                [list(dc.keys()), list(dc.values())], columns=columns)
            df.to_pickle('%s_in_dg_cen_%i.pkl' % (file_name, (i + 1)))
            node = sorted(s.items(), key=lambda x: x[1], reverse=True)[0]
            amenity = nx.get_node_attributes(Graph, 'amenity')[node[0]]
            node_tuple = ('in_dg_cen', node[0], amenity)
            rows.append(create_row(node_tuple, Graph, i))
            Graph = remove_edges(Graph, node[0])
        except Exception as e:
            print("Unexpected error: {}".format(e))
            logger.exception(e)
    return rows


def out_degree_centrality(Graph, n, file_name):
    rows = list()
    for i in range(n):
        try:
            if Graph.has_node('H'):
                Graph.remove_node('H')
            dc = nx.out_degree_centrality(Graph)
            columns = ['poi_id', 'out_dg_cen']
            df = pd.DataFrame(
                [list(dc.keys()), list(dc.values())], columns=columns)
            df.to_pickle('%s_out_dg_cen_%i.pkl' % (file_name, (i + 1)))
            node = sorted(s.items(), key=lambda x: x[1], reverse=True)[0]
            amenity = nx.get_node_attributes(Graph, 'amenity')[node[0]]
            node_tuple = ('out_dg_cen', node[0], amenity)
            rows.append(create_row(node_tuple, Graph, i))
            Graph = remove_edges(Graph, node[0])
        except Exception as e:
            print("Unexpected error: {}".format(e))
            logger.exception(e)
    return rows


def create_graphs(graph):
    logger.info(">>>>>> Processing graph %s" % graph)
    H = nx.read_gml(directory + graph)
    file_name = directory + graph.split('.')[0].replace('inf_', '')
    row_lines = list()
    columns = ['iter', 'metric', 'poi_id', 'poi_amenity', 'density', 'strong_cc', 'weak_cc',
               'num_nodes', 'num_edges', 'avg_in_dg', 'avg_out_dg', 'avg_short_path', 'diamenter']
    logger.info(">>>>>> Processing Support for %s" % graph)
    row_lines += support(H.copy(), iter_param, file_name)
    logger.info(">>>>>> Processing Attract for %s" % graph)
    row_lines += attract(H.copy(), iter_param, file_name)
    logger.info(">>>>>> Processing Eig Cen In for %s" % graph)
    row_lines += eigenvector_centrality_in(H.copy(), iter_param, file_name)
    logger.info(">>>>>> Processing Eig Cen Out for %s" % graph)
    row_lines += eigenvector_centrality_out(H.copy(), iter_param, file_name)
    df = pd.DataFrame(row_lines, columns=columns)
    logger.info(">>>>>> Processing In Dgr Cen for %s" % graph)
    row_lines += in_degree_centrality(H.copy(), iter_param, file_name)
    logger.info(">>>>>> Processing Out Dgr Cen for %s" % graph)
    row_lines += out_degree_centrality(H.copy(), iter_param, file_name)
    logger.info(">>>>>> Saving dataFrame for %s" % file_name)
    df.to_pickle('%s_metrics.pkl' % (file_name))
    logger.info(">>>>>> Finished for %s" % graph)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('metrics_power_%s.log' % (
        datetime.datetime.now().strftime('%d_%m_%y')))
    handler.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    # create a logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(consoleHandler)

    parser = argparse.ArgumentParser(description='Metrics of Power')
    parser.add_argument('-p', '--place', required=True)
    parser.add_argument('-i', '--iterations', required=True)

    args = parser.parse_args()
    place = args.place
    iter_param = int(args.iterations)

    directory = 'graphs/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    files = ([file for file in os.listdir('graphs') if file.startswith(
        'inf_%s' % place) and file.endswith('.gml')])

    workers = (mp.cpu_count()-2)
    logger.info(">>>>>> number of workes: %i" % workers)
    pool = mp.Pool(processes=(workers))
    logger.info(">>>>>> Call functions with multiprocessing")
    _ = pool.map(create_graphs, files)
