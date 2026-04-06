export interface ReportSummary {
  score: number
  score_band: string
  report_date: string
  total_accounts: number
  active_accounts: number
  closed_accounts: number
}

export interface Address {
  type: string
  address: string
  status: string
}

export interface PersonalInformation {
  name: string
  dob: string
  pan: string
  emails: string[]
  addresses: Address[]
  phone_numbers: string[]
  issues: string[]
}

export interface Account {
  account_id: string
  lender: string
  type: string
  status: string
  credit_limit?: number
  loan_amount?: number
  current_balance: number
  utilization_percent?: number
  overdue_amount: number
  payment_history: string[]
  remarks: string[]
}

export interface Delinquency {
  account_id: string
  type: string
  amount?: number
  impact: string
  days_past_due?: number
}

export interface Enquiry {
  lender: string
  date: string
  type: string
  amount: number
}

export interface Dispute {
  account_id: string
  field: string
  status: string
  remark: string
}

export interface CreditUtilization {
  total_limit: number
  used_limit: number
  utilization_percent: number
  status: string
}

export interface PaymentSummary {
  on_time_payments: number
  late_payments: number
  severe_delinquencies: number
}

export interface CreditReport {
  report_summary: ReportSummary
  personal_information: PersonalInformation
  accounts: Account[]
  delinquencies: Delinquency[]
  enquiries: Enquiry[]
  disputes: Dispute[]
  credit_utilization: CreditUtilization
  payment_summary: PaymentSummary
  risk_flags: string[]
  positive_factors: string[]
}
