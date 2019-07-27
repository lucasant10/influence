import unittest
from power_influence import power_attract_influence, power_support_influence
import networkx as nx


class TestPowerInfluence(unittest.TestCase):

    H = nx.MultiDiGraph()
    H.add_edge('H', 1, '1_1', weight=8)
    H.add_edge(1,'H', '1_1', weight=2)
    H.add_edge(1, 2, '1_3', weight=2)
    H.add_edge(2, 3, '1_3', weight=2)
    H.add_edge(1, 3, '1_3', weight=4)
    H.add_edge('H', 2, '2_2', weight=6)
    H.add_edge(2,'H', '2_2', weight=2)
    H.add_edge(2,1, '2_1', weight=2)
    H.add_edge(2, 3, '2_3', weight=2)
    H.add_edge(2, 1, '2_1', weight=2)
    H.add_edge(1,'H','2_1', weight=2)
    H.add_edge('H',3,'3_3', weight=2)
    H.add_edge(3,'H','3_3', weight=2)
    H.add_edge(3,'H','2_3', weight=2)
    H.add_edge(3,'H','1_3', weight=6)

    G = nx.MultiDiGraph()
    G.add_edge('H', 1, 1, weight=8)
    G.add_edge(1,'H', 1, weight=2)
    G.add_edge(1, 2, 1, weight=2)
    G.add_edge(2, 4, 1, weight=2)
    G.add_edge(4, 5, 1, weight=2)
    G.add_edge(5, 'H', 1, weight=2)
    G.add_edge(1, 3, 1, weight=2)
    G.add_edge(3, 4, 1, weight=2)
    G.add_edge(4, 5, 1, weight=2)
    G.add_edge(5, 'H', 1, weight=2)
    G.add_edge('H', 4, 4, weight=4)
    G.add_edge(4,'H', 4, weight=2)
    G.add_edge(4, 5, 4, weight=2)
    G.add_edge(5, 'H', 4, weight=2)
    G.add_edge('H', 5, 5, weight=2)
    G.add_edge(5, 6, 5, weight=2)
    G.add_edge(6,'H', 5, weight=2)
    G.add_edge(1, 6, 1, weight=2)
    G.add_edge(6,'H', 1, weight=2)
    
    
    def test_power_support_influence(self):
        G_test = power_support_influence(self.H)
        self.assertAlmostEqual(G_test.node[3]['support'], 0, 2)
        self.assertAlmostEqual(G_test.node[1]['support'], 0.85, 2)
        self.assertAlmostEqual(G_test.node[2]['support'], 0.60, 2)
        # # test edge values
        self.assertAlmostEqual(G_test[2][3]['1_3']['weight'], 0.2, 2)
        self.assertAlmostEqual(G_test[2][3]['2_3']['weight'], 0.2, 2)
        self.assertAlmostEqual(G_test[1][2]['1_3']['weight'], 0.25, 2)
        self.assertAlmostEqual(G_test[1][3]['1_3']['weight'], 0.40, 2)
        self.assertAlmostEqual(G_test[2][1]['2_1']['weight'], 0.2, 2)
    
    def test_power_attract_influence(self):
        G_test = power_attract_influence(self.H)
        self.assertAlmostEqual(G_test.node[3]['attract'], 1.1, 2)
        self.assertAlmostEqual(G_test.node[1]['attract'], 0.25, 2)
        self.assertAlmostEqual(G_test.node[2]['attract'], 0.20, 2)
    #     # # test edge values
        self.assertAlmostEqual(G_test[2][3]['1_3']['weight'], 0.25, 2)
        self.assertAlmostEqual(G_test[2][3]['2_3']['weight'], 0.25, 2)
        self.assertAlmostEqual(G_test[1][2]['1_3']['weight'], 0.20, 2)
        self.assertAlmostEqual(G_test[1][3]['1_3']['weight'], 0.40, 2)
        self.assertAlmostEqual(G_test[2][1]['2_1']['weight'], 0.25, 2)
    
    # def test_power_attract_influence_2(self):
    #     G_test = power_attract_influence(self.G)
    #     self.assertAlmostEqual(G_test.node[6]['attract'], 0.58, 2)
    #     self.assertAlmostEqual(G_test.node[5]['attract'], 3.17, 2)
    #     self.assertAlmostEqual(G_test.node[4]['attract'], 2.5, 2)
    #     self.assertAlmostEqual(G_test.node[3]['attract'], 0.25, 2)
    #     self.assertAlmostEqual(G_test.node[2]['attract'], 0.25, 3)
    #     self.assertAlmostEqual(G_test.node[1]['attract'], 0, 2)
    
    # def test_power_support_influence_2(self):
    #     G_test = power_support_influence(self.G)
    #     self.assertAlmostEqual(G_test.node[6]['support'], 0, 2)
    #     self.assertAlmostEqual(G_test.node[5]['support'], 0.5, 2)
    #     self.assertAlmostEqual(G_test.node[4]['support'], 0.67, 2)
    #     self.assertAlmostEqual(G_test.node[3]['support'], 0.25, 2)
    #     self.assertAlmostEqual(G_test.node[2]['support'], 0.25, 2)
    #     self.assertAlmostEqual(G_test.node[1]['support'], 3.33, 2)


if __name__ == '__main__':
    unittest.main()
