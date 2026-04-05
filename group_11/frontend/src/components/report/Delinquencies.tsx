import type { Delinquency } from '../../services/types'
import { formatInr } from '../../utils/formatInr'
import SectionCard from './SectionCard'

interface Props {
  delinquencies: Delinquency[]
}

const impactColors: Record<string, string> = {
  High: 'bg-red-100 text-red-700',
  Medium: 'bg-orange-100 text-orange-700',
  Low: 'bg-yellow-100 text-yellow-700',
}

export default function Delinquencies({ delinquencies }: Props) {
  return (
    <SectionCard
      title="Delinquencies"
      badge={
        <span className="text-xs bg-red-50 text-red-700 px-2 py-1 rounded-full font-medium">
          {delinquencies.length} found
        </span>
      }
    >
      {delinquencies.length === 0 ? (
        <p className="text-sm text-slate-500">No delinquencies found.</p>
      ) : (
        <div className="space-y-3">
          {delinquencies.map((d, i) => (
            <div key={i} className="flex items-start justify-between bg-red-50/60 border border-red-100 rounded-xl px-4 py-3 gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-slate-900">{d.type}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${impactColors[d.impact] ?? 'bg-slate-100 text-slate-600'}`}>
                    {d.impact} Impact
                  </span>
                </div>
                <p className="text-xs text-slate-500">Account: {d.account_id}</p>
                {d.days_past_due != null && (
                  <p className="text-xs text-slate-500">Days Past Due: <span className="text-red-600 font-semibold">{d.days_past_due}</span></p>
                )}
              </div>
              {d.amount != null && (
                <p className="text-sm font-bold text-red-600 whitespace-nowrap">{formatInr(d.amount)}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </SectionCard>
  )
}
