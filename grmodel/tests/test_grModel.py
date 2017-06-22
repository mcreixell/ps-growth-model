import unittest
import numpy as np


class TestgrMethods(unittest.TestCase):
    def setUp(self):
        from ..GrowthModel import GrowthModel

        self.GR = GrowthModel(selCol=5)

    def test_logpdf_sum(self):
        from ..GrowthModel import logpdf_sum 
        logpdf_sum(1,0,1)
        
    def test_preCalc(self):
        from ..GrowthModel import preCalc
        params = np.array([0.009, 0.016, 0.01, 0.008, 0.0007])
        t_interval = np.arange(0, 11, 1)
        for t in t_interval:
            preCalc(t,params)

    def test_logL(self):
        """ Test logL run """
        self.GR.logL(self.GR.lb)

    def test_integral_data(self):
        """ TODO: describe test """
        from ..GrowthModel import simulate

        params = np.array([0.009, 0.016, 0.01, 0.008])
        t_interval = np.arange(0, 10, .005)

        output = simulate(params, t_interval)

        # Test that we get back time and output
        self.assertEqual(len(output), 2000)


if __name__ == '__main__':
    unittest.main()
