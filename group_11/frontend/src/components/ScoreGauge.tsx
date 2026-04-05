interface ScoreGaugeProps {
  score: number
  band: string
  size?: 'sm' | 'md'
}

const SCORE_MIN = 300
const SCORE_MAX = 900

const bandConfig: Record<string, { color: string; bg: string; bar: string }> = {
  Poor: { color: 'text-red-600', bg: 'bg-red-50', bar: 'bg-red-500' },
  Fair: { color: 'text-orange-600', bg: 'bg-orange-50', bar: 'bg-orange-400' },
  Good: { color: 'text-yellow-600', bg: 'bg-yellow-50', bar: 'bg-yellow-400' },
  'Very Good': { color: 'text-green-600', bg: 'bg-green-50', bar: 'bg-green-500' },
  Excellent: { color: 'text-emerald-600', bg: 'bg-emerald-50', bar: 'bg-emerald-500' },
}

function getBandConfig(band: string) {
  return bandConfig[band] ?? { color: 'text-slate-600', bg: 'bg-slate-50', bar: 'bg-slate-400' }
}

export default function ScoreGauge({ score, band, size = 'md' }: ScoreGaugeProps) {
  const percent = ((score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN)) * 100
  const cfg = getBandConfig(band)
  const isSmall = size === 'sm'

  return (
    <div className="flex flex-col items-center gap-4">
      <div className={`${isSmall ? 'w-24 h-24' : 'w-36 h-36'} rounded-full ${cfg.bg} flex flex-col items-center justify-center border-4 ${cfg.bar.replace('bg-', 'border-')}`}>
        <span className={`${isSmall ? 'text-2xl' : 'text-4xl'} font-black ${cfg.color}`}>{score}</span>
        <span className="text-xs text-slate-500 mt-1">out of {SCORE_MAX}</span>
      </div>
      <div className="w-full max-w-xs">
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>{SCORE_MIN}</span>
          <span className={`font-semibold ${cfg.color}`}>{band}</span>
          <span>{SCORE_MAX}</span>
        </div>
        <div className="w-full bg-slate-100 rounded-full h-3">
          <div
            className={`${cfg.bar} h-3 rounded-full transition-all duration-700`}
            style={{ width: `${percent}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-slate-300 mt-1">
          <span>Poor</span>
          <span>Fair</span>
          <span>Good</span>
          <span>Very Good</span>
          <span>Excellent</span>
        </div>
      </div>
    </div>
  )
}
