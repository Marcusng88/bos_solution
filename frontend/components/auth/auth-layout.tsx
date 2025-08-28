import type React from "react"
import Link from "next/link"
import { Brain, Users, BarChart3, Clock, Target, Globe, TrendingUp, Zap, Mail, Shield, Lightbulb, ArrowUpRight } from "lucide-react"

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
    <div className="min-h-screen flex justify-center items-center bg-gradient-to-br from-yellow-50 to-amber-100 dark:from-yellow-900 dark:to-amber-800 relative overflow-hidden">
      {/* Notebook lines background */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            repeating-linear-gradient(
              0deg,
              transparent,
              transparent 29px,
              #000 29px,
              #000 30px
            )
          `,
          backgroundSize: '100% 30px'
        }}
      />
      
      {/* Floating Background Components */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Original 10 Components - Made Bigger */}
        {/* Floating Users Icon */}
        <div className="absolute top-20 left-10 animate-float-slow opacity-30">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Users className="h-16 w-16 text-blue-600" />
          </div>
        </div>
        
        {/* Floating Bar Chart */}
        <div className="absolute top-32 right-16 animate-float-medium opacity-25">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <BarChart3 className="h-16 w-16 text-green-600" />
          </div>
        </div>
        
        {/* Floating Clock */}
        <div className="absolute bottom-32 left-20 animate-float-slow opacity-30">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Clock className="h-16 w-16 text-purple-600" />
          </div>
        </div>
        
        {/* Floating Target */}
        <div className="absolute bottom-20 right-24 animate-float-medium opacity-25">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Target className="h-16 w-16 text-red-600" />
          </div>
        </div>
        
        {/* Floating Globe */}
        <div className="absolute top-1/2 left-8 animate-float-slow opacity-20">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Globe className="h-16 w-16 text-indigo-600" />
          </div>
        </div>
        
        {/* Floating Trending Up */}
        <div className="absolute top-1/3 right-8 animate-float-medium opacity-30">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <TrendingUp className="h-16 w-16 text-emerald-600" />
          </div>
        </div>
        
        {/* Floating Zap */}
        <div className="absolute bottom-1/3 left-1/4 animate-float-slow opacity-25">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Zap className="h-16 w-16 text-yellow-600" />
          </div>
        </div>
        
        {/* Floating Mail */}
        <div className="absolute top-1/4 right-1/3 animate-float-medium opacity-20">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Mail className="h-16 w-16 text-pink-600" />
          </div>
        </div>
        
        {/* Floating Shield */}
        <div className="absolute bottom-1/4 right-1/3 animate-float-slow opacity-30">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Shield className="h-16 w-16 text-cyan-600" />
          </div>
        </div>
        
        {/* Floating Lightbulb */}
        <div className="absolute top-2/3 left-1/3 animate-float-medium opacity-25">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Lightbulb className="h-16 w-16 text-orange-600" />
          </div>
        </div>
        
        {/* Floating Arrow Up Right */}
        <div className="absolute top-16 left-1/2 animate-float-slow opacity-20">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <ArrowUpRight className="h-16 w-16 text-teal-600" />
          </div>
        </div>

        {/* Duplicate 10 Components - Different Colors & Positions */}
        {/* Duplicate Users Icon */}
        <div className="absolute top-40 left-1/4 animate-float-fast opacity-25">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Users className="h-16 w-16 text-rose-600" />
          </div>
        </div>
        
        {/* Duplicate Bar Chart */}
        <div className="absolute top-48 right-1/3 animate-float-slow opacity-30">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <BarChart3 className="h-16 w-16 text-violet-600" />
          </div>
        </div>
        
        {/* Duplicate Clock */}
        <div className="absolute bottom-40 left-1/3 animate-float-fast opacity-25">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Clock className="h-16 w-16 text-lime-600" />
          </div>
        </div>
        
        {/* Duplicate Target */}
        <div className="absolute bottom-48 right-1/4 animate-float-medium opacity-20">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Target className="h-16 w-16 text-sky-600" />
          </div>
        </div>
        
        {/* Duplicate Globe */}
        <div className="absolute top-1/3 left-1/2 animate-float-slow opacity-30">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Globe className="h-16 w-16 text-fuchsia-600" />
          </div>
        </div>
        
        {/* Duplicate Trending Up */}
        <div className="absolute top-2/3 right-1/4 animate-float-fast opacity-25">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <TrendingUp className="h-16 w-16 text-amber-600" />
          </div>
        </div>
        
        {/* Duplicate Zap */}
        <div className="absolute bottom-1/3 right-1/2 animate-float-medium opacity-20">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Zap className="h-16 w-16 text-emerald-600" />
          </div>
        </div>
        
        {/* Duplicate Mail */}
        <div className="absolute top-1/2 right-1/6 animate-float-slow opacity-30">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Mail className="h-16 w-16 text-blue-500" />
          </div>
        </div>
        
        {/* Duplicate Shield */}
        <div className="absolute bottom-1/2 left-1/6 animate-float-fast opacity-25">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Shield className="h-16 w-16 text-green-500" />
          </div>
        </div>
        
        {/* Duplicate Lightbulb */}
        <div className="absolute top-1/6 left-1/3 animate-float-medium opacity-20">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <Lightbulb className="h-16 w-16 text-purple-500" />
          </div>
        </div>
        
        {/* Duplicate Arrow Up Right */}
        <div className="absolute bottom-1/6 right-1/3 animate-float-slow opacity-30">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-full">
            <ArrowUpRight className="h-16 w-16 text-orange-500" />
          </div>
        </div>
      </div>
      

      <div className="w-full max-w-md mx-auto px-6 py-12 relative z-10">
        {/* Mobile branding */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Brain className="h-6 w-6 text-white" />
          </div>
          <span className="text-xl font-bold">Bos Solution</span>
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
  )
}
