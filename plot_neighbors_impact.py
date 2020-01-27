from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D      
import pandas as pd
import numpy as np
import configparser

datasets = ['Dartmouth','USC','KTH']
markers = ['v','^','s','o','p','*','P','X','1','d','>']
metrics = ['support','attract','bf_power','eigcen_in', 'eigcen_out','in_dg_cen','out_dg_cen','pager_rank','betweeness','random','independence']
metrics_colors = {"support": '#b30600', "attract": '#b30600', "bf_power": '#0054b3',"eigcen_in": '#0054b3',"eigcen_out": '#0054b3',\
            "in_dg_cen": '#0054b3', "out_dg_cen": '#0054b3', "pager_rank": '#0054b3',"betweeness": '#0054b3',"random": '#00b35f',"independence": '#b30600'}

    
def df_fall_mean(df):
    df_list = list()
    for metric in metrics:
        m = df[df.metric == metric].main_poi.unique()
        result = df[df.metric.isin([metric]) & df.main_poi.isin(m)]
        result = result.groupby(['metric','main_poi'])['mean_users_before', 'mean_users_after'].mean()
        result['fall'] = ((result.mean_users_before - result.mean_users_after) / result.mean_users_before).round(2) * 100 
        df_list.append(result)
    return pd.concat(df_list).reset_index()

def newline(ax,p1, p2, color='black'):
    l = Line2D([p1[0],p2[0]], [p1[1],p2[1]], color=color, alpha=0.3,zorder=1,lw=2.3, solid_capstyle='round')
    ax.add_line(l)
    return l

if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))

    fig, ax = plt.subplots(1,3,figsize=(10,4),facecolor='w')

    num_models = len(metrics)
    gap = 1 #size of the gap between each line
    maxy = num_models
    maxg = 0
    ming = np.inf
    yh = 0
    for i, dataset in enumerate(datasets):
        directory = path["dartmouth"]
        df_rm = pd.read_pickle(directory+"poi_remove_impact.pkl")
        df = df_fall_mean(df_rm)
        maxg = maxg if maxg > df.fall.max() else df.fall.max()
        ming = ming if ming < df.fall.min() else df.fall.min()
        for j, metric in enumerate(metrics):
            mean = df[df.metric==metric].fall.mean()
            boot_up = df[df.metric==metric].fall.max()
            boot_low = df[df.metric==metric].fall.min()
            maxv = max(mean,boot_up)  #maximum value for marker or line
            minv = min(mean,boot_low) #minimum value for marker or line
            yh = j 
            #line
            newline(ax[i],[boot_up,yh],[boot_low,yh], color=metrics_colors[metric])
            #markers
            ax[i].scatter(y=yh, x = mean, zorder=2, s=60, color=metrics_colors[metric], edgecolor='k', marker = markers[j], alpha=0.8)
            
        # Decoration
        ax[i].set_facecolor('w')
        ax[i].set_title(dataset, fontdict={'size':23},loc='center')
        ax[i].set_xticks(np.arange(ming, maxg + 10, 10))
        ax[i].set(xlim=(ming-1.05,maxg*1.05), ylim=(-0.4, maxy))
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['bottom'].set_visible(False)
        ax[i].get_yaxis().set_visible(False)
        ax[i].invert_yaxis()

    #Legend
    legend=[]
    for j, metric in enumerate(metrics):
        legend.append(Line2D([], [], color=metrics_colors[metric], linestyle='None',marker=markers[j],markersize=10, label=metric))
    ax[-1].legend(handles=legend,loc='upper left', frameon=False, ncol=1, bbox_to_anchor=(1.0, 1.0), columnspacing=0.,handletextpad=0.,borderpad=0.,fontsize=11.5)
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.01, hspace=0.05)
    #plt.savefig("results_www", bbox_inches = 'tight', pad_inches = 0)
    plt.show()    
