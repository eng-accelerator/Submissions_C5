import { Link } from 'react-router-dom'
import CreditImprovementIllustration from '../components/CreditImprovementIllustration'
import Navbar from '../components/Navbar'

const features = [
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    title: 'Real-time Score Analysis',
    description: 'Get a detailed breakdown of every factor impacting your credit score.',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
    title: 'AI-Powered Insights',
    description: 'Personalised recommendations to help you build a stronger credit profile.',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
    title: 'Secure & Private',
    description: 'Bank-grade encryption. Your data never leaves our secure infrastructure.',
  },
]

const quickLinks = [
  {
    to: '/upload',
    title: 'Upload Docs',
    subtitle: 'PDF, CSV, JSON',
    bg: 'bg-purple-50',
    iconColor: 'text-purple-600',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
    ),
  },
  {
    to: '/plan',
    title: 'My Plan',
    subtitle: 'Financial plan',
    bg: 'bg-blue-50',
    iconColor: 'text-blue-600',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    to: '/chat',
    title: 'AI Coach',
    subtitle: 'Chat with agents',
    bg: 'bg-green-50',
    iconColor: 'text-green-600',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
    ),
  },
  {
    to: '/admin',
    title: 'Tips',
    subtitle: 'AI-generated tips',
    bg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
  },
  {
    to: '/showcase',
    title: 'AI Showcase',
    subtitle: 'All AI features',
    bg: 'bg-indigo-50',
    iconColor: 'text-indigo-600',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
]

const steps = [
  { step: '01', title: 'Upload Your Documents', description: 'Upload credit reports, bank statements, salary slips, or photos of financial documents.' },
  { step: '02', title: 'AI Analyzes Your Data', description: 'Our AI agents extract data, build your financial profile, and generate insights.' },
  { step: '03', title: 'Get Personalized Advice', description: 'Chat with specialist agents for debt analysis, budgeting, savings plans, and payoff strategies.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      {/* Hero */}
      <section className="relative overflow-hidden pt-32 pb-24 px-4 sm:px-6">
        {/* Background gradient blobs */}
        <div className="absolute -top-40 -right-40 w-[600px] h-[600px] bg-brand-100 rounded-full opacity-40 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -left-40 w-[500px] h-[500px] bg-indigo-100 rounded-full opacity-30 blur-3xl pointer-events-none" />

        <div className="relative max-w-4xl mx-auto text-center">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 text-brand-700 text-sm font-medium mb-6 border border-brand-100">
            <span className="w-2 h-2 bg-brand-500 rounded-full animate-pulse" />
            AI-powered credit intelligence
          </span>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-slate-900 leading-tight tracking-tight mb-6">
            Your credit dreams{' '}
            <span className="text-brand-600">will fulfil here</span>
          </h1>

          <p className="text-xl text-slate-500 max-w-2xl mx-auto mb-10 leading-relaxed">
            Understand your credit score, dispute errors, and get a personalised AI roadmap
            to the score you deserve — all in one place.
          </p>
          <CreditImprovementIllustration />
        </div>
      </section>

      {/* Quick Menu */}
      <section className="py-2 px-4 sm:px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-slate-900 text-center mb-2">Explore Features</h2>
          <p className="text-slate-500 text-center mb-8">Jump into any feature to see it in action</p>
          <div className="flex flex-wrap justify-center gap-4">
            {quickLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="group flex flex-col items-center gap-3 p-5 w-40 bg-white rounded-2xl border border-slate-200 hover:border-brand-300 hover:shadow-lg hover:shadow-brand-100/50 transition-all duration-200"
              >
                <div className={`w-12 h-12 ${link.bg} ${link.iconColor} rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform`}>
                  {link.icon}
                </div>
                <div className="text-center">
                  <div className="text-sm font-semibold text-slate-900">{link.title}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{link.subtitle}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-4 px-4 sm:px-6 bg-slate-50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-slate-900 text-center mb-12">
            Everything you need to take control
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((f) => (
              <div key={f.title} className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-brand-50 text-brand-600 rounded-xl flex items-center justify-center mb-4">
                  {f.icon}
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{f.title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-10 px-4 sm:px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-slate-900 text-center mb-12">How it works</h2>
          <div className="space-y-6">
            {steps.map((s, i) => (
              <div key={s.step} className="flex items-start gap-6 group">
                <div className="flex-shrink-0 w-14 h-14 bg-brand-600 text-white rounded-2xl flex items-center justify-center text-lg font-bold shadow-sm">
                  {s.step}
                </div>
                <div className={`flex-1 pb-6 ${i < steps.length - 1 ? 'border-b border-slate-100' : ''}`}>
                  <h3 className="text-lg font-semibold text-slate-900 mb-1">{s.title}</h3>
                  <p className="text-slate-500">{s.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 sm:px-6 bg-brand-600">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to improve your score?</h2>
          <p className="text-brand-200 mb-8 text-lg">
            Join thousands of users who have already started their credit journey with DemoAI.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 sm:px-6 border-t border-slate-100">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="text-sm text-slate-400">© 2026 DemoAI. All rights reserved.</span>
        </div>
      </footer>
    </div>
  )
}

