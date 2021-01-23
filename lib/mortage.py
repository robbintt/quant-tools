'''

Future:
    - move finance objects to separate lib
'''

from moneyed import Money, USD
from decimal import Decimal


class Rate:
    """A rate object

    This rate object takes apr and returns a variety of rate formats
    It is especially useful for calculating rates between loan periods
    """

    def __init__(self, rate: Decimal, period: str):
        self.rate = rate
        self.period_definitions = {
            "daily": 365,  # except leap years
            "monthly": 12,
            "yearly": 1,
            #"continuously": 123,  # except leap years
        }
        self.validate_period(period)
        self.period = period
        self.yearly_periods = self.period_definitions[period]
        self.periodic_rate = rate / self.yearly_periods
        self.apy = (1 + self.periodic_rate) ** self.yearly_periods - 1

    class InvalidPeriod(Exception):
        """Exception class for invalid rate period string name"""

        pass

    def validate_period(self, period):
        if period in self.period_definitions.keys():
            return True
        else:
            raise self.InvalidPeriod(
                "Period string not defined in period_definitions keys."
            )


class Mortgage:
    """A mortgage object

    Mortgage should maintain some basic state of a mortgage template.

    Find or write a finance library for managing a decimal dollar type.

    Need relevant interest equations and dates as well.

    Features:
        - method for giving two dates and returning all values for that slice
    """

    def __init__(
        self,
        term: int,
        rate: Decimal,
        price: Money,
        down_payment: Money,
        value: Money = None,
    ):
        """
        term: months  # needs to be its own object?
        """
        self.term = term
        self.rate = rate
        # move to financial library
        self.price = price
        if value:
            self.value = value
        # is this a sane default?
        else:
            self.value = price
        self.down_payment = down_payment


if __name__ == "__main__":

    r = Rate(Decimal("0.05"), "monthly")
    print(r.period)
    print(r.rate)
    print(r.apy)

    m = Mortgage(30 * 12, Decimal("0.05"), Money(1000000, USD), Money(200000, USD))

    m.price
