from chain_harvester.adapters.morpho import AdaptiveCurveIrm


def test_adaptive_curve_irm():
    irm = AdaptiveCurveIrm()
    rate = irm.borrow_rate(116964899942613682796603519, 96477486297720518303877851, 1737384779)
    assert rate == 13154021334
