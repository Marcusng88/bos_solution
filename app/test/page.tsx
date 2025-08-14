import { currentUser } from "@clerk/nextjs/server"
import { SignedIn, SignedOut, UserButton } from "@clerk/nextjs"

export default async function UserTestPage() {
  const user = await currentUser()

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-4">User Authentication Test</h1>
      
      <SignedOut>
        <p className="text-red-600">You are not signed in.</p>
      </SignedOut>

      <SignedIn>
        <div className="space-y-4">
          <p className="text-green-600">You are signed in!</p>
          <div className="flex items-center gap-4">
            <UserButton />
            <span>Welcome, {user?.firstName || user?.emailAddresses[0]?.emailAddress}</span>
          </div>
          <div className="bg-gray-100 p-4 rounded">
            <h3 className="font-semibold">User Details:</h3>
            <pre className="text-sm">{JSON.stringify(user, null, 2)}</pre>
          </div>
        </div>
      </SignedIn>
    </div>
  )
}
