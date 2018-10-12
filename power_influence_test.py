import unittest
from power_influence import power_influence, power_indirect_influence
import networkx as nx

class TestPowerInfluence(unittest.TestCase):

    G = nx.DiGraph()
    G.add_edge(1,1, weight=5)
    G.add_edge(1,2, weight=3)
    G.add_edge(2,3, weight=1)
    G.add_edge(3,2, weight=6)
    G.add_edge(2,2, weight=1)
    G.add_edge(4,4, weight=1)

    H = nx.MultiDiGraph()
    H.add_edge(1,1,1, weight=8)
    H.add_edge(1,2,1, weight=2)
    H.add_edge(2,3,1, weight=2)
    H.add_edge(1,3,1, weight=4)
    H.add_edge(2,2,2, weight=6)
    H.add_edge(2,3,2, weight=2)
    H.add_edge(2,1,2, weight=2)
    H.add_edge(3,3,3, weight=2)
    H.add_edge(3,1,3, weight=2)
    

    def test_power(self):
        G_test = power_influence(self.G)
        self.assertEqual(G_test.node[2]['power'], 1)
        self.assertEqual(G_test.node[1]['power'], (3/10))
        self.assertEqual(G_test.node[3]['power'], (6/10))
        self.assertEqual(G_test.node[4]['power'], 0)


    
    def test_indirect_power(self):
        G_test = power_indirect_influence(self.H)
        self.assertAlmostEqual(G_test.node[3]['power'], 0.16,1)
        self.assertAlmostEqual(G_test.node[1]['power'], 0.85,2)
        self.assertAlmostEqual(G_test.node[2]['power'], 0.56,1)
        #test edge values
        self.assertAlmostEqual(G_test[2][3][1]['weight'], 0.2,1)
        self.assertAlmostEqual(G_test[2][3][2]['weight'], 0.2,1)
        self.assertAlmostEqual(G_test[1][2][1]['weight'], 0.25,1)
        self.assertAlmostEqual(G_test[1][3][1]['weight'], 0.4,1)


if __name__ == '__main__':
    unittest.main()