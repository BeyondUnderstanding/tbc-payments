import datetime
from pydantic import BaseModel, Field
import enum
from typing import Optional, List


class Authentication(BaseModel):
    access_token: str
    expires_in: int
    token_type: str

    @property
    def expires_datetime(self) -> datetime.datetime:
        # TODO: Authentication.expires_datetime
        return datetime.datetime.now()


class PaymentCurrency(enum.Enum):
    EUR = 'EUR'
    USD = 'USD'
    GEL = 'GEL'


class PaymentAmount(BaseModel):
    total: float
    subtotal: float
    tax: float
    shipping: float
    currency: PaymentCurrency


class PaymentMethods(enum.Enum):
    web_qr = 4
    pan_card = 5
    ertguli_points = 6
    internet_bank = 7
    installment = 8
    apple_pay = 9


class InstallmentProduct(BaseModel):
    Price: float
    Quantity: int
    Name: Optional[str] = None


class PageLanguage(enum.Enum):
    KA = 'KA'
    EN = 'EN'


class PaymentLink(BaseModel):
    uri: str
    method: str
    rel: str


class PaymentResponse(BaseModel):
    payId: str
    status: str
    amount: float
    links: List[PaymentLink]
    transactionId: Optional[str]
    preAuth: bool
    recId: Optional[str]
    httpStatusCode: int
    developerMessage: Optional[str]
    userMessage: Optional[str]


class WebPaymentPayload(BaseModel):
    amount: PaymentAmount
    returnurl: str
    extra: Optional[str] = Field(default=None)
    expiration_minutes: Optional[int] = Field(default=None)
    methods: Optional[List[PaymentMethods]] = Field(default=None)
    installmentProducts: Optional[List[InstallmentProduct]] = Field(default=None)
    callbackUrl: Optional[str] = Field(default=None)
    preAuth: Optional[bool] = Field(default=None)
    language: Optional[PageLanguage] = Field(default=None)
    merchantPaymentId: Optional[str] = Field(default=None)
    skipInfoMessage: Optional[bool] = Field(default=None)
    saveCard: Optional[bool] = Field(default=None)
    saveCardToDate: Optional[str] = Field(default=None)


class PaymentDetails(BaseModel):
    payId: str
    status: str
    currency: str
    amount: float
    confirmedAmount: float
    returnedAmount: float
    links: Optional[str]
    transactionId: str
    paymentMethod: int
    recurringCard: Optional[dict]
    preAuth: bool
    httpStatusCode: int
    developerMessage: Optional[str]
    userMessage: Optional[str]
    isBnpl: bool


class CompletePreAuthResponse(BaseModel):
    status: str
    amount: float
    confirmedAmount: float
    httpStatusCode: int
    developerMessage: Optional[str]
    userMessage: Optional[str]