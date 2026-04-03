from _common import build_sandbox, run_guest_code

from sandbox_examples.shared_tools import (
    calc_line_total,
    discount_for_coupon,
    shipping_for_weight_kg,
    utc_now_iso,
)


def main():
    sandbox = build_sandbox(
        tools=[
            ("calc_line_total", calc_line_total),
            ("discount_for_coupon", discount_for_coupon),
            ("shipping_for_weight_kg", shipping_for_weight_kg),
            ("utc_now_iso", utc_now_iso),
        ],
        domains=["https://httpbin.org"],
    )

    guest_code = """
    print('== Function-Call Example: Shared Tools ==')

    products = [
        {'name': 'Notebook', 'unit_price': 9.90, 'qty': 4, 'weight_kg': 0.25},
        {'name': 'Keyboard', 'unit_price': 39.00, 'qty': 1, 'weight_kg': 0.85},
    ]
    tax_rate = 0.0725
    coupon = 'VIP15'

    subtotal = 0.0
    shipping = 0.0

    for p in products:
        line = call_tool(
            'calc_line_total',
            unit_price=p['unit_price'],
            quantity=p['qty'],
            tax_rate=tax_rate,
        )
        line_weight = p['weight_kg'] * p['qty']
        shipping += call_tool('shipping_for_weight_kg', weight_kg=line_weight)
        subtotal += line['total']
        print(f"{p['name']} x{p['qty']}: line=${line['total']}, ship=${round(shipping, 2)}")

    discount_pct = call_tool('discount_for_coupon', code=coupon)
    discount_amount = round(subtotal * discount_pct, 2)
    grand_total = round(subtotal + shipping - discount_amount, 2)

    http_ok = http_get('https://httpbin.org/status/200')
    stamp = call_tool('utc_now_iso')

    print(f'timestamp: {stamp}')
    print(f'subtotal: ${round(subtotal, 2)}')
    print(f'shipping: ${round(shipping, 2)}')
    print(f'discount ({coupon}): -${discount_amount}')
    print(f'grand total: ${grand_total}')
    print(f'http status: {http_ok["status"]}')
    """
    run_guest_code(sandbox, guest_code)


if __name__ == "__main__":
    main()
