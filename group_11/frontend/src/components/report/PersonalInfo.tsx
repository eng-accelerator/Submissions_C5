import type { PersonalInformation } from '../../services/types'
import SectionCard from './SectionCard'

interface Props {
  data: PersonalInformation
}

export default function PersonalInfo({ data }: Props) {
  return (
    <SectionCard title="Personal Information">
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <InfoRow label="Full Name" value={data.name} />
          <InfoRow label="Date of Birth" value={data.dob} />
          <InfoRow label="PAN" value={data.pan} />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-slate-500 font-medium mb-2">Email Addresses</p>
            <ul className="space-y-1">
              {data.emails.map((email) => (
                <li key={email} className="text-sm text-slate-700 bg-slate-50 rounded-lg px-3 py-2">
                  {email}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium mb-2">Phone Numbers</p>
            <ul className="space-y-1">
              {data.phone_numbers.map((phone) => (
                <li key={phone} className="text-sm text-slate-700 bg-slate-50 rounded-lg px-3 py-2">
                  {phone}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div>
          <p className="text-xs text-slate-500 font-medium mb-2">Addresses</p>
          <div className="space-y-2">
            {data.addresses.map((addr, i) => (
              <div key={i} className="flex items-start justify-between bg-slate-50 rounded-xl px-4 py-3 gap-4">
                <div>
                  <p className="text-sm font-medium text-slate-800">{addr.address}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{addr.type}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium whitespace-nowrap ${addr.status === 'Current' ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                  {addr.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {data.issues.length > 0 && (
          <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
            <p className="text-xs font-semibold text-amber-700 mb-2 uppercase tracking-wide">Alerts</p>
            <ul className="space-y-1">
              {data.issues.map((issue) => (
                <li key={issue} className="flex items-center gap-2 text-sm text-amber-800">
                  <svg className="w-4 h-4 text-amber-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {issue}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </SectionCard>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-50 rounded-xl px-4 py-3">
      <p className="text-xs text-slate-500 font-medium mb-1">{label}</p>
      <p className="text-sm font-semibold text-slate-800">{value}</p>
    </div>
  )
}
