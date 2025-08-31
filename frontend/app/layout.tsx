import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { ThemeProvider } from "@/components/optimization/theme-provider"
import { ClerkProviderWrapper } from "@/components/providers/clerk-provider"
import { Toaster } from "@/components/ui/toaster"
import { AIChatWidget } from "@/components/optimization/ai-chat-widget"
import "./globals.css"

export const metadata: Metadata = {
  title: "BOSSolution",
  description: "AI-powered marketing and content strategy platform",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <style>{`
html {
  font-family: ${GeistSans.style.fontFamily};
  --font-sans: ${GeistSans.variable};
  --font-mono: ${GeistMono.variable};
}
        `}</style>
        
        {/* Facebook SDK */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.fbAsyncInit = function() {
                FB.init({
                  appId      : '${process.env.NEXT_PUBLIC_FACEBOOK_APP_ID}',
                  cookie     : true,
                  xfbml      : true,
                  version    : 'v18.0'
                });
                  
                FB.AppEvents.logPageView();   
                  
              };

              (function(d, s, id){
                 var js, fjs = d.getElementsByTagName(s)[0];
                 if (d.getElementById(id)) {return;}
                 js = d.createElement(s); js.id = id;
                 js.src = "https://connect.facebook.net/en_US/sdk.js";
                 fjs.parentNode.insertBefore(js, fjs);
               }(document, 'script', 'facebook-jssdk'));
            `,
          }}
        />
      </head>
      <body suppressHydrationWarning>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          <ClerkProviderWrapper>
            {children}
            <AIChatWidget />
            <Toaster />
          </ClerkProviderWrapper>
        </ThemeProvider>
      </body>
    </html>
  )
}
