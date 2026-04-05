import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import ScoreSummary from '../components/report/ScoreSummary'
import PersonalInfo from '../components/report/PersonalInfo'
import AccountsTable from '../components/report/AccountsTable'
import Delinquencies from '../components/report/Delinquencies'
import Enquiries from '../components/report/Enquiries'
import Disputes from '../components/report/Disputes'
import CreditUtilization from '../components/report/CreditUtilization'
import PaymentSummary from '../components/report/PaymentSummary'
import RiskFlags from '../components/report/RiskFlags'
import { getSampleReport } from '../services/api'
import type { CreditReport } from '../services/types'

export default function SampleReport() {
  const { id } = useParams<{ id: string }>()
  const reportId = id?.trim() || 'sample'
  const [report, setReport] = useState<CreditReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getSampleReport()
      .then(setReport)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Failed to load report')
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="pt-24 pb-16 px-4 sm:px-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-slate-400">
            <Link to="/" className="hover:text-brand-600 transition-colors">Home</Link>
            <span>/</span>
            <span className="text-slate-600 font-medium">Credit Report</span>
            <span>/</span>
            <span className="text-slate-400">{reportId}</span>
          </nav>

          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-slate-900">Credit Report</h1>
            <span className="text-xs bg-amber-50 text-amber-700 border border-amber-100 px-3 py-1.5 rounded-full font-medium">
              Sample Report
            </span>
          </div>

          {loading && <LoadingSkeleton />}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
              <svg className="w-10 h-10 text-red-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-red-700 font-semibold mb-1">Unable to load report</p>
              <p className="text-red-500 text-sm">{error}</p>
              <p className="text-slate-400 text-xs mt-3">
                In dev, run FastAPI on port 8001 (or set{' '}
                <code className="bg-slate-100 px-1 rounded">VITE_DEV_PROXY_TARGET</code>) — Vite proxies{' '}
                <code className="bg-slate-100 px-1 rounded">/api</code>.
              </p>
            </div>
          )}

          {report && !loading && (
            <>
              <ScoreSummary data={report.report_summary} />
              <PersonalInfo data={report.personal_information} />
              <AccountsTable accounts={report.accounts} />
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <CreditUtilization data={report.credit_utilization} />
                <PaymentSummary data={report.payment_summary} />
              </div>
              <Delinquencies delinquencies={report.delinquencies} />
              <Enquiries enquiries={report.enquiries} />
              <Disputes disputes={report.disputes} />
              <RiskFlags riskFlags={report.risk_flags} positiveFactors={report.positive_factors} />
            </>
          )}
        </div>
      </main>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {[200, 160, 240, 180].map((h, i) => (
        <div key={i} className="bg-white rounded-2xl border border-slate-100" style={{ height: h }}>
          <div className="h-12 bg-slate-100 rounded-t-2xl" />
          <div className="p-6 space-y-3">
            <div className="h-4 bg-slate-100 rounded w-3/4" />
            <div className="h-4 bg-slate-100 rounded w-1/2" />
          </div>
        </div>
      ))}
    </div>
  )
}
