import type { CreditUtilization as CUType } from '../../services/types'
import { formatInr, numOr } from '../../utils/formatInr'
import SectionCard from './SectionCard'

interface Props {
  data: CUType
}

const statusColors: Record<string, { bar: string; text: string; bg: string }> = {
  High: { bar: 'bg-red-500', text: 'text-red-600', bg: 'bg-red-50' },
  Medium: { bar: 'bg-orange-400', text: 'text-orange-600', bg: 'bg-orange-50' },
  Low: { bar: 'bg-green-500', text: 'text-green-600', bg: 'bg-green-50' },
}

export default function CreditUtilization({ data }: Props) {
  const cfg = statusColors[data.status] ?? { bar: 'bg-slate-400', text: 'text-slate-600', bg: 'bg-slate-50' }

  return (
    <SectionCard title="Credit Utilization">
      <div className="space-y-5">
        <div className="flex items-center gap-4 flex-wrap">
          <div className={`px-3 py-1.5 ${cfg.bg} rounded-lg`}>
            <p className="text-xs text-slate-500">Used</p>
            <p className={`text-lg font-bold ${cfg.text}`}>{formatInr(data.used_limit)}</p>
          </div>
          <div className="text-slate-300 text-2xl font-light">/</div>
          <div className="px-3 py-1.5 bg-slate-50 rounded-lg">
            <p className="text-xs text-slate-500">Total Limit</p>
            <p className="text-lg font-bold text-slate-800">{formatInr(data.total_limit)}</p>
          </div>
          <span className={`ml-auto text-sm font-semibold px-3 py-1 rounded-full ${cfg.bg} ${cfg.text}`}>
            {data.status} ({numOr(data.utilization_percent)}%)
          </span>
        </div>

        <div>
          <div className="flex justify-between text-xs text-slate-500 mb-1">
            <span>0%</span>
            <span className={`font-semibold ${cfg.text}`}>{numOr(data.utilization_percent)}% used</span>
            <span>100%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-4 overflow-hidden">
            <div
              className={`${cfg.bar} h-4 rounded-full transition-all duration-700 flex items-center justify-end pr-2`}
              style={{ width: `${Math.min(numOr(data.utilization_percent), 100)}%` }}
            >
              {numOr(data.utilization_percent) > 15 && (
                <span className="text-white text-xs font-bold">{numOr(data.utilization_percent)}%</span>
              )}
            </div>
          </div>
        </div>

        <p className="text-xs text-slate-500 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">
          <strong className="text-amber-700">Tip:</strong> Aim to keep credit utilization below 30% to positively impact your score.
        </p>
      </div>
    </SectionCard>
  )
}
