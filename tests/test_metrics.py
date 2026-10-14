import unittest
import numpy as np
import pandas as pd
from common.metrics import gini_from_auc
from LGD.src.evaluation import evaluate_lgd_model
from CCF.src.target import calculate_leq, calculate_ccf, reconstruct_ead_from_leq


class TestCreditMetrics(unittest.TestCase):
    def test_gini(self):
        self.assertAlmostEqual(gini_from_auc(0.5), 0.0)
        self.assertAlmostEqual(gini_from_auc(0.75), 0.5)

    def test_lgd_evaluation(self):
        y_true = [0.20, 0.40, 0.60]
        y_pred = [0.25, 0.35, 0.65]
        res = evaluate_lgd_model(y_true, y_pred, "TestModel")
        self.assertEqual(res["out_of_bounds_count"], 0)
        self.assertAlmostEqual(res["out_of_bounds_pct"], 0.0)
        self.assertAlmostEqual(res["mae"], 0.05)

    def test_ccf_target_and_ead(self):
        # Account: Limit=1000, Balance_obs=400, EAD_T=700
        # Undrawn = 600, Delta = 300 -> LEQ = 300 / 600 = 0.5
        leq = calculate_leq(ead_at_default=[700], balance_at_observation=[400], limit_at_observation=[1000])
        self.assertAlmostEqual(leq.iloc[0], 0.5)

        # Reconstruct EAD from predicted LEQ
        ead_reconstructed = reconstruct_ead_from_leq([400], [1000], [0.5])
        self.assertAlmostEqual(ead_reconstructed.iloc[0], 700.0)


if __name__ == "__main__":
    unittest.main()
