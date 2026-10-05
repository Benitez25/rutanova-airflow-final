import json
from pathlib import Path
from decimal import Decimal
import pytest
from src.business import DataQualityError, money, validate_orders, validate_costs, reconcile, profitability
ROOT = Path(__file__).resolve().parents[1]

def fixture_data():
    return validate_orders(json.loads((ROOT/'api/orders.json').read_text())), validate_costs((ROOT/'inbox/delivery_costs.csv').read_text())

@pytest.mark.parametrize('bad',['-1','NaN','Infinity','invalid','1.234'])
def test_reject_bad_amounts(bad):
    with pytest.raises(DataQualityError):
        money(bad)

def test_decimal_arithmetic_and_zero_revenue():
    assert profitability('100.10','50.05','10.05') == (Decimal('40.00'),Decimal('40.00')/Decimal('100.10')*100)
    assert profitability('0','10','2') == (Decimal('-12.00'),None)

def test_negative_margin_is_valid():
    assert profitability('20','25','5')[0] == Decimal('-10.00')

def test_duplicate_csv_fails():
    with pytest.raises(DataQualityError,match='Duplicate'):
        validate_costs('order_id,delivery_cost,delivery_date\nRN-001,10,2026-10-01\nRN-001,12,2026-10-01\n')

def test_invalid_date_fails():
    with pytest.raises(DataQualityError,match='date'):
        validate_costs('order_id,delivery_cost,delivery_date\nRN-001,10,2026-02-30\n')

def test_missing_delivered_cost_fails():
    orders,costs=fixture_data()
    with pytest.raises(DataQualityError,match='without'):
        reconcile(orders,costs[1:])

def test_orphan_cost_fails():
    orders,costs=fixture_data()
    with pytest.raises(DataQualityError,match='unknown'):
        reconcile(orders,costs+[{'order_id':'RN-999'}])

def test_duplicate_api_fails():
    orders,_=fixture_data()
    with pytest.raises(DataQualityError,match='Duplicate'):
        validate_orders(orders + [orders[0]])

def test_cancelled_without_cost_is_valid():
    orders,costs=fixture_data()
    assert reconcile(orders,costs)=={'orders':18,'costs':15,'delivered':15}

def test_business_baseline():
    orders,costs=fixture_data();by_id={r['order_id']:r for r in costs}
    delivered=[r for r in orders if r['status']=='delivered']
    revenue=sum(money(r['revenue']) for r in delivered)
    margin=sum(profitability(r['revenue'],r['product_cost'],by_id[r['order_id']]['delivery_cost'])[0] for r in delivered)
    assert revenue == Decimal('2850.00')
    assert margin == Decimal('779.00')
