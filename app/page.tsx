import { SignedIn, SignedOut, SignInButton } from "@clerk/nextjs"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="text-center space-y-6 max-w-2xl mx-auto px-4">
        <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          MarketingAI Pro
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-lg mx-auto">
          AI-powered marketing and content strategy platform to supercharge your campaigns
        </p>
        
        <SignedOut>
          <div className="space-y-4">
            <p className="text-gray-500 dark:text-gray-400">
              Get started with your marketing transformation today
            </p>
            <div className="flex gap-4 justify-center">
              <SignInButton mode="modal">
                <Button variant="outline" size="lg">
                  Sign In
                </Button>
              </SignInButton>
              <Button size="lg" asChild>
                <Link href="/signup">Get Started Free</Link>
              </Button>
            </div>
          </div>
        </SignedOut>

        <SignedIn>
          <div className="space-y-4">
            <p className="text-gray-600 dark:text-gray-300">
              Welcome back! Ready to optimize your marketing campaigns?
            </p>
            <div className="flex gap-4 justify-center">
              <Button size="lg" asChild>
                <Link href="/dashboard">Go to Dashboard</Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="/onboarding">Setup Guide</Link>
              </Button>
            </div>
          </div>
        </SignedIn>
      </div>
    </div>
  )
}
