import SectionCard from './SectionCard'

interface Props {
  riskFlags: string[]
  positiveFactors: string[]
}

export default function RiskFlags({ riskFlags, positiveFactors }: Props) {
  return (
    <SectionCard title="Risk Flags & Positive Factors">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p className="text-xs font-semibold text-red-600 uppercase tracking-wide mb-3 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            Risk Flags
          </p>
          <ul className="space-y-2">
            {riskFlags.map((flag) => (
              <li key={flag} className="flex items-start gap-2 bg-red-50 border border-red-100 rounded-lg px-3 py-2 text-sm text-red-800">
                <svg className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                {flag}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs font-semibold text-green-600 uppercase tracking-wide mb-3 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Positive Factors
          </p>
          <ul className="space-y-2">
            {positiveFactors.map((factor) => (
              <li key={factor} className="flex items-start gap-2 bg-green-50 border border-green-100 rounded-lg px-3 py-2 text-sm text-green-800">
                <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                {factor}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </SectionCard>
  )
}
