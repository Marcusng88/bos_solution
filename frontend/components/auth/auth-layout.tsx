import type React from "react"
import Link from "next/link"
import { Brain, Sparkles } from "lucide-react"
import { ThemeToggle } from "@/components/theme-toggle"

interface AuthLayoutProps {
  children: React.ReactNode
  title: string
  subtitle: string
  footerText: string
  footerLinkText: string
  footerLinkHref: string
}

export function AuthLayout({ children, title, subtitle, footerText, footerLinkText, footerLinkHref }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-blue-800 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10" />
        <div className="relative z-10 flex flex-col justify-center px-12 text-white">
          <div className="flex items-center gap-3 mb-8">
            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
              <Brain className="h-8 w-8" />
            </div>
            <h1 className="text-3xl font-bold">MarketingAI Pro</h1>
          </div>
          <h2 className="text-4xl font-bold mb-6 leading-tight">Transform your marketing with AI-powered insights</h2>
          <p className="text-xl text-blue-100 mb-8 leading-relaxed">
            Create compelling content, optimize campaigns, and drive results with our intelligent marketing platform.
          </p>
          <div className="flex items-center gap-4 text-blue-100">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              <span>AI Content Generation</span>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              <span>Smart Analytics</span>
            </div>
          </div>
        </div>
        {/* Decorative elements */}
        <div className="absolute top-20 right-20 w-32 h-32 bg-white/10 rounded-full blur-xl" />
        <div className="absolute bottom-20 left-20 w-24 h-24 bg-white/10 rounded-full blur-xl" />
      </div>

      {/* Right side - Form */}
      <div className="flex-1 flex flex-col justify-center px-6 py-12 lg:px-12">
        <div className="absolute top-6 right-6">
          <ThemeToggle />
        </div>

        <div className="mx-auto w-full max-w-sm">
          {/* Mobile branding */}
          <div className="flex items-center justify-center gap-2 mb-8 lg:hidden">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold">MarketingAI Pro</span>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-foreground mb-2">{title}</h2>
            <p className="text-muted-foreground">{subtitle}</p>
          </div>

          {children}

          <p className="text-center text-sm text-muted-foreground mt-6">
            {footerText}{" "}
            <Link href={footerLinkHref} className="font-medium text-blue-600 hover:text-blue-500 transition-colors">
              {footerLinkText}
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
