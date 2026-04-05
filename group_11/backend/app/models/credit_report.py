from pydantic import BaseModel
from typing import Optional


class ReportSummary(BaseModel):
    score: int
    score_band: str
    report_date: str
    total_accounts: int
    active_accounts: int
    closed_accounts: int


class Address(BaseModel):
    type: str
    address: str
    status: str


class PersonalInformation(BaseModel):
    name: str
    dob: str
    pan: str
    emails: list[str]
    addresses: list[Address]
    phone_numbers: list[str]
    issues: list[str]


class Account(BaseModel):
    account_id: str
    lender: str
    type: str
    status: str
    credit_limit: Optional[int] = None
    loan_amount: Optional[int] = None
    current_balance: int
    utilization_percent: Optional[int] = None
    overdue_amount: int
    payment_history: list[str]
    remarks: list[str]


class Delinquency(BaseModel):
    account_id: str
    type: str
    amount: Optional[int] = None
    impact: str
    days_past_due: Optional[int] = None


class Enquiry(BaseModel):
    lender: str
    date: str
    type: str
    amount: int


class Dispute(BaseModel):
    account_id: str
    field: str
    status: str
    remark: str


class CreditUtilization(BaseModel):
    total_limit: int
    used_limit: int
    utilization_percent: int
    status: str


class PaymentSummary(BaseModel):
    on_time_payments: int
    late_payments: int
    severe_delinquencies: int


class CreditReport(BaseModel):
    report_summary: ReportSummary
    personal_information: PersonalInformation
    accounts: list[Account]
    delinquencies: list[Delinquency]
    enquiries: list[Enquiry]
    disputes: list[Dispute]
    credit_utilization: CreditUtilization
    payment_summary: PaymentSummary
    risk_flags: list[str]
    positive_factors: list[str]
