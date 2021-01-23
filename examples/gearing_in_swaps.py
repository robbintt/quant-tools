''' From examples

https://quantlib-python-docs.readthedocs.io/en/latest/examples/fixedincome/gearing.html
'''
import QuantLib as ql
import pandas as pd

yts = ql.YieldTermStructureHandle(ql.FlatForward(2, ql.TARGET(), 0.05, ql.Actual360()))
engine = ql.DiscountingSwapEngine(yts)
index = ql.USDLibor(ql.Period('6M'), yts)

schedule = ql.MakeSchedule(ql.Date(15,6,2021), ql.Date(15,6,2023), ql.Period('6M'))
nominal = [10e6]


fixedLeg = ql.FixedRateLeg(schedule, index.dayCounter(), nominal, [0.05])
floatingLeg = ql.IborLeg(nominal, schedule, index)
swap = ql.Swap(fixedLeg, floatingLeg)
swap.setPricingEngine(engine)

print(f"Floating leg NPV: {swap.legNPV(1):,.2f}\n")
pd.DataFrame([{
    'fixingDate': cf.fixingDate().ISO(),
    'accrualStart': cf.accrualStartDate().ISO(),
    'accrualEnd': cf.accrualEndDate().ISO(),
    "paymentDate": cf.date().ISO(),
    'gearing': cf.gearing(),
    'forward': cf.indexFixing(),
    'rate': cf.rate(),
    "amount": cf.amount()
} for cf in map(ql.as_floating_rate_coupon, swap.leg(1))])
