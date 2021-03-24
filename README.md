*We are not accountants or affiliated with Stripe, do your own research*

# Stripe Dynamic Taxes
Useful scripts for [Stripe Dynamic Tax](https://stripe.com/docs/payments/checkout/taxes)

## Setup
1. You'll need a Stripe account
2. `pip3 install poetry`
3. `poetry install`
4. Set your environment variables: `STRIPE_SECRET_KEY`, `STRIPE_API_VERSION`, and `STRIPE_ACC_ID`
5. Uncomment `prep_tax_rates` in `generate_stripe_tax_rates.py` (if someone wants to do a PR with argparse that'd be cool)
6. Run `python generate_stripe_tax_rates.py`

## Maintenance
You'll want to keep an eye on the `pyvat` library and make sure it stays up-to-date

## Help Wanted
If you figure out how to do this for US Sales Tax - please open a PR/email me.