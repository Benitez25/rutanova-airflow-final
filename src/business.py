"""Business rules independent of Airflow, Docker and Snowflake."""
import csv
import io
import re
from datetime import date
from decimal import Decimal, InvalidOperation

class DataQualityError(ValueError):
    pass

def money(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise DataQualityError('Amount is not numeric') from None
    if not result.is_finite() or result < 0:
        raise DataQualityError('Amount must be finite and non-negative')
    if result != result.quantize(Decimal('0.01')):
        raise DataQualityError('Amount has more than two decimal places')
    return result.quantize(Decimal('0.01'))

def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'RN-\d{3,}', value):
        raise DataQualityError('Invalid order_id')
    return value

def iso_date(value):
    try:
        return date.fromisoformat(value).isoformat()
    except (ValueError, TypeError):
        raise DataQualityError('Invalid ISO date') from None

def validate_orders(payload):
    if not isinstance(payload, list) or not payload:
        raise DataQualityError('API must return a non-empty list')
    output, seen = [], set()
    for row in payload:
        try:
            oid = identifier(row['order_id'])
            if oid in seen:
                raise DataQualityError('Duplicate order_id in API')
            seen.add(oid)
            city = str(row['city']).strip()
            if not city:
                raise DataQualityError('City is missing')
            status = row['status']
            if status not in ('delivered', 'cancelled'):
                raise DataQualityError('Unsupported status')
            output.append({'order_id':oid, 'order_date':iso_date(row['order_date']), 'city':city,
                           'revenue':str(money(row['revenue'])), 'product_cost':str(money(row['product_cost'])), 'status':status})
        except (KeyError, TypeError):
            raise DataQualityError('API row has missing or invalid fields') from None
    return output

def validate_costs(text):
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != ['order_id', 'delivery_cost', 'delivery_date']:
        raise DataQualityError('CSV columns must be order_id,delivery_cost,delivery_date')
    output, seen = [], set()
    for row in reader:
        oid = identifier(row['order_id'])
        if oid in seen:
            raise DataQualityError('Duplicate order_id in CSV')
        seen.add(oid)
        output.append({'order_id':oid, 'delivery_cost':str(money(row['delivery_cost'])),
                       'delivery_date':iso_date(row['delivery_date'])})
    if not output:
        raise DataQualityError('CSV is empty')
    return output

def reconcile(orders, costs):
    delivered = {r['order_id'] for r in orders if r['status'] == 'delivered'}
    all_orders = {r['order_id'] for r in orders}
    cost_ids = {r['order_id'] for r in costs}
    if cost_ids - all_orders:
        raise DataQualityError('CSV contains unknown orders')
    if delivered - cost_ids:
        raise DataQualityError('Delivered orders without delivery cost')
    return {'orders': len(orders), 'costs': len(costs), 'delivered': len(delivered)}

def profitability(revenue, product_cost, delivery_cost):
    revenue = money(revenue)
    margin = revenue - money(product_cost) - money(delivery_cost)
    return margin, (margin / revenue * 100 if revenue else None)
