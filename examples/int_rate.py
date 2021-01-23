''' some little examples

'''

import QuantLib as ql

rate = ql.InterestRate(0.05, ql.Actual360(), ql.Compounded, ql.Annual)
print(rate.rate())

daycount = rate.dayCounter().dayCount(ql.Date(1,1,2020), ql.Date(1,1,2021))
print(daycolittle examples
