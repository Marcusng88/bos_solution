"use client"

import { SignIn } from "@clerk/nextjs"
import { useEffect } from "react"

export function LoginForm() {
  useEffect(() => {
    // Function to make Google button wider
    const makeGoogleButtonWider = () => {
      // Try multiple selectors to find the Google button
      const selectors = [
        'button[data-provider="google"]',
        '[data-testid="social-buttons-block-button"]:has([data-provider="google"])',
        'button:has(span:contains("Google"))',
        'button:has(span:contains("Continue with Google"))',
        '[data-testid="social-buttons-block"] button',
        '.cl-socialButtonsBlockButton'
      ]
      
      selectors.forEach(selector => {
        try {
          const elements = document.querySelectorAll(selector)
          elements.forEach(element => {
            if (element instanceof HTMLElement) {
              element.style.width = '100%'
              element.style.maxWidth = '100%'
              element.style.minWidth = '100%'
              console.log('Made Google button wider:', element)
            }
          })
        } catch (e) {
          // Ignore errors for invalid selectors
        }
      })
    }

    // Run immediately
    makeGoogleButtonWider()
    
    // Also run after a short delay to catch late-rendering elements
    const timer = setTimeout(makeGoogleButtonWider, 1000)
    
    // Cleanup
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="w-full max-w-md mx-auto">
      <SignIn 
        routing="hash"
        appearance={{
          elements: {
            rootBox: "w-full",
            card: "shadow-none border-0",
            headerTitle: "text-2xl font-bold text-foreground",
            headerSubtitle: "text-muted-foreground",
            formButtonPrimary: "bg-primary hover:bg-primary/90 text-primary-foreground",
            formFieldInput: "border border-input bg-background text-foreground",
            formFieldLabel: "text-foreground",
            footerActionLink: "text-primary hover:text-primary/90",
            dividerLine: "bg-border",
            dividerText: "text-muted-foreground",
            socialButtonsBlockButton: "border border-input bg-background text-foreground hover:bg-accent hover:text-accent-foreground",
            socialButtonsBlockButtonText: "text-foreground",
          }
        }}
        fallbackRedirectUrl="/onboarding"
        signUpUrl="/signup"
      />
      <style jsx global>{`
        /* Multiple ways to hide Facebook - one of these should work */
        
        /* Method 1: Hide by provider attribute */
        button[data-provider="facebook"],
        button[data-provider="meta"] {
          display: none !important;
        }
        
        /* Method 2: Hide by test ID */
        [data-testid="social-buttons-block-button"]:has([data-provider="facebook"]),
        [data-testid="social-buttons-block-button"]:has([data-provider="meta"]) {
          display: none !important;
        }
        
        /* Method 3: Hide by button text content */
        button:has(span:contains("Facebook")),
        button:has(span:contains("Continue with Facebook")) {
          display: none !important;
        }
        
        /* Method 4: Hide by aria-label */
        button[aria-label*="Facebook"],
        button[aria-label*="facebook"] {
          display: none !important;
        }
        
        /* Method 5: Hide by class names that might contain Facebook */
        button[class*="facebook"],
        button[class*="Facebook"] {
          display: none !important;
        }
        
        /* Method 6: Nuclear option - hide any button with Facebook in its HTML */
        button:has(*:contains("Facebook")) {
          display: none !important;
        }
      `}</style>
    </div>
  )
}
