from scipy.stats
import kendalltau
import os
import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as pl
import seaborn as sns
import logging


def parallel(directory):
    try:
        logger.info(">>>>>> files from directory: %s" % directory)

        child_dirs = next(os.walk(directory))[1]
        for child in child_dirs:
            place = child
            child = directory + child + '/'
            logger.info(">>>>>> files from child directory: %s" % child)
            files = ([file for file in os.listdir(
                child) if file.endswith('.pkl')])
            files.sort()
            dic = dict()
            if len(files) > 3:
                for file in files:
                    df = pd.read_pickle(file)
                    dic[df.iloc[1].values[2]] = df.sort_values([df.columns[1]], ascending=False)[
                        'poi_id'][:10].values
                df_rnk = pd.DataFrame.from_dict(dic, orient='index').reset_index()

                mat = np.zeros((df_rnk.shape[0], df_rnk.shape[0]))
                for i in range(df_rnk.shape[0]):
                    for j in range(df_rnk.shape[0]):
                        mat[i, j] = round(kendalltau(
                            df_rnk.iloc[i][1:11], df_rnk.iloc[j][1:11])[0], 2)
                np.savetxt(child + 'matrix_{}.csv'.format(place),
                        mat, delimiter=",")

                mask = np.zeros_like(mat, dtype=np.bool)
                mask[np.triu_indices_from(mask, k=1)] = True
                f, ax = pl.subplots(figsize=(10, 8))
                sns.heatmap(mat, mask=mask, cmap="RdBu", square=True,
                            ax=ax, vmin=-1, annot=True, annot_kws={"size": 15})
                ax.set_yticklabels(df_rnk['index'].values,
                                rotation='horizontal', fontsize=20)
                ax.set_xticklabels(df_rnk['index'].values,
                                rotation='30', fontsize=20)
                pl.savefig(child + 'corr_{}.png'.format(place))
    except Exception as e:
        print("Unexpected error: {}".format(e))
        logger.exception(e)


if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('script_correlations_%s.log' % (
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

    cf = configparser.ConfigParser()
    cf.read("file_path.properties")
    path = dict(cf.items("file_path"))

    workers = (mp.cpu_count()-1)
    logger.info(">>>>>> number of workes: %i" % workers)
    pool = mp.Pool(processes=(workers))
    _ = pool.map(parallel, path.values())
