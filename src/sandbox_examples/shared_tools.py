from datetime import UTC, datetime


def calc_line_total(unit_price=0.0, quantity=1, tax_rate=0.0):
    subtotal = float(unit_price) * int(quantity)
    tax = subtotal * float(tax_rate)
    total = subtotal + tax
    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "total": round(total, 2),
    }


def discount_for_coupon(code=""):
    coupons = {
        "SPRING10": 0.10,
        "VIP15": 0.15,
        "TEAM20": 0.20,
    }
    return coupons.get(code.upper(), 0.0)


def utc_now_iso():
    return datetime.now(UTC).isoformat()


def shipping_for_weight_kg(weight_kg=0.0):
    weight = max(float(weight_kg), 0.0)
    if weight <= 0.5:
        return 3.5
    if weight <= 2.0:
        return 6.0
    if weight <= 5.0:
        return 9.5
    return 14.0
