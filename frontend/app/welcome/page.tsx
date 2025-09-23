'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowRight, 
  Sparkles, 
  Target, 
  TrendingUp, 
  Zap, 
  Globe,
  Users,
  BarChart3,
  Lightbulb,
  Loader2,
  Calendar,
  Eye,
  Share2,
  Brain,
  Settings,
  ChevronRight,
  ChevronLeft,
  Search,
  DollarSign
} from 'lucide-react';
import { AuthGuard } from '@/components/auth/auth-guard';
import LiquidEther from '@/components/effects/LiquidEther';
import ShinyText from '@/components/effects/ShinyText';
import GradientText from '@/components/effects/GradientText';

export default function WelcomePage() {
  const router = useRouter();
  const { user } = useUser();
  const [isVisible, setIsVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [activeFeature, setActiveFeature] = useState<number | null>(null);
  const [isSliding, setIsSliding] = useState(false);

  useEffect(() => {
    // Always allow access to Welcome page
    setIsLoading(false);
    setIsVisible(true);
  }, []);

  const handleContinueToDashboard = () => {
    router.push('/dashboard');
  };

  const handleFeatureHover = (index: number) => {
    setActiveFeature(index);
    setIsSliding(true);
  };

  const handleFeatureLeave = () => {
    setActiveFeature(null);
    setIsSliding(false);
  };

  const featureNavigationItems = [
    {
      icon: <Calendar className="h-5 w-5" />,
      title: "Content Planning",
      description: "AI-powered content strategy and scheduling across all your social media platforms. Plan months ahead with intelligent recommendations.",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: <Eye className="h-5 w-5" />,
      title: "Continuous Monitoring",
      description: "Real-time tracking of your brand mentions, competitor activities, and market trends. Never miss an important conversation.",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: <Share2 className="h-5 w-5" />,
      title: "Multi-Platform Publishing",
      description: "Seamlessly publish and manage content across Facebook, Instagram, Twitter, LinkedIn, and YouTube from one unified dashboard.",
      color: "from-green-500 to-teal-500"
    },
    {
      icon: <Search className="h-5 w-5" />,
      title: "Competitor Intelligence",
      description: "Deep analysis of competitor strategies, content performance, and market positioning to give you a competitive edge.",
      color: "from-orange-500 to-red-500"
    },
    {
      icon: <DollarSign className="h-5 w-5" />,
      title: "ROI Dashboard",
      description: "Comprehensive analytics and financial insights to track your return on investment and optimize marketing spend.",
      color: "from-yellow-500 to-orange-500"
    },
    {
      icon: <Settings className="h-5 w-5" />,
      title: "Campaign Optimization",
      description: "Automated A/B testing, performance optimization, and intelligent budget allocation for maximum ROI.",
      color: "from-indigo-500 to-purple-500"
    }
  ];

  const features = [
    {
      icon: <Target className="h-6 w-6" />,
      title: "Smart Targeting",
      description: "AI-powered audience insights"
    },
    {
      icon: <TrendingUp className="h-6 w-6" />,
      title: "Growth Analytics",
      description: "Real-time performance tracking"
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: "Instant Optimization",
      description: "Automated campaign improvements"
    },
    {
      icon: <Globe className="h-6 w-6" />,
      title: "Global Reach",
      description: "Multi-platform content distribution"
    }
  ];

  if (isLoading) {
    return (
      <AuthGuard>
        <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-white" />
            <p className="text-white text-lg">Preparing your experience...</p>
          </div>
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-black relative overflow-hidden">
        {/* LiquidEther Background Effect */}
        <div className="absolute inset-0 z-0">
          <LiquidEther
            colors={['#5227FF', '#FF9FFC', '#B19EEF']}
            mouseForce={20}
            cursorSize={100}
            isViscous={false}
            viscous={30}
            iterationsViscous={32}
            iterationsPoisson={32}
            resolution={0.5}
            isBounce={false}
            autoDemo={true}
            autoSpeed={0.5}
            autoIntensity={2.2}
            takeoverDuration={0.25}
            autoResumeDelay={3000}
            autoRampDuration={0.6}
            style={{ width: '100%', height: '100%' }}
          />
        </div>

        {/* Dark overlay for better text readability */}
        <div className="absolute inset-0 z-10 bg-black/40 backdrop-blur-[0.5px]"></div>

        {/* Top Feature Navigation Bar */}
        <div className="fixed top-0 left-0 right-0 z-30 bg-black/20 backdrop-blur-md border-b border-white/10">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-center gap-20 py-4">
              {featureNavigationItems.map((item, index) => (
                <div
                  key={index}
                  className={`relative cursor-pointer transition-all duration-300 group ${
                    activeFeature === index ? 'text-white' : 'text-white/80 hover:text-white'
                  }`}
                  onMouseEnter={() => handleFeatureHover(index)}
                  onMouseLeave={handleFeatureLeave}
                >
                  <span className="font-medium text-sm tracking-wide">
                    {item.title}
                  </span>
                  
                  {/* Underline effect */}
                  <div className={`absolute bottom-0 left-0 h-0.5 bg-gradient-to-r ${item.color} transition-all duration-300 ${
                    activeFeature === index ? 'w-full opacity-100' : 'w-0 opacity-0 group-hover:w-full group-hover:opacity-100'
                  }`}></div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content Container with Sliding Animation */}
        <div className={`relative z-20 transition-transform duration-700 ease-in-out pt-16 ${isSliding ? '-translate-y-1/4' : 'translate-y-0'}`}>

          <div className="container mx-auto px-4 py-12">
            {/* Main Hero Section */}
            <div className={`text-center mb-16 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              <div className="mb-8">
                <Badge className="mb-6 px-4 py-2 text-sm bg-blue-500/30 text-blue-200 border-blue-400/50 backdrop-blur-sm">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Welcome to the Future of Marketing
                </Badge>
                
                <h1 className="text-7xl md:text-8xl lg:text-9xl font-black mb-6 leading-tight">
                  <div className="relative">
                    {/* Background glow effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent blur-sm opacity-70 scale-110">
                      BOSSOLUTION
                    </div>
                    {/* Main title with shiny effect */}
                    <ShinyText 
                      text="BOSSOLUTION" 
                      disabled={false} 
                      speed={3} 
                      className="relative z-10 bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent font-black"
                    />
                  </div>
                </h1>
                
                <div className="max-w-4xl mx-auto mb-8">
                  <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6 leading-relaxed drop-shadow-lg">
                    <GradientText
                      colors={["#40ffaa", "#4079ff", "#ff6b40", "#ff40aa", "#40ffaa"]}
                      animationSpeed={4}
                      showBorder={false}
                      className="text-3xl md:text-4xl lg:text-5xl font-bold"
                    >
                      Transform Your Business with AI-Powered Marketing Intelligence
                    </GradientText>
                  </h2>
                  
                  <div className="text-xl md:text-2xl leading-relaxed drop-shadow-md">
                    <GradientText
                      colors={["#60a5fa", "#a78bfa", "#34d399", "#fbbf24", "#f87171"]}
                      animationSpeed={5}
                      showBorder={false}
                      className="text-xl md:text-2xl"
                    >
                      Unlock unprecedented growth, dominate your competition, and achieve extraordinary results with our revolutionary platform.
                    </GradientText>
                  </div>
                </div>

                <div className="flex flex-wrap justify-center gap-4 mb-12">
                  <div className="flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur-md rounded-full border border-white/30 hover:bg-white/30 hover:border-white/50 hover:scale-105 transition-all duration-300 group animate-bounce-in" style={{ animationDelay: '0.1s' }}>
                    <Users className="w-5 h-5 text-green-400 group-hover:animate-pulse" />
                    <span className="text-white font-medium">Join 50,000+ Marketers</span>
                  </div>
                  <div className="flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur-md rounded-full border border-white/30 hover:bg-white/30 hover:border-white/50 hover:scale-105 transition-all duration-300 group animate-bounce-in" style={{ animationDelay: '0.2s' }}>
                    <BarChart3 className="w-5 h-5 text-blue-400 group-hover:animate-pulse" />
                    <span className="text-white font-medium">Proven Results</span>
                  </div>
                  <div className="flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur-md rounded-full border border-white/30 hover:bg-white/30 hover:border-white/50 hover:scale-105 transition-all duration-300 group animate-bounce-in" style={{ animationDelay: '0.3s' }}>
                    <Lightbulb className="w-5 h-5 text-yellow-400 group-hover:animate-pulse" />
                    <span className="text-white font-medium">AI-First Approach</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Features Grid */}
            <div className={`grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16 transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              {features.map((feature, index) => (
                <Card 
                  key={index} 
                  className="p-6 bg-white/20 backdrop-blur-md border-white/30 text-center hover:bg-white/25 transition-all duration-500 group shadow-xl hover:shadow-2xl hover:shadow-blue-500/20 transform hover:scale-105 hover:-translate-y-2 animate-bounce-in relative overflow-hidden"
                  style={{ 
                    animationDelay: `${index * 0.1}s`,
                    animation: isVisible ? `bounce-in 0.8s ease-out ${index * 0.1}s both, float 3s ease-in-out ${index * 0.5}s infinite` : undefined
                  }}
                >
                  {/* Animated background glow */}
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-lg"></div>
                  
                  {/* Floating particles effect */}
                  <div className="absolute top-2 right-2 w-2 h-2 bg-blue-400/50 rounded-full animate-ping group-hover:animate-pulse"></div>
                  <div className="absolute bottom-3 left-3 w-1 h-1 bg-purple-400/50 rounded-full animate-pulse delay-75"></div>
                  
                  <div className="relative z-10">
                    <div className="w-12 h-12 mx-auto mb-4 bg-blue-500/30 backdrop-blur-sm rounded-full flex items-center justify-center text-blue-400 group-hover:scale-125 group-hover:rotate-12 transition-all duration-500 group-hover:bg-blue-500/40 group-hover:shadow-lg group-hover:shadow-blue-400/30">
                      <div className="group-hover:animate-pulse">
                        {feature.icon}
                      </div>
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2 drop-shadow-md group-hover:text-blue-200 transition-colors duration-300">{feature.title}</h3>
                    <p className="text-blue-200 text-sm drop-shadow-sm group-hover:text-white transition-colors duration-300">{feature.description}</p>
                  </div>
                  
                  {/* Animated border on hover */}
                  <div className="absolute inset-0 rounded-lg border-2 border-transparent group-hover:border-blue-400/50 transition-all duration-500"></div>
                </Card>
              ))}
            </div>

            {/* CTA Section */}
            <div className={`text-center transition-all duration-1000 delay-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              <div className="flex justify-center items-center mb-6">
                <Button 
                  onClick={handleContinueToDashboard}
                  size="lg" 
                  className="px-12 py-6 text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0 rounded-full shadow-2xl hover:shadow-blue-500/25 transform hover:scale-105 transition-all duration-300 backdrop-blur-sm"
                >
                  Enter Your Dashboard
                  <ArrowRight className="ml-3 h-6 w-6" />
                </Button>
              </div>
              <p className="text-blue-200 text-lg drop-shadow-md">
                Ready to revolutionize your marketing strategy?
              </p>
            </div>
          </div>
        </div>

        {/* Feature Description Panel */}
        <div className={`fixed top-16 left-0 right-0 h-auto bg-black/95 backdrop-blur-md z-25 transition-all duration-700 ease-in-out border-b border-white/20 ${
          isSliding && activeFeature !== null ? 'translate-y-0 opacity-100' : '-translate-y-full opacity-0'
        }`}>
          {activeFeature !== null && (
            <div className="container mx-auto px-4 py-8">
              <div className="flex items-center justify-center">
                <div className="max-w-4xl text-center">
                  <div className={`w-20 h-20 mx-auto mb-6 bg-gradient-to-r ${featureNavigationItems[activeFeature].color} rounded-3xl flex items-center justify-center shadow-2xl`}>
                    <div className="text-white scale-150">
                      {featureNavigationItems[activeFeature].icon}
                    </div>
                  </div>
                  
                  <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                    <GradientText
                      colors={["#40ffaa", "#4079ff", "#ff6b40", "#ff40aa"]}
                      animationSpeed={3}
                      showBorder={false}
                      className="text-4xl md:text-5xl font-bold"
                    >
                      {featureNavigationItems[activeFeature].title}
                    </GradientText>
                  </h2>
                  
                  <p className="text-xl md:text-2xl text-blue-200 leading-relaxed mb-8 max-w-3xl mx-auto">
                    {featureNavigationItems[activeFeature].description}
                  </p>
                  
                  <div className="flex justify-center">
                    <div className="flex items-center gap-3 text-blue-300 hover:text-white transition-colors duration-300 cursor-pointer group bg-white/10 px-6 py-3 rounded-full backdrop-blur-sm hover:bg-white/20">
                      <span className="text-lg font-medium">Explore Feature</span>
                      <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </AuthGuard>
  );
}