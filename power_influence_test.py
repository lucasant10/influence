import unittest
from power_influence import power_influence, power_outdegree_influence, power_indegree_influence, get_in_degree_weight, convert_to_digraph
import networkx as nx


class TestPowerInfluence(unittest.TestCase):

    G = nx.DiGraph()
    G.add_edge(1, 1, weight=5)
    G.add_edge(1, 2, weight=3)
    G.add_edge(2, 3, weight=1)
    G.add_edge(3, 2, weight=6)
    G.add_edge(2, 2, weight=1)
    G.add_edge(4, 4, weight=1)

    H = nx.MultiDiGraph()
    H.add_edge(1, 1, 1, weight=8)
    H.add_edge(1, 2, 1, weight=2)
    H.add_edge(2, 3, 1, weight=2)
    #H.add_edge(3,1,1, weight=2)
    H.add_edge(1, 3, 1, weight=4)
    H.add_edge(2, 2, 2, weight=6)
    H.add_edge(2, 3, 2, weight=2)
    H.add_edge(2, 1, 2, weight=2)
    H.add_edge(3, 3, 3, weight=2)

    def test_power(self):
        G_test = power_influence(self.G)
        self.assertEqual(G_test.node[2]['power'], 1)
        self.assertEqual(G_test.node[1]['power'], (3/10))
        self.assertEqual(G_test.node[3]['power'], (6/10))
        self.assertEqual(G_test.node[4]['power'], 0)

    def test_power_indegree_influence(self):
        G_test = power_indegree_influence(self.H)
        self.assertAlmostEqual(G_test.node[3]['power_in'], 0, 2)
        self.assertAlmostEqual(G_test.node[1]['power_in'], 0.85, 2)
        self.assertAlmostEqual(G_test.node[2]['power_in'], 0.60, 2)
        # test edge values
        self.assertAlmostEqual(G_test[2][3][1]['weight'], 0.20, 2)
        self.assertAlmostEqual(G_test[2][3][2]['weight'], 0.20, 2)
        self.assertAlmostEqual(G_test[1][2][1]['weight'], 0.25, 2)
        self.assertAlmostEqual(G_test[1][3][1]['weight'], 0.40, 2)
        #self.assertAlmostEqual(G_test[3][1][1]['weight'], 0.20,2)

    def test_power_outdegree_influence(self):
        G_test = power_outdegree_influence(self.H)
        self.assertAlmostEqual(G_test.node[3]['power_out'], 1.33, 2)
        self.assertAlmostEqual(G_test.node[1]['power_out'], 0.33, 2)
        self.assertAlmostEqual(G_test.node[2]['power_out'], 0.33, 2)
        # test edge values
        self.assertAlmostEqual(G_test[2][3]['weight'], 0.67, 2)
        self.assertAlmostEqual(G_test[1][2]['weight'], 0.33, 2)
        self.assertAlmostEqual(G_test[1][3]['weight'], 0.67, 2)
        self.assertAlmostEqual(G_test[2][1]['weight'], 0.33, 2)

    def test_get_in_degree_weight(self):
        self.assertEqual(get_in_degree_weight(self.H, 1), 10)
        self.assertEqual(get_in_degree_weight(self.H, 2), 8)
        self.assertEqual(get_in_degree_weight(self.H, 3), 10)

    def test_convert_to_digraph(self):
        G_test = convert_to_digraph(self.H)
        self.assertEqual(G_test[2][3]['weight'], 4)
        self.assertEqual(G_test[1][2]['weight'], 2)
        self.assertEqual(G_test[1][3]['weight'], 4)
        self.assertEqual(G_test[2][1]['weight'], 2)
        self.assertEqual(G_test[2][2]['weight'], 6)
        self.assertEqual(G_test[1][1]['weight'], 8)
        self.assertEqual(G_test[3][3]['weight'], 2)


if __name__ == '__main__':
    unittest.main()
