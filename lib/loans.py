"""

Future:
    - move finance objects to separate lib
"""

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
            # "continuously": 123,  # except leap years
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
        rate: Rate,
        price: Money,
        down_payment: Money,
        value: Money or None = None,
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
        # explicitly for mortgage category loan
        self.principal = self.price - self.down_payment

        # this is just the first month's interest payment... too simple
        self.periodic_payment = self.principal * self.rate.periodic_rate

    def interest(self):
        self.term * self.rate


class Asset:
    ''' How to write comparisons against 2 assets over time? Asset operators?

    What else do we care about other than appreciation/depreciation with assets?
    '''
    def __init__(self, value: Money, rate: Rate):
        self.value = value
        self.rate = rate

    def projected_appreciation_percent(self, period):
        ''' total appreciation rate over period years
        '''
        return 100 * (((1 + self.rate.apy) ** period))

    def projected_appreciation(self, period):
        '''
        would it be useful to have a period class in rate and here?
        period would handle conversions between two period objects, like in a rate
        period also represents a slice of time, so rate/time is easier to handle...

        lets start with years and move on
        '''
        return self.value * (((1 + self.rate.apy) ** period))


class StandardLoan(Asset):

    def __init__(self, value, rate, term):
        super().__init__(value, rate)
        self.term = term
        # principal repayment for month n
        #p = (d - r * s) * ((1 + r)**n - 1) / r

    @property
    def monthly_payment(self):
        return self.rate.periodic_rate * self.value / (1 - (1 + self.rate.periodic_rate) ** (-1 * self.term))

    def princ_remaining(self, period):
        ''' return principal remaining

        If any additional principal payment is paid, this formula is no longer valid.
        '''
        if period not in range(0, self.term):
            raise(Exception(f"Loan period '{period}' requested was not in range of loan term range (0,{self.term})."))
        return (self.monthly_payment / self.rate.periodic_rate) * (1 - (1 / (1 + self.rate.periodic_rate)) ** (self.term - period))

    def ipmt(self, period):
        ''' return interest portion of the payment for the loan period
        '''
        return self.princ_remaining(period) * self.rate.periodic_rate

    def ppmt(self, period):
        ''' return principal portion of the payment for the loan period
        '''
        return self.monthly_payment - self.princ_remaining(period) * self.rate.periodic_rate

    def ipmt_range(self, period_range):
        # use a generator instead...
        return sum([self.ipmt(i) for i in period_range])

    def addl_princ_payment_interest_reduction(self, period, payment):
        """ Change in total interest paid when additional principal is paid during a period
        There is a reverse method called 'cash out refinance' that might also be interesting to implement
        I believe both can be implemented here within the same method
        """
        # loan basis changes... how to capture in model?
        # monthly payment does not change, so you must change ppmt 
        # period will also change
        # this is a stateful thing, so it should be part of the model creation or as a function input
        # this is almost a "new loan" since it's a breakpoint in which the loan term is reduced
        # basically you can recalculate the loan term from: principal, monthly_payment, rate



if __name__ == "__main__":

    '''
    r = Rate(Decimal("0.05"), "monthly")
    print(r.period, r.rate, r.apy)
    m = Mortgage(30 * 12, r, Money(1000000, USD), Money(200000, USD))
    # currently just has first payment, not done
    print(m.price, m.periodic_payment)
    '''

    loan_payload = {
            "value": Money(10000, USD),
            "rate": Rate(Decimal("0.08"), "monthly"),
            "term": 5*12 }

    #loan = StandardLoan(Money(10000, USD), Rate(Decimal("0.08"), "monthly"), 5*12)
    loan = StandardLoan(**loan_payload)
    print(loan.value, loan.rate.apy, loan.term, loan.monthly_payment)
    ipaid = 0
    for i in range(3, 15):
        print(loan.princ_remaining(i), loan.ipmt(i), loan.ppmt(i))
        ipaid += loan.ipmt(i)
    print(ipaid)

    r = range(3, 15)
    interest = loan.ipmt_range(r)
    print(f"Interest for range {r} is {interest}")

    '''
    a = Asset(Money(1000000, USD), r)
    print(a.projected_appreciation(5))
    print(a.projected_appreciation_percent(5))
    '''

    '''
    house = Asset(Money(1000000, USD), Rate(Decimal("0.03"), "yearly"))
    mortgage = Mortgage(30*12, Rate(Decimal("0.0295"), "monthly"), house.value, house.value*0.2)
    for i in range(1,31):
        # isn't a loan just someone else's asset that you pay on a schedule?
        # should loan inherit from asset?
        print(house.projected_appreciation(i) - house.value - mortgage.)
    '''


    '''
    car = Asset(Money(35000, USD), Rate(Decimal("-0.15"), "yearly"))
    for i in range(1, 11):
        print("Car value in year {}: {}, {} %".format(i, car.projected_appreciation(i), car.projected_appreciation_percent(i)))
    '''

    # do i want a state machine to advance the period and give the results?
    # or do i want a stateless model to give the result for a slice of the loan?
    # I intend to compose the mortgage class into a real estate investment model
    # so i will want to just call the modeled mortgage for a range of periods
    # then i can essentially advance the external states and internal states in-step
    # historic data for a mortgage is not needed
    # but i may want to handle tax rebates and exceptions somewhere

    # i should also use an asset class to write growth projections for assets
    # not really sure how to quantify growth, something like periodic compound growth
    # whatever the data i am using for projections...
    # plus historic data for the asset should be stored...

    # how will "rental" information be calculated, probably on the asset?
    # rent is, in theory, a type of interest
    #    - ideally rent is bound to property value, but rental markets are disjoint
    #    - rent vacancy rates, dated interior design, etc. provide addl inputs

    # what is the overarching model for a "rental property"
    #    - how does an asset model work? pretty simple?
    #    - mortgage model + rental model + asset model is sufficient?
    #    - the asset model can calculate periodic costs rental side and mortage side
    #    - the asset model can manage asset appreciation and tax advantage?
    #    - might be nice to have a simpler asset model and have mortage_asset_model inherit
