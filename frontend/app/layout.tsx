import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'LIFE PAY ERP',
  description: 'Premium Enterprise ERP Dashboard'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  )
}
