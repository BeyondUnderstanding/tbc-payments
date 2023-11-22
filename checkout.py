from typing import List
import requests
from exceptions import FailedRequest
from endpoints import Endpoints as endpnts
from .models import (Authentication, PaymentAmount, PaymentMethods,
                     InstallmentProduct, PageLanguage, WebPaymentPayload,
                     PaymentResponse, PaymentDetails, CompletePreAuthResponse)


Endpoints = endpnts()


class Checkout:
    """
    Methods for integrating TBC E-Commerce payments in Python
    """
    def __init__(self, client_id: str, client_secret: str, apikey: str):
        self.apikey = apikey
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth: Authentication = self.authenticate()

    def authenticate(self) -> Authentication:
        """
        Authenticates client with client_id(merchant_id), client_secret and apikey
        Returns Authentication object with access_token, expires_in, token_type

        https://developers.tbcbank.ge/reference/checkout-get-access-token-api

        :return: Authentication
        """
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

    def re_auth(self) -> None:
        """
        Refresh access_token
        :return: None
        """
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
        """
        Initiate TBC Checkout web payment

        https://developers.tbcbank.ge/reference/checkout-create-web-payment-api

        :param amount: PaymentAmount object
        :param return_url: url to redirect user after finishing payment
        :param extra: additional parameter for merchant specific info (optional). only non-unicode (ANS) symbols allowed. max length 25. This parameter will appear in the account statement
        :param expiration_minutes: payment initiation expiration time in minutes.
        :param methods: PaymentMethods list
        :param installment_products: InstallmentProduct list
        :param callback_url: when payment status changes to final status, POST request containing PaymentId in the body will be sent to given URL.
        :param pre_auth: specify if pre-authorization is needed for the transaction.
        :param language: PageLanguage object
        :param merchant_payment_id: Merchant-side payment identifier
        :param skip_info_message: If true is passed, TBC checkout info message will be skipped and customer will be redirected to merchant.
        :param save_card: Specify if saving card function is needed.
        :param save_card_to_date: The date until the card will be saved can be passed in following format "MMYY".
        :return: PaymentResponse
        :raises FailedRequest: Response status code is not 200
        """
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

    def get_payment(self, pay_id: str) -> PaymentDetails:
        """
        Request returns payment status and details for given payId.

        https://developers.tbcbank.ge/reference/checkout-get-checkout-payment-details-api

        :param pay_id: Checkout payment identifier
        :return: PaymentDetails
        :raises FailedRequest: Response status code is not 200
        """
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

    def cancel_checkout(self, pay_id: str, amount: float = None):
        """
        Request cancels payment for given payId.

        https://developers.tbcbank.ge/reference/checkout-cancel-checkout-payment-api

        :param pay_id: Checkout payment identifier
        :param amount: In case of partial cancellation of payment, corresponding amount should be passed in request body. Passed amount should not exceed transaction amount
        :return: bool
        :raises FailedRequest: Response status code is not 200
        """
        request = requests.post(Endpoints.cancel_payment(pay_id),
                                json={'amount': amount} if amount else None,
                                headers={
                                    "content-type": "application/json",
                                    "apikey": self.apikey,
                                    'Authorization': f'Bearer {self.auth.access_token}'
                                })
        if request.status_code == 400:
            # TODO: Complete logic
            ...
        if request.status_code == 401:
            # TODO: Complete logic
            ...
        if request.status_code != 200:
            raise FailedRequest('Cancel payment request return not 200 status code', request)
        return True

    def complete_preauth(self, pay_id: str, amount: float) -> CompletePreAuthResponse:
        """
        Request completes pre-authorized payment for given payId.

        https://developers.tbcbank.ge/reference/complete-pre-authorized-payment-1

        :param pay_id: Checkout payment identifier
        :param amount: amount to be confirmed (should not exceed transaction amount). if confirmed amount is less than the original transaction amount, difference is automatically returned to the customer.
        :return: CompletePreAuthResponse
        :raises FailedRequest: Response status code is not 200
        """
        request = requests.post(Endpoints.complete_preauth(pay_id),
                                json={'amount': amount},
                                headers={
                                    "content-type": "application/json",
                                    "apikey": self.apikey,
                                    'Authorization': f'Bearer {self.auth.access_token}'
                                })
        if request.status_code == 400:
            # TODO: Complete logic
            ...
        if request.status_code == 401:
            # TODO: Complete logic
            ...
        if request.status_code != 200:
            raise FailedRequest('Complete pre-auth request return not 200 status code', request)

        return CompletePreAuthResponse.model_validate_json(request.json())

    def execute_recurring(self):
        # TODO: Complete logic
        ...

    def delete_recurring(self):
        # TODO: Complete logic
        ...
