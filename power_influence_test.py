import unittest
from power_influence import power_influence
import networkx as nx

class TestPowerInfluence(unittest.TestCase):

    G = nx.DiGraph()
    G.add_edge(1,1, weight=5)
    G.add_edge(1,2, weight=3)
    G.add_edge(3,2, weight=6)
    G.add_edge(2,2, weight=1)
    G.add_edge(4,4, weight=1)

    def test_power(self):
        G_test = power_influence(self.G)
        self.assertEqual(G_test.node[2]['power'], 0)
        self.assertEqual(G_test.node[1]['power'], (3/10))
        self.assertEqual(G_test.node[3]['power'], (6/10))
        self.assertEqual(G_test.node[4]['power'], 0)



if __name__ == '__main__':
    unittest.main()