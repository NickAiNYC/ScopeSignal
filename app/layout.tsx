import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'COMMAND CENTER 2026',
  description: 'Unified Intelligence Platform - ViolationSentinel, Regula, AI-PulsePoint, and ScopeSignal',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-white antialiased">
        {children}
      </body>
    </html>
  )
}
