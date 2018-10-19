import unittest
from influence import generate_graphs
import networkx as nx
import pandas as pd
import numpy as np
from sklearn.utils import shuffle

class TestInfluence(unittest.TestCase):

    
    dates =  pd.date_range('20160101', periods = 6, freq='5H')
    dates2 =  pd.date_range('2016-01-01 10:15:00', periods = 2, freq='1H')
    dates3 =  pd.date_range('2016-01-01 20:10:00', periods = 2, freq='30min')
    dt = sorted(dates.append([dates2,dates3]))
    #00:00,05:00,10:00,10:15,11:15,  15:00,20:00,20:10,  20:40,01:00
    dataDf = pd.DataFrame({'date': dt,
        'user': np.array(['user1','user1','user1','user1','user1',  'user2','user2','user2',  'user3','user3']),
        'poi_id': np.array([1,2,2,3,1,  3,2,1,   1,1]),
        'impact': np.array([0.2,0.2,0.2,0.2,0.2,  0.1,0.9,0.9,  0.5,0.8]),
        'amenity': np.array(['L1','L1','L1','L1','L1',  'L2','L2','L2',  'L3','L3'])
        })
    dataDf = dataDf.set_index('date')
    dataDf['hour'] = dataDf.index.hour
    
    def test_generate_graphs(self):
        delta_t = 4    
        t_frame = 'W'
        for U, _ in generate_graphs(delta_t, self.dataDf, t_frame):
            self.assertTrue(U.has_edge(1,1,1))
            self.assertFalse(U.has_edge(1,2,1))
            self.assertTrue(U.has_edge(2,2,2))
            self.assertTrue(U.has_edge(2,3,2))
            self.assertTrue(U.has_edge(3,1,2))
            self.assertTrue(U.has_edge(3,3,3))
            self.assertFalse(U.has_edge(3,2,3))
            self.assertTrue(U.has_edge(2,1,2))
            self.assertAlmostEqual(U[1][1][1]['weight'], 1.5,1)
            self.assertAlmostEqual(U[2][2][2]['weight'], 1.3,1)
            self.assertAlmostEqual(U[2][3][2]['weight'], 0.2,1)
            self.assertAlmostEqual(U[2][3][2]['weight'], 0.2,1)
            self.assertAlmostEqual(U[3][1][2]['weight'], 0.2,1)
            self.assertAlmostEqual(U[3][3][3]['weight'], 0.1,1)
            self.assertAlmostEqual(U[2][1][2]['weight'], 0.9,1)



if __name__ == '__main__':
    unittest.main()