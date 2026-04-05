import type { Account } from '../../services/types'
import { formatInr, numOr } from '../../utils/formatInr'
import SectionCard from './SectionCard'

interface Props {
  accounts: Account[]
}

const paymentBadge = (code: string) => {
  if (code === '000') return <span className="inline-block w-7 h-7 rounded-full bg-green-100 text-green-700 text-xs font-bold flex items-center justify-center">✓</span>
  const days = parseInt(code, 10)
  if (days >= 90) return <span className="inline-block w-7 h-7 rounded-full bg-red-100 text-red-700 text-xs font-bold flex items-center justify-center">{days}</span>
  if (days >= 30) return <span className="inline-block w-7 h-7 rounded-full bg-orange-100 text-orange-700 text-xs font-bold flex items-center justify-center">{days}</span>
  return <span className="inline-block w-7 h-7 rounded-full bg-slate-100 text-slate-500 text-xs font-bold flex items-center justify-center">{code}</span>
}

const statusBadge = (status: string) => {
  const map: Record<string, string> = {
    Active: 'bg-green-50 text-green-700',
    'Written-off': 'bg-red-50 text-red-700',
    Closed: 'bg-slate-100 text-slate-500',
  }
  return (
    <span className={`text-xs px-2 py-1 rounded-full font-medium ${map[status] ?? 'bg-slate-100 text-slate-600'}`}>
      {status}
    </span>
  )
}

export default function AccountsTable({ accounts }: Props) {
  return (
    <SectionCard
      title="Accounts"
      badge={<span className="text-xs bg-brand-50 text-brand-700 px-2 py-1 rounded-full font-medium">{accounts.length} accounts</span>}
    >
      <div className="space-y-4">
        {accounts.map((acc) => (
          <div key={acc.account_id} className="border border-slate-100 rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 bg-slate-50/70">
              <div>
                <p className="font-semibold text-slate-900 text-sm">{acc.lender}</p>
                <p className="text-xs text-slate-500">{acc.type} · {acc.account_id}</p>
              </div>
              {statusBadge(acc.status)}
            </div>
            <div className="px-4 py-3 grid grid-cols-2 sm:grid-cols-4 gap-3">
              {acc.credit_limit != null && (
                <MiniStat label="Credit Limit" value={formatInr(acc.credit_limit)} />
              )}
              {acc.loan_amount != null && (
                <MiniStat label="Loan Amount" value={formatInr(acc.loan_amount)} />
              )}
              <MiniStat label="Current Balance" value={formatInr(acc.current_balance)} />
              <MiniStat
                label="Overdue"
                value={formatInr(acc.overdue_amount)}
                highlight={numOr(acc.overdue_amount) > 0}
              />
              {acc.utilization_percent != null && (
                <MiniStat
                  label="Utilization"
                  value={`${numOr(acc.utilization_percent)}%`}
                  highlight={numOr(acc.utilization_percent) > 70}
                />
              )}
            </div>
            <div className="px-4 pb-3">
              <p className="text-xs text-slate-500 font-medium mb-2">Payment History (DPD)</p>
              <div className="flex flex-wrap gap-1">
                {(acc.payment_history ?? []).map((code, i) => (
                  <span key={i}>{paymentBadge(code)}</span>
                ))}
              </div>
            </div>
            {(acc.remarks ?? []).length > 0 && (
              <div className="px-4 pb-4">
                <div className="bg-red-50 rounded-lg px-3 py-2">
                  <ul className="space-y-0.5">
                    {(acc.remarks ?? []).map((r) => (
                      <li key={r} className="text-xs text-red-700">{r}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </SectionCard>
  )
}

function MiniStat({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div>
      <p className="text-xs text-slate-500">{label}</p>
      <p className={`text-sm font-semibold ${highlight ? 'text-red-600' : 'text-slate-800'}`}>{value}</p>
    </div>
  )
}
