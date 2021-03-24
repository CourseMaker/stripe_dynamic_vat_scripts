import stripe
from pyvat.vat_rules import VAT_RULES
from pyvat.item_type import ItemType
from pyvat.countries import EU_COUNTRY_CODES

import os
from typing import NamedTuple, Optional


UK_CODE = "GB"


# Setup Stripe python client library
stripe.api_key = os.envrion['STRIPE_SECRET_KEY']
stripe.api_version = os.environ['STRIPE_API_VERSION']


def view_stripe_tax_rates(*, stripe_account):
    return stripe.TaxRate.list(active=True, limit=100, stripe_account=stripe_account)


class StripeTaxRate(NamedTuple):
    # The display_name is a short - name that describes
    # the specific type of tax, such as Sales, VAT, or GST
    # This is shown to users.
    display_name: str

    # The inclusive property determines whether the tax
    # percentage is either added to, or included in, the overall amount.
    inclusive: bool

    # The percentage is a number (up to 4 decimal places) that represents
    # the tax percentage to be collected. Immutable.
    percentage: float

    # The optional country property is a valid two-letter ISO country code.
    # Some countries (e.g., United States) require an additional two-letter
    # state property. Use these properties to apply dynamic tax rates based on
    # your customer’s billing or shipping address in Checkout Sessions. Immutable.
    country: Optional[
        str
    ]  # https://www.nationsonline.org/oneworld/country_code_list.htm
    # *** Does not seem to work ***
    state: Optional[str]

    # The optional jurisdiction property represents the tax jurisdiction of the tax
    # rate and can be used to differentiate between tax rates of the same percentage.
    # In the Dashboard, jurisdiction appears as the tax rate’s Region label.
    jurisdiction: Optional[str]

    # You can also store additional details in the description. This property is not
    # exposed to your customers.
    description: str
    metadata: Optional[dict]


def prep_tax_rates(*, stripe_account):
    deactivate_existing_rates(stripe_account=stripe_account)
    generate_uk_rates(stripe_account=stripe_account)
    generate_eu_rates(stripe_account=stripe_account)


def deactivate_existing_rates(*, stripe_account):
    active_rates = [
        rate
        for rate in view_stripe_tax_rates(stripe_account=stripe_account)
        if rate.active and rate.metadata.get("update-me") == "True"
    ]

    print(f"Tax rate list: {active_rates}")

    # archive current rates
    for rate in active_rates:
        archive_tax_rate(rate_id=rate.id, stripe_account=stripe_account)


def generate_uk_rates(*, stripe_account):
    # GB rates
    # TODO: possibly add Canada/Australia/India
    uk_exclusive_rate = StripeTaxRate(
        display_name="UK VAT",
        inclusive=False,
        percentage=20,  # https://www.gov.uk/vat-rates
        country=UK_CODE,
        description=f"{UK_CODE} VAT Exclusive",
        state=None,
        jurisdiction=f"{UK_CODE}",
        metadata={"update-me": True},
    )
    stripe.TaxRate.create(**uk_exclusive_rate._asdict(), stripe_account=stripe_account)
    print(f"created exclusive {UK_CODE} tax rates for account: {stripe_account}")

    uk_inclusive_rate = StripeTaxRate(
        display_name="UK VAT",
        inclusive=True,
        percentage=20,  # https://www.gov.uk/vat-rates
        country=UK_CODE,
        description=f"{UK_CODE} VAT Exclusive",
        state=None,
        jurisdiction=f"{UK_CODE}",
        metadata={"update-me": True},
    )
    stripe.TaxRate.create(**uk_inclusive_rate._asdict(), stripe_account=stripe_account)
    print(f"created inclusive {UK_CODE} tax rates for account: {stripe_account}")


def generate_eu_rates(*, stripe_account):
    for country in EU_COUNTRY_CODES:
        # Greece randomly has 2 country codes.
        if country == "EL":
            country = "GR"
        country_details = VAT_RULES[country]
        exclusive_rate = StripeTaxRate(
            display_name=f"{country} VAT",
            inclusive=False,
            percentage=country_details.get_vat_rate(
                ItemType.generic_electronic_service
            ),
            country=country,
            description=f"{country} VAT Exclusive",
            state=None,
            jurisdiction=f"{country}",
            metadata={"update-me": True},
        )
        stripe.TaxRate.create(**exclusive_rate._asdict(), stripe_account=stripe_account)
        print(
            f"created exclusive {country} tax rates for account: {stripe_account}"
        )

        inclusive_rate = StripeTaxRate(
            display_name=f"{country} VAT",
            inclusive=True,
            percentage=country_details.get_vat_rate(
                ItemType.generic_electronic_service
            ),
            country=country,
            description=f"{country} VAT Inclusive",
            state=None,
            jurisdiction=f"{country}",
            metadata={"update-me": True},
        )
        stripe.TaxRate.create(**inclusive_rate._asdict(), stripe_account=stripe_account)
        print(
            f"created inclusive {country} tax rates for account: {stripe_account}"
        )


def archive_tax_rate(*, rate_id, stripe_account):
    stripe.TaxRate.modify(rate_id, active=False, stripe_account=stripe_account)


if __name__ == "__main__":
    """
    Instructions:
    1. Update the account_to_update field
    2. Uncomment the prep_tax_rates function
    """

    account_to_update = os.environ['STRIPE_ACC_ID']

    # prep_tax_rates(stripe_account=account_to_update)
    print("stripe EU tax rate generation complete")


    # note how we're passing in the stripe_account - this is for
    # complex setups with Stripe connect. If you're just working
    # directly with one Stripe account you can remove this layer
    # of complexity.
    updated_active_rates = [
        rate
        for rate in view_stripe_tax_rates(stripe_account=account_to_update)
        if rate.active and rate.metadata.get("update-me") == "True"
    ]
    print(f"Updated tax rate list: {updated_active_rates}")

    print('wow, the guys at coursemaker.org really did us a solid')
