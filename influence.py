import networkx as nx
import pandas as pd
import math
from collections import defaultdict
from scipy.stats import beta


def combined_graphs_edges(G, H):
    for u, v, hdata in H.edges(data=True):
        attr = dict((key, value) for key, value in hdata.items())
        # get data from G or use empty dict if no edge in G
        if G.has_edge(u, v):
            gdata = G[u].get(v, {})
        else:
            gdata = []
        # add data from g
        # sum shared items
        shared = set(gdata) & set(hdata)
        attr.update(dict((key, attr[key] + gdata[key]) for key in shared))
        # non shared items
        non_shared = set(gdata) - set(hdata)
        attr.update(dict((key, gdata[key]) for key in non_shared))
        yield u, v, attr
    return


def harmonic(value1, value2):
    return (2 * value1 * value2 / (value1 + value2))


def fv_func(Wij, j, G):
    Nik = 0
    for _, _, edata in G.in_edges(j, data=True):
        Nik += edata['weight']
    return (Wij / Nik)


def inflences(G):
    out_degree = G.out_degree()
    dic_inf = defaultdict(list)
    for node in G.nodes():
        if(out_degree[node] > 0):
            Nit = G.out_degree(node)
            inf_f = (math.log2(Nit) if Nit >= 1 else 0)
            inf_w = 0
            inf_nb = 0
            Wik = G.out_degree(node, weight='weight')
            for j in G.neighbors(node):
                Wij = G[node][j]['weight']
                inf_w += (-1 * ((Wij / Wik) * math.log2(Wij / Wik)))
                inf_nb += Wij * fv_func(Wij, j, G)
            dic_inf[node] = [inf_f, inf_w, inf_nb, G.node[node]['amenity']]
    return dic_inf


def set_amenities(G):
    attr = dict()
    for node in G.nodes():
        attr[node] = df[df['poi_id'] == node].iloc[0].amenity
    nx.set_node_attributes(G, attr, 'amenity')
    return G


def generate_graphs_hours(t_slice):
    for h in range(0, 24, t_slice):
        M = nx.DiGraph()
        # for each slice hour
        sliced = df[(df['hour'] >= h) & (df['hour'] < h + t_slice)]
        print('generating graph for %iH' % h)
        for name in sliced.user.unique():
            # If user have at least 1 trajectory from i to j
            if len(sliced.user == name) > 1:
                U = nx.DiGraph()
                t_user = sliced[sliced.user == name]
                # add transitions in same day by user
                for t in t_user.index.strftime('%D').unique():
                    path = list(t_user[t].poi_id)
                    U.add_path(path, weight=0)
                # remove self loops
                U.remove_edges_from(U.selfloop_edges())
                # sum egde weight
                for i, j in U.edges():
                    # get impact
                    imp_f = t_user[t_user.poi_id == i].iloc[0].impact
                    imp_t = t_user[t_user.poi_id == j].iloc[0].impact
                    U[i][j]['weight'] += harmonic(imp_f, imp_t)
                M.add_edges_from(combined_graphs_edges(M, U))
        print('saving graph %iH' % h)
        M = set_amenities(M)
        nx.write_gml(M, "graphs/inf_from_%i_to_%iH.gml" % (h, (h + t_slice)))
        print('calculating influences')
        dic_inf = inflences(M)
        tmp_inf = pd.DataFrame.from_dict(dic_inf, orient='index')
        tmp_inf['hour'] = h
        inf_list.append(tmp_inf)


def generate_graphs(t_slice, df, t_frame):
    for group in df.groupby(pd.Grouper(freq=t_frame)):
        # for each time frame
        time_df = group[1]
        time = group[0].strftime("%d-%m-%y")
        for h in range(0, 24, t_slice):
            # for each slice hour
            sliced = time_df[(time_df['hour'] >= h) & (
                time_df['hour'] < h + t_slice)]
            M = nx.DiGraph()
            print('generating graph for %s at %iH' % (time, h))
            for name in sliced.user.unique():
                U = nx.DiGraph()
                # If user have more than 1 place in its trajectory
                if len(sliced[sliced.user == name].poi_id.unique()) > 1:
                    t_user = sliced[sliced.user == name]
                    # add transitions by user
                    path = list(t_user.poi_id)
                    U.add_path(path, weight=0)
                    # remove self loops
                    U.remove_edges_from(U.selfloop_edges())
                    # sum egde weight
                    for i, j in U.edges():
                        # get impact
                        imp_f = t_user[t_user.poi_id == i].iloc[0].impact
                        imp_t = t_user[t_user.poi_id == j].iloc[0].impact
                        U[i][j]['weight'] += harmonic(imp_f, imp_t)
                else:
                    #self loop
                    user = sliced[sliced.user == name].iloc[0]
                    U.add_edge(user.poi_id, user.poi_id, weight=user.impact)
                M.add_edges_from(combined_graphs_edges(M, U))
            print('saving graph %iH' % h)
            M = set_amenities(M)
            nx.write_gml(M, "graphs/inf_for_%s_%iH.gml" % (time, h))


if __name__ == "__main__":

    df = pd.read_pickle('poi_tw.pkl')
    df['amenity'] = df.amenity.fillna("")
    inf_list = list()
    t_slice = 6
    t_frame = 'W'
    generate_graphs(t_slice, df, t_frame)

    # print('concatenating dataframes')
    # df_inf = pd.concat(inf_list)
    # df_inf = df_inf.rename(columns={0:'imp_f', 1:'imp_t',2:'imp_nb',3:'amenity'})
    # print('saving dataframe influence')
    # df_inf.to_pickle('poi_influnces.pkl')
    # #df_inf = pd.read_pickle('poi_influnces.pkl')

    # df_inf['d_inf'] = df_inf.apply(lambda row: (0.4 * row['imp_f'] + 0.6 * row['imp_t']), axis=1)
    # df_inf.apply(lambda row: (0.4 * row['imp_f'] + 0.6 * row['imp_t']), axis=1)

# nx.bfs_tree(G, 1).edges()
# list(nx.bfs_tree(G, 1).edges())
