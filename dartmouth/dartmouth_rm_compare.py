import sys
sys.path.append('../')
import os
import pandas as pd
import networkx as nx
import configparser
import multiprocessing as mp
from functools import partial
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def compare_metrics(metric1, metric2):
    m1 = df_rm[df_rm.metric == metric1].main_poi.unique()
    m2 = df_rm[df_rm.metric == metric2].main_poi.unique()
    set_diff1 = np.setdiff1d(m1,m2)
    set_diff2 = np.setdiff1d(m2,m1)
    tmp_list = [group_df(m1, metric1), group_df(m2, metric2)]
    #tmp_list = [group_df(set_diff1, metric1), group_df(set_diff2, metric2)]
    return pd.concat(tmp_list)

def group_df(set_diff, metric):
    result = df_rm[df_rm.metric.isin([metric]) & df_rm.main_poi.isin(set_diff)]
    result = result.groupby(['metric','main_poi'])['mean_users_before', 'mean_users_after'].mean()
    result['fall'] = ((result.mean_users_before - result.mean_users_after) / result.mean_users_before).round(2) * 100
    return result

def plot_comparison(metric):
    metrics = ['support', 'attract','independence','bf_power', 'eigcen_in', 'random', 'in_dg_cen', 'out_dg_cen', 'eigcen_out' , 'visits']
    metrics.remove(metric)
    metrics.remove('visits')
    df_list = list()
    for comp_metric in metrics:
        df_list.append(compare_metrics(metric,comp_metric))
    fig, ax = plt.subplots(1,8, sharey=True)
    for i, grp in enumerate(df_list):
        grp.boxplot(column=['fall'], by='metric',ax=ax[i], grid=False, fontsize=13)
        ax[i].set_title("")
        ax[i].set_xlabel("")
        ax[i].tick_params(axis='x', rotation=15)
    fig.suptitle('')
    fig.subplots_adjust( top=0.9, wspace=0.1)
    ax[0].set_ylabel('Fall percentage', fontsize=20)
    plt.show()

def plot_comparison_all():
    metrics = ['support', 'attract','independence','bf_power', 'eigcen_in', 'random', 'in_dg_cen', 'out_dg_cen', 'eigcen_out' , 'visits']
    metrics.remove('visits')
    df_list = list()
    for comp_metric in metrics:
        m = df_rm[df_rm.metric == comp_metric].main_poi.unique()
        result = df_rm[df_rm.metric.isin([comp_metric]) & df_rm.main_poi.isin(m)]
        result = result.groupby(['metric','main_poi'])['mean_users_before', 'mean_users_after'].mean()
        result['fall'] = ((result.mean_users_before - result.mean_users_after) / result.mean_users_before).round(2) * 100 
        df_list.append(result)
    tmp = pd.concat(df_list).reset_index()
    fig, ax  = plt.subplots(figsize = (10,7))    
    my_pal = {'support':"red", 'attract':"red",'independence':"red",'bf_power':'lightblue', 'eigcen_in':'lightblue', 'random':'lightblue', 'in_dg_cen':'lightblue', 'out_dg_cen':'lightblue', 'eigcen_out':'lightblue'}
    sns.boxplot(x='metric', y='fall', data=tmp,ax=ax, palette=my_pal, showfliers=False, order=metrics)
    ax.set_title("")
    ax.set_xlabel("")
    ax.tick_params(axis='x', rotation=20, labelsize=18)
    ax.tick_params(axis='y', labelsize=18)
    fig.suptitle('')
    ax.set_ylabel('Fall percentage', fontsize=20)
    plt.show()


if __name__ == "__main__":

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))
    directory = path['dartmouth']

    df_rm = pd.read_pickle(directory+"poi_remove_impact.pkl")

    # plot_comparison('support')
    # plot_comparison('attract')
    # plot_comparison('independence')
    plot_comparison_all()
