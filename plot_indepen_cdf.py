import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import configparser
import matplotlib.cm as cm
import os

def plot_cdf(data, ax):
    num_bins = 300
    counts, bin_edges = np.histogram(data, bins=num_bins)
    cdf = np.cumsum(counts)
    ax.plot(bin_edges[1:], cdf/cdf[-1], linewidth=4)

if __name__ == "__main__":
    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['weeplaces']    
    
    cities = ([file.replace('.pkl', '') for file in os.listdir(directory) if file.endswith('.pkl')])

    figure = plt.figure(figsize=(15, 8))
    ax = figure.add_subplot(111)
    legend=[]
    colors = cm.cubehelix(np.linspace(0, 1, len(cities)))
    for i, city in enumerate(cities):
        df = pd.read_pickle(directory + "{0}/independence_{0}.pkl".format(city))
        plot_cdf(df.power, ax, colors[i])
        legend.append(Line2D([], [], color=colors[i], linestyle='None', label=city))

    ax.legend(handles=legend,loc='upper left', frameon=False, ncol=1, bbox_to_anchor=(1.0, 1.0), columnspacing=0.,handletextpad=0.,borderpad=0.,fontsize=11.5)
    plt.xlabel('Independence percentage',fontsize=25)
    plt.ylabel('F(x)',fontsize=25)
    plt.xticks(np.arange(0, 1.1, step=0.1),fontsize=25, rotation=30)
    plt.yticks(np.arange(0, 1.1, step=0.1),fontsize=25)
    #plt.savefig(dir_in + 'cdf_%s.png' % (city))
    plt.show()
    plt.clf()


