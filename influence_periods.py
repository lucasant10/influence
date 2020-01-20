import matplotlib 
matplotlib.use('agg')
import networkx as nx
import pandas as pd
import argparse
import os
import influence

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Creating Influence Network by Periods')
    parser.add_argument('-p', '--place', required=True)
    parser.add_argument('-f', '--file', required=True)
    args = parser.parse_args()

    file = args.file 
    place = args.place

    delta_t = 6
    df = pd.read_pickle(file)
    intervals = [('22:00','6:00'),('6:00','14:00'),('14:00','22:00')]

    for start, end in intervals:
        print("processing: %s - %s" % (place, start))
        df_period = df.between_time(start,end)
        M, time = influence.generate_graphs_from_group(df_period,delta_t)
        nx.write_gml(M, "graphs/inf_%s_%sh.gml" % (place, start.split(':')[0]))