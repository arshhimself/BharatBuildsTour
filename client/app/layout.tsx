import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'BizMate — Run your business. Not the busywork.',
  description: 'Your AI team for sales, operations, finance and growth — working quietly behind the conversations you already have.',
  metadataBase: new URL('https://bizmate.app'),
  openGraph: {
    title: 'BizMate — Run your business. Not the busywork.',
    description: 'Your AI team for sales, operations, finance and growth — working quietly behind the conversations you already have.',
    images: [
      {
        url: '/bizmate-og-cover.png',
        width: 1672,
        height: 941,
        alt: 'BizMate — Your AI Business Partner',
      },
    ],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'BizMate — Run your business. Not the busywork.',
    description: 'Your AI team for sales, operations, finance and growth — working quietly behind the conversations you already have.',
    images: ['/bizmate-og-cover.png'],
  },
  icons: {
    icon: '/bizmate-logo-icon.png',
    apple: '/bizmate-logo-icon.png',
  },
}

export const viewport: Viewport = {
  colorScheme: 'light dark',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
