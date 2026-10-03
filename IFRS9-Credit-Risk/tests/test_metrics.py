from common.metrics import gini_from_auc

def test_gini():
    assert gini_from_auc(0.5) == 0.0
    assert gini_from_auc(0.75) == 0.5
