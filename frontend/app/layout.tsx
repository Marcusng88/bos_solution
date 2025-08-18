import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { ThemeProvider } from "@/components/theme-provider"
import { ClerkProviderWrapper } from "@/components/providers/clerk-provider"
import { Toaster } from "@/components/ui/toaster"
import { AIChatWidget } from "@/components/ai-chat-widget"
import "./globals.css"

export const metadata: Metadata = {
  title: "MarketingAI Pro",
  description: "AI-powered marketing and content strategy platform",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <style>{`
html {
  font-family: ${GeistSans.style.fontFamily};
  --font-sans: ${GeistSans.variable};
  --font-mono: ${GeistMono.variable};
}
        `}</style>
      </head>
      <body suppressHydrationWarning>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          <ClerkProviderWrapper>
            {children}
            <AIChatWidget />
            <Toaster />
          </ClerkProviderWrapper>
        </ThemeProvider>
      </body>
    </html>
  )
}
