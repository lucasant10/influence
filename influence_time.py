import glob
import os
import pandas as pd
import json
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
import scipy.stats as ss
import numpy as np

def granger(df_g, t_slice, x, y, hour):
    x_tmp = df_g[(df_g.poi_id==x) & (df_g.hour==hour)].groupby(pd.Grouper(freq='W'))['hour'].count()
    y_tmp = df_g[(df_g.poi_id==y) & (df_g.hour==hour)].groupby(pd.Grouper(freq='W'))['hour'].count()
    x1 = np.nan_to_num(ss.zscore(x_tmp[t_slice].fillna(0)))
    y1 = np.nan_to_num(ss.zscore(y_tmp[t_slice].fillna(0)))
    tuples = list(zip(y1,x1))
    gc = grangercausalitytests(tuples, 2, addconst=True, verbose=False)
    return gc[1][0]['params_ftest'][1]


if __name__ == "__main__":

    all_files = glob.glob(os.path.join(os.getcwd() + "/graphs/", "*12H.csv"))
    dfs = []
    for filename in all_files:
        dfs.append(pd.read_csv(filename, header=None, names=['in','out', 'influence']))

    for i, tmp in enumerate(dfs):
        dfs[i].influence = tmp.influence.apply(lambda x: json.loads(x.replace("'",'"'))["weight"])

    df = pd.DataFrame(columns=['in','out', 'influence'])
    for dt_frame in dfs:
        df = df.merge(dt_frame, how = 'outer', on = ['in','out'])

    df = df.iloc[:,1:]
    df = df.fillna(0)

    sample = df[(df.iloc[:,2:] > 0).sum(axis=1) >5]

    df_g = pd.read_pickle('poi_tw.pkl')
    w = df_g.groupby(pd.Grouper(freq='W'))['hour'].count().index
    hour =12

    sample['p-value'] = sample.apply(lambda row: granger(df_g, w, row['in'], row['out'], hour), axis=1)


