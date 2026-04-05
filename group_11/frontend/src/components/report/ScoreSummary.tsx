import type { ReportSummary } from '../../services/types'
import ScoreGauge from '../ScoreGauge'
import SectionCard from './SectionCard'

interface Props {
  data: ReportSummary
}

export default function ScoreSummary({ data }: Props) {
  return (
    <SectionCard title="Credit Score Summary">
      <div className="flex flex-col lg:flex-row items-center gap-8">
        <ScoreGauge score={data.score} band={data.score_band} />
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 flex-1 w-full">
          <StatTile label="Report Date" value={data.report_date} />
          <StatTile label="Total Accounts" value={data.total_accounts} />
          <StatTile label="Active Accounts" value={data.active_accounts} />
          <StatTile label="Closed Accounts" value={data.closed_accounts} />
        </div>
      </div>
    </SectionCard>
  )
}

function StatTile({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-slate-50 rounded-xl p-4">
      <p className="text-xs text-slate-500 font-medium mb-1">{label}</p>
      <p className="text-xl font-bold text-slate-900">{value}</p>
    </div>
  )
}
