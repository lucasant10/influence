import unittest
from power_influence import power_attract_influence, power_support_influence
import networkx as nx


class TestPowerInfluence(unittest.TestCase):

    H = nx.MultiDiGraph()
    H.add_edge('H', 1, 1, weight=8)
    H.add_edge(1,'H', 1, weight=2)
    H.add_edge(1, 2, 1, weight=2)
    H.add_edge(2, 3, 1, weight=2)
    H.add_edge(1, 3, 1, weight=4)
    H.add_edge('H', 2, 2, weight=6)
    H.add_edge(2,'H', 2, weight=2)
    H.add_edge(1,'H', 2, weight=2)
    H.add_edge(2, 3, 2, weight=2)
    H.add_edge(2, 1, 2, weight=2)
    H.add_edge('H',3, 3, weight=2)
    H.add_edge(3,'H', 3, weight=2)
    H.add_edge(3,'H', 2, weight=2)
    H.add_edge(3,'H', 1, weight=6)

    def test_power_support_influence(self):
        G_test = power_support_influence(self.H)
        self.assertAlmostEqual(G_test.node[3]['support'], 0, 2)
        self.assertAlmostEqual(G_test.node[1]['support'], 0.85, 2)
        self.assertAlmostEqual(G_test.node[2]['support'], 0.60, 2)
        # test edge values
        self.assertAlmostEqual(G_test[2][3][1]['weight'], 0.20, 2)
        self.assertAlmostEqual(G_test[2][3][2]['weight'], 0.20, 2)
        self.assertAlmostEqual(G_test[1][2][1]['weight'], 0.25, 2)
        self.assertAlmostEqual(G_test[1][3][1]['weight'], 0.40, 2)
        self.assertAlmostEqual(G_test[2][1][2]['weight'], 0.20, 2)

    def test_power_attract_influence(self):
        G_test = power_attract_influence(self.H)
        self.assertAlmostEqual(G_test.node[3]['attract'], 1.10, 2)
        self.assertAlmostEqual(G_test.node[1]['attract'], 0.25, 2)
        self.assertAlmostEqual(G_test.node[2]['attract'], 0.20, 2)
        # test edge values
        self.assertAlmostEqual(G_test[2][3][1]['weight'], 0.25, 2)
        self.assertAlmostEqual(G_test[2][3][2]['weight'], 0.25, 2)
        self.assertAlmostEqual(G_test[1][2][1]['weight'], 0.20, 2)
        self.assertAlmostEqual(G_test[1][3][1]['weight'], 0.40, 2)
        self.assertAlmostEqual(G_test[2][1][2]['weight'], 0.25, 2)

if __name__ == '__main__':
    unittest.main()
