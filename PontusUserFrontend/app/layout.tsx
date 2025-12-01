import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
})

export const metadata: Metadata = {
  title: "Pontus - Multi-Rail Payment Routing & Execution",
  description: "AI-powered multi-rail payment routing, treasury automation, and global payout OS",
  icons: {
    icon: [
      { url: "/PontusIcon.png", type: "image/png" },
    ],
    apple: [
      { url: "/PontusIcon.png", type: "image/png" },
    ],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">{children}</body>
    </html>
  )
}

