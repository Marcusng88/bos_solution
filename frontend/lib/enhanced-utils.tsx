"use client"

import React from 'react'

// Accessibility utilities
export const A11yUtils = {
  // Skip link for keyboard navigation
  SkipLink: ({ href = "#main-content", children = "Skip to main content" }: {
    href?: string
    children?: React.ReactNode
  }) => (
    <a
      href={href}
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 bg-blue-600 text-white px-4 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    >
      {children}
    </a>
  ),

  // Screen reader only text
  ScreenReaderOnly: ({ children }: { children: React.ReactNode }) => (
    <span className="sr-only">{children}</span>
  ),

  // Focus trap for modals
  useFocusTrap: (isActive: boolean) => {
    const containerRef = React.useRef<HTMLDivElement>(null)

    React.useEffect(() => {
      if (!isActive || !containerRef.current) return

      const container = containerRef.current
      const focusableElements = container.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const firstElement = focusableElements[0] as HTMLElement
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

      const handleTabKey = (e: KeyboardEvent) => {
        if (e.key !== 'Tab') return

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement?.focus()
            e.preventDefault()
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement?.focus()
            e.preventDefault()
          }
        }
      }

      const handleEscapeKey = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          const event = new CustomEvent('escape-pressed')
          container.dispatchEvent(event)
        }
      }

      document.addEventListener('keydown', handleTabKey)
      document.addEventListener('keydown', handleEscapeKey)
      firstElement?.focus()

      return () => {
        document.removeEventListener('keydown', handleTabKey)
        document.removeEventListener('keydown', handleEscapeKey)
      }
    }, [isActive])

    return containerRef
  },

  // Announce to screen readers
  announce: (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcer = document.createElement('div')
    announcer.setAttribute('aria-live', priority)
    announcer.setAttribute('aria-atomic', 'true')
    announcer.className = 'sr-only'
    document.body.appendChild(announcer)
    
    announcer.textContent = message
    
    setTimeout(() => {
      document.body.removeChild(announcer)
    }, 1000)
  },

  // ARIA live region hook
  useLiveRegion: () => {
    const [message, setMessage] = React.useState('')
    const [priority, setPriority] = React.useState<'polite' | 'assertive'>('polite')

    const announce = React.useCallback((text: string, urgency: 'polite' | 'assertive' = 'polite') => {
      setMessage('')
      setPriority(urgency)
      setTimeout(() => setMessage(text), 100)
    }, [])

    const LiveRegion = React.useCallback(() => (
      <div
        aria-live={priority}
        aria-atomic="true"
        className="sr-only"
      >
        {message}
      </div>
    ), [message, priority])

    return { announce, LiveRegion }
  }
}

// Performance utilities
export const PerfUtils = {
  // Lazy component wrapper
  createLazyComponent: <T,>(
    importFn: () => Promise<{ default: React.ComponentType<T> }>,
    fallback?: React.ComponentType
  ) => {
    const LazyComponent = React.lazy(importFn)
    
    return React.forwardRef<any, T>((props, ref) => (
      <React.Suspense fallback={fallback ? React.createElement(fallback) : null}>
        <LazyComponent {...props} ref={ref} />
      </React.Suspense>
    ))
  },

  // Intersection observer hook for lazy loading
  useIntersectionObserver: (
    options: IntersectionObserverInit = {}
  ) => {
    const [ref, setRef] = React.useState<Element | null>(null)
    const [isIntersecting, setIsIntersecting] = React.useState(false)
    const [hasIntersected, setHasIntersected] = React.useState(false)

    React.useEffect(() => {
      if (!ref) return

      const observer = new IntersectionObserver(
        ([entry]) => {
          setIsIntersecting(entry.isIntersecting)
          if (entry.isIntersecting) {
            setHasIntersected(true)
          }
        },
        {
          threshold: 0.1,
          rootMargin: '50px',
          ...options
        }
      )

      observer.observe(ref)

      return () => observer.disconnect()
    }, [ref, options])

    return { setRef, isIntersecting, hasIntersected }
  },

  // Debounced value hook
  useDebounce: <T,>(value: T, delay: number): T => {
    const [debouncedValue, setDebouncedValue] = React.useState<T>(value)

    React.useEffect(() => {
      const handler = setTimeout(() => {
        setDebouncedValue(value)
      }, delay)

      return () => clearTimeout(handler)
    }, [value, delay])

    return debouncedValue
  },

  // Throttled callback hook
  useThrottle: <T extends (...args: any[]) => any>(
    callback: T,
    delay: number
  ): T => {
    const lastRun = React.useRef<number>(Date.now())

    return React.useCallback(
      ((...args: Parameters<T>) => {
        if (Date.now() - lastRun.current >= delay) {
          callback(...args)
          lastRun.current = Date.now()
        }
      }) as T,
      [callback, delay]
    )
  },

  // Virtual scroll hook for large lists
  useVirtualScroll: <T,>(
    items: T[],
    itemHeight: number,
    containerHeight: number,
    overscan: number = 5
  ) => {
    const [scrollTop, setScrollTop] = React.useState(0)

    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    )

    const visibleItems = items.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index
    }))

    const totalHeight = items.length * itemHeight
    const offsetY = startIndex * itemHeight

    return {
      visibleItems,
      totalHeight,
      offsetY,
      onScroll: (e: React.UIEvent<HTMLDivElement>) => {
        setScrollTop(e.currentTarget.scrollTop)
      }
    }
  },

  // Memory usage monitoring
  useMemoryUsage: () => {
    const [memoryUsage, setMemoryUsage] = React.useState<{
      used: number
      total: number
      percentage: number
    } | null>(null)

    React.useEffect(() => {
      if (!('memory' in performance)) return

      const updateMemoryUsage = () => {
        const memory = (performance as any).memory
        if (memory) {
          const used = memory.usedJSHeapSize
          const total = memory.totalJSHeapSize
          setMemoryUsage({
            used,
            total,
            percentage: (used / total) * 100
          })
        }
      }

      updateMemoryUsage()
      const interval = setInterval(updateMemoryUsage, 5000)

      return () => clearInterval(interval)
    }, [])

    return memoryUsage
  },

  // Image lazy loading component
  LazyImage: React.forwardRef<
    HTMLImageElement,
    React.ImgHTMLAttributes<HTMLImageElement> & {
      placeholderSrc?: string
      threshold?: number
    }
  >(({ src, placeholderSrc, threshold = 0.1, ...props }, ref) => {
    const [imageSrc, setImageSrc] = React.useState(placeholderSrc || '')
    const [isLoaded, setIsLoaded] = React.useState(false)
    const { setRef, hasIntersected } = PerfUtils.useIntersectionObserver({
      threshold
    })

    React.useEffect(() => {
      if (hasIntersected && src && typeof src === 'string') {
        const img = new Image()
        img.onload = () => {
          setImageSrc(src)
          setIsLoaded(true)
        }
        img.src = src
      }
    }, [hasIntersected, src])

    return (
      <img
        {...props}
        ref={(node) => {
          setRef(node)
          if (typeof ref === 'function') ref(node)
          else if (ref) ref.current = node
        }}
        src={imageSrc}
        className={`transition-opacity duration-300 ${
          isLoaded ? 'opacity-100' : 'opacity-70'
        } ${props.className || ''}`}
      />
    )
  })
}

// Dark mode utilities
export const ThemeUtils = {
  // System theme detection
  useSystemTheme: () => {
    const [isDark, setIsDark] = React.useState(false)

    React.useEffect(() => {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      setIsDark(mediaQuery.matches)

      const handler = (e: MediaQueryListEvent) => setIsDark(e.matches)
      mediaQuery.addEventListener('change', handler)

      return () => mediaQuery.removeEventListener('change', handler)
    }, [])

    return isDark
  },

  // Color scheme class names
  colorScheme: {
    light: {
      bg: 'bg-white',
      text: 'text-gray-900',
      border: 'border-gray-200',
      hover: 'hover:bg-gray-50'
    },
    dark: {
      bg: 'bg-gray-900',
      text: 'text-gray-100',
      border: 'border-gray-700',
      hover: 'hover:bg-gray-800'
    }
  }
}

// Responsive utilities
export const ResponsiveUtils = {
  // Breakpoint hook
  useBreakpoint: (breakpoint: 'sm' | 'md' | 'lg' | 'xl' | '2xl' = 'md') => {
    const breakpoints = {
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
      '2xl': 1536
    }

    const [isMatch, setIsMatch] = React.useState(false)

    React.useEffect(() => {
      const mediaQuery = window.matchMedia(`(min-width: ${breakpoints[breakpoint]}px)`)
      setIsMatch(mediaQuery.matches)

      const handler = (e: MediaQueryListEvent) => setIsMatch(e.matches)
      mediaQuery.addEventListener('change', handler)

      return () => mediaQuery.removeEventListener('change', handler)
    }, [breakpoint, breakpoints])

    return isMatch
  },

  // Window size hook
  useWindowSize: () => {
    const [windowSize, setWindowSize] = React.useState({
      width: typeof window !== 'undefined' ? window.innerWidth : 0,
      height: typeof window !== 'undefined' ? window.innerHeight : 0
    })

    React.useEffect(() => {
      const handleResize = () => {
        setWindowSize({
          width: window.innerWidth,
          height: window.innerHeight
        })
      }

      window.addEventListener('resize', handleResize)
      return () => window.removeEventListener('resize', handleResize)
    }, [])

    return windowSize
  },

  // Mobile detection
  useIsMobile: () => {
    const isSmall = ResponsiveUtils.useBreakpoint('md')
    return !isSmall
  }
}

// Form utilities
export const FormUtils = {
  // Form field wrapper with enhanced accessibility
  FieldWrapper: ({ 
    children, 
    label, 
    error, 
    description, 
    required = false,
    className = ''
  }: {
    children: React.ReactNode
    label?: string
    error?: string
    description?: string
    required?: boolean
    className?: string
  }) => {
    const id = React.useId()
    const errorId = `${id}-error`
    const descriptionId = `${id}-description`

    return (
      <div className={`space-y-2 ${className}`}>
        {label && (
          <label htmlFor={id} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
            {required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
          </label>
        )}
        
        {React.isValidElement(children) ? React.cloneElement(children, {
          id,
          'aria-describedby': [
            description ? descriptionId : '',
            error ? errorId : ''
          ].filter(Boolean).join(' ') || undefined,
          'aria-invalid': error ? 'true' : undefined,
          'aria-required': required ? 'true' : undefined
        } as any) : children}
        
        {description && (
          <p id={descriptionId} className="text-sm text-gray-600 dark:text-gray-400">
            {description}
          </p>
        )}
        
        {error && (
          <p id={errorId} className="text-sm text-red-600 dark:text-red-400" role="alert">
            {error}
          </p>
        )}
      </div>
    )
  }
}

export default {
  A11yUtils,
  PerfUtils,
  ThemeUtils,
  ResponsiveUtils,
  FormUtils
}