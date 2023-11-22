from dataclasses import dataclass


@dataclass
class Endpoints:
    base: str = 'https://api.tbcbank.ge'
    access_token: str = f'{base}/tpay/access-token'
    create_payment: str = f'{base}/tpay/payments'
    execute_recurring: str = f'{base}/payments/execution'

    def get_payment(self, payid: str) -> str:
        return f'{self.base}/tpay/payments/{payid}'

    def cancel_payment(self, payid: str) -> str:
        return f'{self.base}/tpay/payments/{payid}/cancel'

    def complete_preauth(self, payid: str) -> str:
        return f'{self.base}/payments/{payid}/completion'

    def delete_recurring(self, recid) -> str:
        return f'{self.base}/tpay/payments/{recid}/delete'

