import type { Dispute } from '../../services/types'
import SectionCard from './SectionCard'

interface Props {
  disputes: Dispute[]
}

const statusColors: Record<string, string> = {
  'Under Review': 'bg-blue-50 text-blue-700',
  Resolved: 'bg-green-50 text-green-700',
  Rejected: 'bg-red-50 text-red-700',
}

export default function Disputes({ disputes }: Props) {
  return (
    <SectionCard
      title="Disputes"
      badge={
        <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-full font-medium">
          {disputes.length} open
        </span>
      }
    >
      {disputes.length === 0 ? (
        <p className="text-sm text-slate-500">No active disputes.</p>
      ) : (
        <div className="space-y-3">
          {disputes.map((d, i) => (
            <div key={i} className="bg-blue-50/50 border border-blue-100 rounded-xl px-4 py-3 space-y-2">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-slate-900">{d.field}</p>
                  <p className="text-xs text-slate-500">Account: {d.account_id}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium whitespace-nowrap ${statusColors[d.status] ?? 'bg-slate-100 text-slate-600'}`}>
                  {d.status}
                </span>
              </div>
              <p className="text-sm text-slate-600 italic">"{d.remark}"</p>
            </div>
          ))}
        </div>
      )}
    </SectionCard>
  )
}
