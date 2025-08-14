import { SignedIn, SignedOut, RedirectToSignUp } from "@clerk/nextjs"
import { redirect } from "next/navigation"

export default function SignupPage() {
  return (
    <>
      <SignedIn>
        {redirect("/dashboard")}
      </SignedIn>
      <SignedOut>
        <RedirectToSignUp />
      </SignedOut>
    </>
  )
}
