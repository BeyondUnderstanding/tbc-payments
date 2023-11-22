import dataclasses
import json
from typing import Optional, List

import requests

from exceptions import FailedRequest
from endpoints import Endpoints
from objects import (Authentication, PaymentAmount, PaymentMethods,
                     InstallmentProduct, PageLanguage, WebPaymentPayload,
                     PaymentResponse, PaymentDetails)


class Checkout:
    def __init__(self, client_id: str, client_secret: str, apikey: str):
        self.apikey = apikey
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth: Authentication = self.authenticate()

    def authenticate(self) -> Authentication:
        auth_req = requests.post(Endpoints.access_token,
                                 data={
                                     'client_id': self.client_id,
                                     'client_secret': self.client_secret
                                 },
                                 headers={
                                     'apikey': self.apikey,
                                     'Content-Type': 'application/x-www-form-urlencoded'
                                 })
        if not auth_req.status_code == 200:
            raise FailedRequest('Authentication request return not 200 status code', auth_req)

        return Authentication.model_validate_json(auth_req.json())

    def re_auth(self):
        self.auth = self.authenticate()

    def payment(self,
                amount: PaymentAmount,
                return_url: str,
                extra: str = None,
                expiration_minutes: int = None,
                methods: List[PaymentMethods] = None,
                installment_products: List[InstallmentProduct] = None,
                callback_url: str = None,
                pre_auth: bool = None,
                language: PageLanguage = PageLanguage.EN,
                merchant_payment_id: str = None,
                skip_info_message: bool = None,
                save_card: bool = None,
                save_card_to_date: str = None,  # MMYY example: 1123 (November 2023)
                ) -> PaymentResponse:
        payload = {'amount': amount, 'returnurl': return_url}

        if extra:
            payload['extra'] = extra
        if expiration_minutes:
            payload['expiration_minutes'] = expiration_minutes
        if methods:
            payload['methods'] = methods
        if installment_products:
            payload['installmentProducts'] = installment_products
        if callback_url:
            payload['callbackUrl'] = callback_url
        if pre_auth:
            payload['preAuth'] = pre_auth
        if language:
            payload['language'] = language
        if merchant_payment_id:
            payload['merchantPaymentId'] = merchant_payment_id
        if skip_info_message:
            payload['skipInfoMessage'] = skip_info_message
        if save_card:
            payload['saveCard'] = save_card
        if save_card_to_date:
            payload['saveCardToDate'] = save_card_to_date

        p = WebPaymentPayload.model_validate(payload)

        request = requests.post(Endpoints.create_payment,
                                json=p.model_dump(exclude_none=True, mode='json'),
                                headers={
                                    "accept": "application/json",
                                    "content-type": "application/json",
                                    "apikey": self.apikey,
                                    'Authorization': f'Bearer {self.auth.access_token}'
                                })

        if request.status_code == 401:
            raise FailedRequest('Authorization error', request)
        if request.status_code != 200:
            raise FailedRequest('Create payment request return not 200 status code', request)

        return PaymentResponse.model_validate_json(request.json())

    def get_payment(self, pay_id) -> PaymentDetails:
        request = requests.get(Endpoints.get_payment(pay_id),
                               headers={
                                   "content-type": "application/x-www-form-urlencoded",
                                   "apikey": self.apikey,
                                   'Authorization': f'Bearer {self.auth.access_token}'
                               })
        if request.status_code == 401:
            raise FailedRequest('Authorization error', request)
        if request.status_code != 200:
            raise FailedRequest('Get payment request return not 200 status code', request)

        return PaymentDetails.model_validate_json(request.json())
