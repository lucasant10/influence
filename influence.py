import networkx as nx
import pandas as pd
import math
from collections import defaultdict

def combined_graphs_edges(G, H):
    for u,v,hdata in H.edges(data=True):
        attr = dict( (key, value) for key,value in hdata.items())
        # get data from G or use empty dict if no edge in G
        if G.has_edge(u,v):
            gdata = G[u].get(v,{})
        else:
            gdata = []
        # add data from g
        # sum shared items
        shared = set(gdata) & set(hdata)
        attr.update(dict((key, attr[key] + gdata[key]) for key in shared))
        # non shared items
        non_shared = set(gdata) - set(hdata)
        attr.update(dict((key, gdata[key]) for key in non_shared))
        yield u,v,attr
    return

def harmonic(value1, value2):
    return (2 * value1 * value2 / (value1 + value2))

def fv_func(Wij,j, G):
    Nik = 0
    for _, _, edata in G.in_edges(j, data=True):
        Nik += edata['weight']
    return (Wij / Nik)

def inflences(G):
    out_degree = G.out_degree()
    dic_inf = defaultdict(list)
    for node in G.nodes():
        if(out_degree[node]>0):
            Nit = G.out_degree(node)
            inf_f =  (math.log2(Nit) if Nit >= 1 else 0)
            inf_w = 0
            inf_nb = 0
            Wik = G.out_degree(node, weight='weight')
            for j in G.neighbors(node):    
                Wij = G[node][j]['weight']
                inf_w += (-1 * ((Wij / Wik) * math.log2(Wij / Wik)))
                inf_nb += Wij * fv_func(Wij,j,M)
            dic_inf[node] = [inf_f, inf_w, inf_nb]
    return dic_inf

if __name__ == "__main__":
    
    df = pd.read_pickle('poi_tw.pkl')
    inf_list = list()
    for h in range(1, 24, 2):
        M = nx.DiGraph()
        #for each slice hour
        sliced = df[(df['hour'] >= h) & (df['hour'] < h + 1)]
        print('generating graph for %iH' % h)
        for name in sliced.user.unique():
            #If user have at least 1 trajectory from i to j
            if len(sliced.user == name) > 1:
                U = nx.DiGraph()
                t_user = sliced[sliced.user == name]
                #add transitions in same day by user 
                for t in sliced.index.strftime('%D').unique():
                    path = list(t_user[t].poi_id)
                    U.add_path(path, weight=0)
                #remove self loops
                U.remove_edges_from(U.selfloop_edges())
                #sum egde weight
                for i, j in U.edges():
                    #get impact
                    imp_f = t_user[t_user.poi_id == i].iloc[0].impact
                    imp_t = t_user[t_user.poi_id == j].iloc[0].impact
                    U[i][j]['weight'] += harmonic(imp_f, imp_t)
            M.add_edges_from(combined_graphs_edges(M,U))
        print('saving graph %iH' % h)
        nx.write_gml(M, "inf_from_%i_to_%iH.gml" % (h,(h+1)))
        print('calculating influences')
        dic_inf = inflences(M)
        tmp_inf = pd.DataFrame.from_dict(dic_inf, orient='index')
        tmp_inf['hour'] = h
        inf_list.append(tmp_inf)
    print('concatenating dataframes')
    df_inf = pd.concat(inf_list)
    print('saving dataframe influence')
    df.to_pickle('poi_influnces.pkl')

