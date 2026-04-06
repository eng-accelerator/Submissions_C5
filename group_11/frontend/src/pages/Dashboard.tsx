import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import ScoreGauge from '../components/ScoreGauge'
import { getDashboardOverview, getInsights, getPayoffPlan, getBudgetAnalysis } from '../services/api'
import type { DashboardOverview, Insight } from '../services/api'

function formatINR(n: number) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n)
}

const INSIGHT_STYLES: Record<string, { bg: string; border: string; icon: string }> = {
  critical: { bg: 'bg-red-50', border: 'border-red-200', icon: '!!' },
  warning: { bg: 'bg-amber-50', border: 'border-amber-200', icon: '!' },
  positive: { bg: 'bg-green-50', border: 'border-green-200', icon: '+' },
  tip: { bg: 'bg-blue-50', border: 'border-blue-200', icon: 'i' },
}

export default function Dashboard() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null)
  const [insights, setInsights] = useState<Insight[]>([])
  const [payoff, setPayoff] = useState<any>(null)
  const [budget, setBudget] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [ov, ins, pf, bg] = await Promise.all([
          getDashboardOverview(),
          getInsights(),
          getPayoffPlan(),
          getBudgetAnalysis(),
        ])
        setOverview(ov)
        setInsights(ins.insights)
        setPayoff(pf)
        setBudget(bg)
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navbar />
        <div className="pt-20 text-center text-slate-500">Loading dashboard...</div>
      </div>
    )
  }

  if (error || !overview) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navbar />
        <div className="pt-20 text-center text-red-500">
          Failed to load dashboard: {error || 'Unknown error'}
          <br />
          <span className="text-sm text-slate-500">Make sure the backend is running on port 8001</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="pt-20 pb-12 px-4 max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold text-slate-900 mb-6">Financial Dashboard</h1>

        {/* Top cards row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-2xl p-5 border border-slate-200 flex flex-col items-center">
            <ScoreGauge score={overview.credit_score} band={overview.credit_score_band} size="sm" />
          </div>
          <StatCard label="Total Debt" value={formatINR(overview.total_debt)} sub={`${overview.debt_count} accounts`} color="red" />
          <StatCard label="Monthly Income" value={formatINR(overview.monthly_income)} sub={`Expenses: ${formatINR(overview.monthly_expenses)}`} color="green" />
          <StatCard label="Overdue" value={formatINR(overview.total_overdue)} sub={`Min payments: ${formatINR(overview.total_min_payments)}/mo`} color="amber" />
        </div>

        {/* AI Insights */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-slate-900 mb-3">AI Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {insights.map((ins, i) => {
              const style = INSIGHT_STYLES[ins.type] || INSIGHT_STYLES.tip
              return (
                <div key={i} className={`${style.bg} ${style.border} border rounded-xl p-4`}>
                  <div className="font-medium text-slate-900 text-sm mb-1">{ins.title}</div>
                  <div className="text-sm text-slate-600">{ins.description}</div>
                </div>
              )
            })}
          </div>
        </section>

        {/* Payoff Strategies */}
        {payoff?.strategies?.length > 0 && (
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-slate-900 mb-3">
              Debt Payoff Strategies
              <span className="text-sm font-normal text-slate-500 ml-2">
                (with {formatINR(payoff.extra_monthly_payment)}/mo extra payment)
              </span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {payoff.strategies.map((s: any, i: number) => (
                <div
                  key={i}
                  className={`bg-white rounded-2xl p-5 border-2 ${
                    s.strategy === payoff.recommendation ? 'border-brand-500' : 'border-slate-200'
                  }`}
                >
                  {s.strategy === payoff.recommendation && (
                    <span className="text-xs font-medium text-brand-600 bg-brand-50 px-2 py-0.5 rounded-full">Recommended</span>
                  )}
                  <h3 className="text-base font-semibold text-slate-900 mt-1 capitalize">{s.strategy} Strategy</h3>
                  <div className="mt-3 space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Time to debt-free</span>
                      <span className="font-medium">{s.debt_free_date}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Total interest</span>
                      <span className="font-medium text-red-600">{formatINR(s.total_interest)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Total paid</span>
                      <span className="font-medium">{formatINR(s.total_paid)}</span>
                    </div>
                  </div>
                  {s.payoff_order?.length > 0 && (
                    <div className="mt-3 text-xs text-slate-500">
                      <div className="font-medium text-slate-700 mb-1">Payoff order:</div>
                      {s.payoff_order.map((p: any, j: number) => (
                        <div key={j}>{j + 1}. {p.name} (month {p.month})</div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Budget Analysis */}
        {budget?.breakdown && (
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-slate-900 mb-3">Budget Analysis (50/30/20)</h2>
            <div className="bg-white rounded-2xl p-5 border border-slate-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <BudgetBar label="Needs (50%)" actual={budget.breakdown.needs.actual} target={budget.breakdown.needs.target} color="blue" />
                <BudgetBar label="Wants (30%)" actual={budget.breakdown.wants.actual} target={budget.breakdown.wants.target} color="purple" />
                <BudgetBar label="Savings (20%)" actual={budget.breakdown.savings.actual} target={budget.breakdown.savings.target} color="green" />
              </div>
              {budget.expense_details && (
                <div className="mt-4 border-t border-slate-100 pt-4">
                  <div className="text-sm font-medium text-slate-700 mb-2">Expense Breakdown</div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
                    {Object.entries(budget.expense_details).map(([cat, amount]: [string, any]) => (
                      <div key={cat} className="text-xs bg-slate-50 rounded-lg p-2">
                        <div className="text-slate-500">{cat}</div>
                        <div className="font-medium">{formatINR(amount)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Risk Flags & Positive Factors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <section className="bg-white rounded-2xl p-5 border border-slate-200">
            <h2 className="text-base font-semibold text-red-700 mb-2">Risk Flags</h2>
            <ul className="space-y-1">
              {overview.risk_flags.map((f, i) => (
                <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                  <span className="text-red-400 mt-0.5">*</span> {f}
                </li>
              ))}
            </ul>
          </section>
          <section className="bg-white rounded-2xl p-5 border border-slate-200">
            <h2 className="text-base font-semibold text-green-700 mb-2">Positive Factors</h2>
            <ul className="space-y-1">
              {overview.positive_factors.map((f, i) => (
                <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">+</span> {f}
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, sub, color }: { label: string; value: string; sub: string; color: string }) {
  const colorMap: Record<string, string> = {
    red: 'text-red-600',
    green: 'text-green-600',
    amber: 'text-amber-600',
    blue: 'text-blue-600',
  }
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200">
      <div className="text-xs text-slate-500 uppercase tracking-wide mb-1">{label}</div>
      <div className={`text-xl font-bold ${colorMap[color] || 'text-slate-900'}`}>{value}</div>
      <div className="text-xs text-slate-400 mt-1">{sub}</div>
    </div>
  )
}

function BudgetBar({ label, actual, target, color }: { label: string; actual: number; target: number; color: string }) {
  const pct = target > 0 ? Math.min((actual / target) * 100, 150) : 0
  const over = actual > target
  const colorMap: Record<string, string> = {
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    green: 'bg-green-500',
  }
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium text-slate-700">{label}</span>
        <span className={over ? 'text-red-500 font-medium' : 'text-slate-500'}>
          {formatINR(actual)} / {formatINR(target)}
        </span>
      </div>
      <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${over ? 'bg-red-400' : colorMap[color]}`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
    </div>
  )
}
