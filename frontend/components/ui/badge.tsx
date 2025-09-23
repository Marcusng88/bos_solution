import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-full border px-3 py-1 text-xs font-semibold w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1.5 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-2 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-all duration-300 overflow-hidden shadow-soft",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-gradient-to-r from-primary to-primary-light text-primary-foreground shadow-soft [a&]:hover:shadow-elevated [a&]:hover:scale-105",
        secondary:
          "border-transparent bg-gradient-to-r from-secondary to-muted text-secondary-foreground [a&]:hover:shadow-elevated [a&]:hover:scale-105",
        destructive:
          "border-transparent bg-gradient-to-r from-destructive to-red-600 text-white [a&]:hover:shadow-elevated [a&]:hover:scale-105 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40",
        outline:
          "text-foreground border-border/50 bg-background/60 backdrop-blur-sm [a&]:hover:bg-accent [a&]:hover:text-accent-foreground [a&]:hover:shadow-elevated [a&]:hover:scale-105 [a&]:hover:border-primary/30",
        success:
          "border-transparent bg-gradient-to-r from-emerald-500 to-green-600 text-white [a&]:hover:shadow-elevated [a&]:hover:scale-105",
        warning:
          "border-transparent bg-gradient-to-r from-orange-500 to-yellow-600 text-white [a&]:hover:shadow-elevated [a&]:hover:scale-105",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({
  className,
  variant,
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "span"

  return (
    <Comp
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
