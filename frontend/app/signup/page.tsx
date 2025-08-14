import { SignedIn, SignedOut, RedirectToSignUp } from "@clerk/nextjs"
import { redirect } from "next/navigation"
import { SignUpForm } from "@/components/auth/signup-form"

export default function SignupPage() {
  return (
    <>
      <SignedIn>
        {redirect("/dashboard")}
      </SignedIn>
      <SignedOut>
        <SignUpForm />
      </SignedOut>
    </>
  )
}
