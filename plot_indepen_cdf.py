import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import configparser
import matplotlib.cm as cm
import os

def plot_cdf(data, ax, i ):
    num_bins = 300
    counts, bin_edges = np.histogram(data, bins=num_bins)
    cdf = np.cumsum(counts)
    ax.plot(bin_edges[1:], cdf/cdf[-1], linewidth=4, color=colors[i], label=cities[i].replace("poi_tw_",''))

if __name__ == "__main__":
    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['twitter']   
    dir_out =  path['dir_out']  
    
    cities = ([file.replace('.pkl', '') for file in os.listdir(directory) if file.endswith('.pkl')])

    figure = plt.figure(figsize=(13, 10))
    ax = figure.add_subplot(111)
    legend=[]
    colors = plt.cm.get_cmap('tab20').colors
    for i, city in enumerate(cities):
        df = pd.read_pickle(directory + "{0}/independence_{0}.pkl".format(city))
        plot_cdf(df.power, ax, i)

    plt.legend(fontsize=12, frameon=False)
    plt.xlabel('Independence percentage',fontsize=25)
    plt.ylabel('F(x)',fontsize=25)
    plt.xticks(np.arange(0, 1.1, step=0.1),fontsize=25, rotation=30)
    plt.yticks(np.arange(0, 1.1, step=0.1),fontsize=25)
    plt.savefig(dir_out + 'cdf_cities.png')

    plt.clf()


