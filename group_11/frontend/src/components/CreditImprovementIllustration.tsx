import { useEffect, useState } from 'react'

const SEGMENT_COLORS = ['#d1fae5', '#6ee7b7', '#34d399', '#059669', '#065f46']

function polar(cx: number, cy: number, r: number, deg: number) {
  const rad = (deg * Math.PI) / 180
  return { x: cx + r * Math.cos(rad), y: cy - r * Math.sin(rad) }
}

function arcPath(
  cx: number,
  cy: number,
  rInner: number,
  rOuter: number,
  degStart: number,
  degEnd: number,
) {
  const o1 = polar(cx, cy, rOuter, degStart)
  const o2 = polar(cx, cy, rOuter, degEnd)
  const i2 = polar(cx, cy, rInner, degEnd)
  const i1 = polar(cx, cy, rInner, degStart)
  const large = Math.abs(degEnd - degStart) > 180 ? 1 : 0
  return [
    `M ${o1.x} ${o1.y}`,
    `A ${rOuter} ${rOuter} 0 ${large} 0 ${o2.x} ${o2.y}`,
    `L ${i2.x} ${i2.y}`,
    `A ${rInner} ${rInner} 0 ${large} 1 ${i1.x} ${i1.y}`,
    'Z',
  ].join(' ')
}

/**
 * Hero visual: semi-circular credit gauge (poor → excellent greens), needle animating
 * toward the excellent band, checklist + coins — suggests upward credit trajectory.
 */
export default function CreditImprovementIllustration() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true))
    return () => cancelAnimationFrame(id)
  }, [])

  const cx = 160
  // Pivot slightly higher so stroke + hub stay comfortably inside the viewBox / card
  const cy = 162
  const rOuter = 118
  const rInner = 72
  const steps = 5
  const degPer = 180 / steps
  const needleLen = rOuter - 10

  // Needle pivots at center; line points up (−Y). Rotate CW in SVG = positive deg.
  // Start toward left/poor arc (~−115°), end toward right/excellent arc (~+72°).
  const needleStartDeg = -115
  const needleEndDeg = 72

  return (
    <div className="mt-16 mx-auto max-w-2xl bg-white rounded-2xl shadow-xl border border-slate-100 px-4 py-8 sm:px-8 sm:py-10">
      <p className="text-center text-sm font-medium text-slate-500 mb-2">Your journey upward</p>
      <p className="text-center text-lg font-semibold text-slate-800 mb-6">
        From where you are today → to the score you deserve
      </p>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-4 pb-2">
        {/* Checklist — steps completed on the path to better credit */}
        <div className="flex flex-col gap-3 sm:w-[140px] order-2 sm:order-1">
          {['Fix report errors', 'Lower utilisation', 'On-time payments'].map((label) => (
            <div key={label} className="flex items-start gap-2.5 text-left">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border-2 border-slate-800 bg-emerald-50">
                <svg className="h-3 w-3 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </span>
              <div className="min-w-0 pt-0.5">
                <p className="text-xs font-medium text-slate-700 leading-snug">{label}</p>
                <span className="mt-1 block h-1.5 max-w-[72px] rounded-full bg-slate-200" />
              </div>
            </div>
          ))}
        </div>

        {/* Gauge — viewBox includes stroke, shadow, labels; overflow hidden keeps art inside card */}
        <div className="relative order-1 sm:order-2 w-[min(100%,280px)] shrink-0 overflow-hidden">
          <svg
            viewBox="0 0 320 228"
            className="block w-full h-auto overflow-hidden"
            preserveAspectRatio="xMidYMid meet"
            aria-hidden
          >
            <defs>
              <filter id="gaugeShadow" x="-15%" y="-15%" width="130%" height="135%">
                <feDropShadow dx="0" dy="1" stdDeviation="1.5" floodOpacity="0.08" />
              </filter>
            </defs>

            {/* Outer double-line frame */}
            <path
              d={arcPath(cx, cy, rInner - 6, rOuter + 8, 180, 0)}
              fill="none"
              stroke="#1e293b"
              strokeWidth={2.5}
              strokeLinejoin="round"
              opacity={0.35}
            />

            {Array.from({ length: steps }, (_, k) => {
              const start = 180 - k * degPer
              const end = 180 - (k + 1) * degPer
              return (
                <path
                  key={k}
                  d={arcPath(cx, cy, rInner, rOuter, start, end)}
                  fill={SEGMENT_COLORS[k]}
                  stroke="#0f172a"
                  strokeWidth={1.25}
                  strokeLinejoin="round"
                  filter="url(#gaugeShadow)"
                />
              )
            })}

            {/* Needle — nested g so rotation is around pivot after translate */}
            <g transform={`translate(${cx} ${cy})`}>
              <g
                style={{
                  transform: `rotate(${mounted ? needleEndDeg : needleStartDeg}deg)`,
                  transformOrigin: '0px 0px',
                  transition: 'transform 2.2s cubic-bezier(0.22, 1, 0.36, 1)',
                }}
              >
                <line
                  x1={0}
                  y1={0}
                  x2={0}
                  y2={-needleLen}
                  stroke="#0f172a"
                  strokeWidth={3}
                  strokeLinecap="round"
                />
                <circle r={9} fill="#0f172a" stroke="#fff" strokeWidth={2} />
              </g>
            </g>

            {/* Scale labels — kept inside viewBox bottom padding */}
            <text x={36} y={212} className="fill-slate-400 text-[10px] font-medium" textAnchor="start">
              Start
            </text>
            <text x={284} y={212} className="fill-emerald-800 text-[10px] font-semibold" textAnchor="end">
              Excellent
            </text>
          </svg>
        </div>

        {/* Coins — financial upside */}
        <div className="flex flex-col items-center gap-2 sm:w-[100px] order-3">
          <Coin className="h-14 w-14 -rotate-6" />
          <Coin className="h-11 w-11 rotate-6 -mt-2 opacity-95" />
          <p className="text-[11px] text-center text-slate-500 mt-1 max-w-[100px] leading-tight">
            Better credit, better opportunities
          </p>
        </div>
      </div>
    </div>
  )
}

function Coin({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 48 48" aria-hidden>
      <circle cx="24" cy="24" r="22" fill="#fbbf24" stroke="#b45309" strokeWidth={2} />
      <circle cx="24" cy="24" r="18" fill="#fcd34d" stroke="#d97706" strokeWidth={1} />
      <text
        x="24"
        y="30"
        textAnchor="middle"
        className="fill-amber-900 font-bold"
        style={{ fontSize: '18px', fontFamily: 'Inter, system-ui, sans-serif' }}
      >
        ₹
      </text>
    </svg>
  )
}
