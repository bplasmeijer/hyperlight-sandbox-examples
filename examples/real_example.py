from _common import build_sandbox, run_guest_code
from sandbox_examples.shared_tools import calc_line_total, discount_for_coupon, utc_now_iso


def main():
    sandbox = build_sandbox(
        tools=[
            ("calc_line_total", calc_line_total),
            ("discount_for_coupon", discount_for_coupon),
            ("utc_now_iso", utc_now_iso),
        ],
        domains=["https://httpbin.org"],
    )

    guest_code = """
    print('== Realistic Sandbox Example: Checkout + External Ping ==')

    items = [
        {'sku': 'MUG-RED', 'unit_price': 12.50, 'qty': 2},
        {'sku': 'TEE-BLK', 'unit_price': 24.00, 'qty': 1},
        {'sku': 'STK-PACK', 'unit_price': 5.00, 'qty': 3},
    ]
    tax_rate = 0.0825
    coupon = 'SPRING10'

    line_reports = []
    raw_total = 0.0

    for item in items:
        totals = call_tool(
            'calc_line_total',
            unit_price=item['unit_price'],
            quantity=item['qty'],
            tax_rate=tax_rate,
        )
        raw_total += totals['total']
        line_reports.append({
            'sku': item['sku'],
            'qty': item['qty'],
            'line_total': totals['total'],
        })

    discount_pct = call_tool('discount_for_coupon', code=coupon)
    discount_amount = round(raw_total * discount_pct, 2)
    final_total = round(raw_total - discount_amount, 2)

    ping = http_get('https://httpbin.org/status/200')
    echo = http_get('https://httpbin.org/get?source=hyperlight-real-example')
    now = call_tool('utc_now_iso')

    print(f'timestamp: {now}')
    print('line items:')
    for line in line_reports:
        print(f"  - {line['sku']} x{line['qty']} => ${line['line_total']}")

    print(f'raw total: ${round(raw_total, 2)}')
    print(f'coupon: {coupon} ({int(discount_pct * 100)}% off)')
    print(f'discount amount: ${discount_amount}')
    print(f'final total: ${final_total}')
    print(f'http status ping: {ping["status"]}')
    print(f'http echo status: {echo["status"]}')
    """
    run_guest_code(sandbox, guest_code)


if __name__ == "__main__":
    main()
