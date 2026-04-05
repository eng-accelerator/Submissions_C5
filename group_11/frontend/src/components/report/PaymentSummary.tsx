import type { PaymentSummary as PSType } from '../../services/types'
import { numOr } from '../../utils/formatInr'
import SectionCard from './SectionCard'

interface Props {
  data: PSType
}

export default function PaymentSummary({ data }: Props) {
  const onTime = numOr(data.on_time_payments)
  const late = numOr(data.late_payments)
  const severe = numOr(data.severe_delinquencies)
  const total = onTime + late + severe
  const onTimePercent = total > 0 ? Math.round((onTime / total) * 100) : 0
  const onTimeW = total > 0 ? (onTime / total) * 100 : 0
  const lateW = total > 0 ? (late / total) * 100 : 0
  const severeW = total > 0 ? (severe / total) * 100 : 0

  return (
    <SectionCard title="Payment Summary">
      <div className="space-y-5">
        <div className="grid grid-cols-3 gap-4">
          <PaymentTile
            label="On Time"
            count={onTime}
            color="text-green-600"
            bg="bg-green-50"
            border="border-green-100"
          />
          <PaymentTile
            label="Late"
            count={late}
            color="text-orange-600"
            bg="bg-orange-50"
            border="border-orange-100"
          />
          <PaymentTile
            label="Severe"
            count={severe}
            color="text-red-600"
            bg="bg-red-50"
            border="border-red-100"
          />
        </div>

        <div>
          <div className="flex justify-between text-xs text-slate-500 mb-1">
            <span>On-time payment rate</span>
            <span className="font-semibold text-slate-700">{onTimePercent}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden flex">
            <div
              className="bg-green-500 h-3 transition-all duration-700"
              style={{ width: `${onTimeW}%` }}
            />
            <div
              className="bg-orange-400 h-3 transition-all duration-700"
              style={{ width: `${lateW}%` }}
            />
            <div
              className="bg-red-500 h-3 transition-all duration-700"
              style={{ width: `${severeW}%` }}
            />
          </div>
          <div className="flex gap-4 mt-2">
            <LegendDot color="bg-green-500" label="On Time" />
            <LegendDot color="bg-orange-400" label="Late" />
            <LegendDot color="bg-red-500" label="Severe" />
          </div>
        </div>
      </div>
    </SectionCard>
  )
}

function PaymentTile({
  label, count, color, bg, border,
}: {
  label: string; count: number; color: string; bg: string; border: string
}) {
  return (
    <div className={`${bg} ${border} border rounded-xl p-4 text-center`}>
      <p className={`text-3xl font-black ${color}`}>{count}</p>
      <p className="text-xs text-slate-500 mt-1">{label}</p>
    </div>
  )
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1">
      <span className={`w-3 h-3 rounded-full ${color}`} />
      <span className="text-xs text-slate-500">{label}</span>
    </div>
  )
}
