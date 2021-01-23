
import QuantLib as ql

amount = 100
date = ql.Date(15,6,2020)
ap = ql.AmortizingPayment(amount, date)

print(ap.amount())
