"use client"

import { SignUp } from "@clerk/nextjs"

export function SignUpForm() {
  return (
    <div className="w-full max-w-md mx-auto">
      <SignUp 
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
        signInUrl="/login"
      />
    </div>
  )
}
