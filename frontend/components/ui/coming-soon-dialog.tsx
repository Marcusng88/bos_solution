"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Construction, Calendar, Clock, Zap } from "lucide-react"

interface ComingSoonDialogProps {
  trigger: React.ReactNode
  title?: string
  description?: string
  features?: string[]
  estimatedRelease?: string
}

export function ComingSoonDialog({ 
  trigger, 
  title = "Coming Soon! 🚀",
  description = "This feature is currently under development and will be available soon.",
  features = [],
  estimatedRelease = "Q1 2025"
}: ComingSoonDialogProps) {
  const [open, setOpen] = useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-2">
            <Construction className="h-6 w-6 text-blue-600" />
            <Badge variant="secondary" className="text-xs">
              Under Development
            </Badge>
          </div>
          <DialogTitle className="text-xl font-bold text-gray-900">
            {title}
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            {description}
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {features.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                <Zap className="h-4 w-4 text-yellow-500" />
                Planned Features
              </h4>
              <ul className="space-y-2">
                {features.map((feature, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Calendar className="h-4 w-4" />
            Estimated Release: {estimatedRelease}
          </div>
          
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Clock className="h-4 w-4" />
            We're working hard to bring you the best experience
          </div>
        </div>
        
        <div className="flex justify-end gap-2 pt-4">
          <Button variant="outline" onClick={() => setOpen(false)}>
            Got it
          </Button>
          <Button onClick={() => setOpen(false)}>
            Notify me
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
