import type { Enquiry } from '../../services/types'
import { formatInr } from '../../utils/formatInr'
import SectionCard from './SectionCard'

interface Props {
  enquiries: Enquiry[]
}

export default function Enquiries({ enquiries }: Props) {
  return (
    <SectionCard
      title="Recent Enquiries"
      badge={
        <span className="text-xs bg-amber-50 text-amber-700 px-2 py-1 rounded-full font-medium">
          {enquiries.length} enquiries
        </span>
      }
    >
      {enquiries.length === 0 ? (
        <p className="text-sm text-slate-500">No recent enquiries.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left text-xs font-semibold text-slate-500 pb-2 pr-4">Lender</th>
                <th className="text-left text-xs font-semibold text-slate-500 pb-2 pr-4">Type</th>
                <th className="text-left text-xs font-semibold text-slate-500 pb-2 pr-4">Amount</th>
                <th className="text-left text-xs font-semibold text-slate-500 pb-2">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {enquiries.map((e, i) => (
                <tr key={i}>
                  <td className="py-3 pr-4 font-medium text-slate-800">{e.lender}</td>
                  <td className="py-3 pr-4 text-slate-600">{e.type}</td>
                  <td className="py-3 pr-4 text-slate-700 font-semibold">{formatInr(e.amount)}</td>
                  <td className="py-3 text-slate-500">{e.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </SectionCard>
  )
}
