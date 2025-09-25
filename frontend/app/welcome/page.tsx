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

            {/* Pricing Section */}
            <div className={`mb-20 transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              <div className="text-center mb-12">
                <h2 className="text-5xl md:text-6xl font-black mb-6">
                  <GradientText
                    colors={["#40ffaa", "#4079ff", "#ff6b40", "#ff40aa"]}
                    animationSpeed={3}
                    showBorder={false}
                    className="text-5xl md:text-6xl font-black"
                  >
                    Try BOSSolution free for 14 days
                  </GradientText>
                </h2>
                <p className="text-xl text-blue-200 mb-2">No credit card required. Cancel anytime.</p>
                <p className="text-lg text-blue-300">75% more affordable than Sprout Social</p>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
                {/* Starter Plan */}
                <Card className="p-8 bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/15 transition-all duration-500 group shadow-xl hover:shadow-2xl hover:shadow-blue-500/20 transform hover:scale-105 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  <div className="relative z-10">
                    <div className="text-center mb-6">
                      <h3 className="text-2xl font-bold text-white mb-2">Starter</h3>
                      <p className="text-blue-200 text-sm mb-4">Perfect for solopreneurs and small teams</p>
                      <div className="mb-4">
                        <span className="text-4xl font-black text-white">RM49</span>
                        <span className="text-blue-200">/month</span>
                      </div>
                      <div className="text-xs text-blue-300 mb-6">
                        Compare: Sprout Social RM899/month
                      </div>
                    </div>
                    
                    <Button className="w-full mb-6 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white border-0 rounded-full py-3">
                      Start your free trial
                    </Button>
                    
                    <div className="space-y-3 text-sm">
                      <div className="flex items-center text-blue-200">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        3 social media profiles
                      </div>
                      <div className="flex items-center text-blue-200">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        AI content generation (50 posts/month)
                      </div>
                      <div className="flex items-center text-blue-200">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        Basic competitor monitoring
                      </div>
                      <div className="flex items-center text-blue-200">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        ROI analytics dashboard
                      </div>
                      <div className="flex items-center text-blue-200">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        Email support
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Growth Plan - Most Popular */}
                <Card className="p-8 bg-gradient-to-br from-green-500/20 to-blue-500/20 backdrop-blur-md border-green-400/50 hover:from-green-500/25 hover:to-blue-500/25 transition-all duration-500 group shadow-xl hover:shadow-2xl hover:shadow-green-500/30 transform hover:scale-105 relative overflow-hidden">
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-gradient-to-r from-green-400 to-green-500 text-white px-4 py-1 text-xs font-bold">
                      Most Popular
                    </Badge>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 via-transparent to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  <div className="relative z-10">
                    <div className="text-center mb-6">
                      <h3 className="text-2xl font-bold text-white mb-2">Growth</h3>
                      <p className="text-green-200 text-sm mb-4">Best for growing businesses</p>
                      <div className="mb-4">
                        <span className="text-4xl font-black text-white">RM99</span>
                        <span className="text-green-200">/month</span>
                      </div>
                      <div className="text-xs text-green-300 mb-6">
                        Compare: Sprout Social RM1,349/month
                      </div>
                    </div>
                    
                    <Button className="w-full mb-6 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white border-0 rounded-full py-3">
                      Start your free trial
                    </Button>
                    
                    <div className="space-y-3 text-sm">
                      <div className="text-green-200 font-medium mb-2">Everything in Starter, plus:</div>
                      <div className="flex items-center text-green-200">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        10 social media profiles
                      </div>
                      <div className="flex items-center text-green-200">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        Unlimited AI content generation
                      </div>
                      <div className="flex items-center text-green-200">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        Advanced competitor analysis
                      </div>
                      <div className="flex items-center text-green-200">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        Automated content scheduling
                      </div>
                      <div className="flex items-center text-green-200">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        AI chat assistant
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Pro Plan */}
                <Card className="p-8 bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/15 transition-all duration-500 group shadow-xl hover:shadow-2xl hover:shadow-purple-500/20 transform hover:scale-105 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-transparent to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  <div className="relative z-10">
                    <div className="text-center mb-6">
                      <h3 className="text-2xl font-bold text-white mb-2">Pro</h3>
                      <p className="text-purple-200 text-sm mb-4">Built for marketing teams & agencies</p>
                      <div className="mb-4">
                        <span className="text-4xl font-black text-white">RM199</span>
                        <span className="text-purple-200">/month</span>
                      </div>
                      <div className="text-xs text-purple-300 mb-6">
                        Compare: Sprout Social RM1,799/month
                      </div>
                    </div>
                    
                    <Button className="w-full mb-6 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white border-0 rounded-full py-3">
                      Start your free trial
                    </Button>
                    
                    <div className="space-y-3 text-sm">
                      <div className="text-purple-200 font-medium mb-2">Everything in Growth, plus:</div>
                      <div className="flex items-center text-purple-200">
                        <div className="w-2 h-2 bg-purple-400 rounded-full mr-3"></div>
                        25 social media profiles
                      </div>
                      <div className="flex items-center text-purple-200">
                        <div className="w-2 h-2 bg-purple-400 rounded-full mr-3"></div>
                        Real-time competitor alerts
                      </div>
                      <div className="flex items-center text-purple-200">
                        <div className="w-2 h-2 bg-purple-400 rounded-full mr-3"></div>
                        Advanced AI insights
                      </div>
                      <div className="flex items-center text-purple-200">
                        <div className="w-2 h-2 bg-purple-400 rounded-full mr-3"></div>
                        White-label reporting
                      </div>
                      <div className="flex items-center text-purple-200">
                        <div className="w-2 h-2 bg-purple-400 rounded-full mr-3"></div>
                        Priority support
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Enterprise Plan */}
                <Card className="p-8 bg-gradient-to-br from-orange-500/20 to-red-500/20 backdrop-blur-md border-orange-400/50 hover:from-orange-500/25 hover:to-red-500/25 transition-all duration-500 group shadow-xl hover:shadow-2xl hover:shadow-orange-500/30 transform hover:scale-105 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 via-transparent to-red-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  <div className="relative z-10">
                    <div className="text-center mb-6">
                      <h3 className="text-2xl font-bold text-white mb-2">Enterprise</h3>
                      <p className="text-orange-200 text-sm mb-4">For large organizations</p>
                      <div className="mb-4">
                        <span className="text-4xl font-black text-white">Custom</span>
                      </div>
                      <div className="text-xs text-orange-300 mb-6">
                        Tailored pricing for your needs
                      </div>
                    </div>
                    
                    <Button className="w-full mb-6 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white border-0 rounded-full py-3">
                      Schedule a demo
                    </Button>
                    
                    <div className="space-y-3 text-sm">
                      <div className="text-orange-200 font-medium mb-2">Everything in Pro, plus:</div>
                      <div className="flex items-center text-orange-200">
                        <div className="w-2 h-2 bg-orange-400 rounded-full mr-3"></div>
                        Unlimited social profiles
                      </div>
                      <div className="flex items-center text-orange-200">
                        <div className="w-2 h-2 bg-orange-400 rounded-full mr-3"></div>
                        Custom AI model training
                      </div>
                      <div className="flex items-center text-orange-200">
                        <div className="w-2 h-2 bg-orange-400 rounded-full mr-3"></div>
                        Dedicated account manager
                      </div>
                      <div className="flex items-center text-orange-200">
                        <div className="w-2 h-2 bg-orange-400 rounded-full mr-3"></div>
                        Custom integrations
                      </div>
                      <div className="flex items-center text-orange-200">
                        <div className="w-2 h-2 bg-orange-400 rounded-full mr-3"></div>
                        24/7 priority support
                      </div>
                    </div>
                  </div>
                </Card>
              </div>

              {/* Competitive Advantages */}
              <div className="mt-16 text-center">
                <h3 className="text-3xl font-bold text-white mb-8">
                  <GradientText
                    colors={["#40ffaa", "#4079ff", "#ff6b40"]}
                    animationSpeed={3}
                    showBorder={false}
                    className="text-3xl font-bold"
                  >
                    Why Choose BOSSolution Over Sprout Social?
                  </GradientText>
                </h3>
                
                <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                  <div className="text-center p-6 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:bg-white/15 transition-all duration-300">
                    <DollarSign className="w-12 h-12 mx-auto mb-4 text-green-400" />
                    <h4 className="text-xl font-bold text-white mb-2">75% Cost Savings</h4>
                    <p className="text-blue-200">Get enterprise-level features at a fraction of the cost</p>
                  </div>
                  
                  <div className="text-center p-6 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:bg-white/15 transition-all duration-300">
                    <Brain className="w-12 h-12 mx-auto mb-4 text-purple-400" />
                    <h4 className="text-xl font-bold text-white mb-2">AI-First Approach</h4>
                    <p className="text-blue-200">Built-in AI content generation and competitor analysis</p>
                  </div>
                  
                  <div className="text-center p-6 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:bg-white/15 transition-all duration-300">
                    <TrendingUp className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                    <h4 className="text-xl font-bold text-white mb-2">Comprehensive ROI</h4>
                    <p className="text-blue-200">Advanced analytics and predictive insights included</p>
                  </div>
                </div>
              </div>
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