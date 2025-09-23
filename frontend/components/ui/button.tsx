import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-semibold transition-all duration-300 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive relative overflow-hidden group",
  {
    variants: {
      variant: {
        default:
          "bg-gradient-to-r from-primary to-primary-light text-primary-foreground shadow-soft hover:shadow-elevated hover:scale-[1.02] hover:from-primary-light hover:to-primary active:scale-[0.98] before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/20 before:to-transparent before:opacity-0 hover:before:opacity-100 before:transition-opacity",
        destructive:
          "bg-gradient-to-r from-destructive to-red-600 text-destructive-foreground shadow-soft hover:shadow-elevated hover:scale-[1.02] hover:from-red-600 hover:to-destructive active:scale-[0.98] focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40",
        outline:
          "border-2 border-border bg-background/80 backdrop-blur-sm shadow-soft hover:bg-accent hover:text-accent-foreground hover:border-primary/30 hover:shadow-elevated hover:scale-[1.02] active:scale-[0.98] dark:bg-background/50 dark:hover:bg-accent/50",
        secondary:
          "bg-gradient-to-r from-secondary to-muted text-secondary-foreground shadow-soft hover:shadow-elevated hover:scale-[1.02] hover:from-muted hover:to-secondary active:scale-[0.98]",
        ghost:
          "hover:bg-accent/80 hover:text-accent-foreground hover:shadow-soft hover:scale-[1.02] active:scale-[0.98] dark:hover:bg-accent/40",
        link: "text-primary underline-offset-4 hover:underline hover:text-primary-light transition-colors",
      },
      size: {
        default: "h-10 px-6 py-2.5 has-[>svg]:px-5",
        sm: "h-8 rounded-lg gap-1.5 px-4 text-xs has-[>svg]:px-3",
        lg: "h-12 rounded-xl px-8 text-base font-bold has-[>svg]:px-6",
        icon: "size-10 rounded-xl",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
