from decimal import Decimal

from chain_harvester.adapters.morpho import AdaptiveCurveIrm, calculate_morpho_apr


def test_adaptive_curve_irm():
    irm = AdaptiveCurveIrm()
    rate, rate_at_target = irm.borrow_rate(
        169221400019394287275619863, 199829226406920439237253706, 1743759368
    )
    assert rate == 1212191443
    assert rate_at_target == 1268391679


def test_calculate_morpho_apr():
    apr, new_rate_at_target = calculate_morpho_apr(
        169221400019394287275619863,
        199829226406920439237253706,
        1743756563,
        1743759368,
        2.142084902e-9,
    )
    assert apr == Decimal("0.062939448925488000")
    assert new_rate_at_target == Decimal("2.070248874E-9")
