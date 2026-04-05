import type { ReactNode } from 'react'

interface Props {
  title: string
  children: ReactNode
  badge?: ReactNode
}

export default function SectionCard({ title, children, badge }: Props) {
  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/60">
        <h2 className="text-base font-semibold text-slate-800">{title}</h2>
        {badge}
      </div>
      <div className="p-6">{children}</div>
    </div>
  )
}
