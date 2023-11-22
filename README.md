# tbc-payments
tbcbank.ge Python 3 API Wrapper

## Install
```shell
pip3 install tbc-payments
```

## How to

### Create order
```python
from tbc_payments import Checkout
from tbc_payments.models import InstallmentProduct, PaymentAmount, PaymentCurrency, PaymentMethods, PaymentResponse
from tbc_payments.exceptions import FailedRequest

payment_client = Checkout(
    client_id = '',
    client_secret = '',
    apikey = ''
)

amount = PaymentAmount.model_validate({
    'total': 100.0,
    'subtotal': 90.0,
    'tax': 5.0,  # may be zero
    'shipping': 5.0,  # may be zero
    'currency': PaymentCurrency.GEL
})

products = [
    InstallmentProduct.model_validate({'Price': 45.0, 'Quantity': 1, 'Name': 'Foo'}),
    InstallmentProduct.model_validate({'Price': 45.0, 'Quantity': 1, 'Name': 'Bar'}),
]

new_order: PaymentResponse = payment_client.payment(amount=amount,
                                   return_url='https://example.com/path/to/redirect_url',
                                   installment_products=products,
                                   callback_url='https://example.com/path/to/callback_url',
                                   methods=[PaymentMethods.web_qr, PaymentMethods.apple_pay, PaymentMethods.internet_bank])
print(new_order.payId)  # Pay id 
print(new_order.links)  # Payment links
print(new_order.status) # Payments status

```
