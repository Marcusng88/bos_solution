"use client"

import * as React from "react"
import { Eye, EyeOff, X, Search, AlertCircle, CheckCircle, Upload } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'default' | 'error' | 'success'
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  isLoading?: boolean
  error?: string
  success?: string
  showClearButton?: boolean
  onClear?: () => void
}

interface PasswordInputProps extends Omit<InputProps, 'type'> {
  showToggle?: boolean
}

interface SearchInputProps extends Omit<InputProps, 'type'> {
  onSearch?: (value: string) => void
  searchDelay?: number
}

interface FileInputProps extends Omit<InputProps, 'type'> {
  accept?: string
  multiple?: boolean
  maxSize?: number // in bytes
  onFileSelect?: (files: FileList | null) => void
  preview?: boolean
}

interface FormFieldProps {
  label?: string
  description?: string
  error?: string
  success?: string
  required?: boolean
  children: React.ReactNode
  className?: string
}

const inputVariants = {
  default: "border-input bg-background hover:border-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
  error: "border-red-500 bg-red-50 dark:bg-red-950 focus:border-red-500 focus:ring-2 focus:ring-red-200",
  success: "border-green-500 bg-green-50 dark:bg-green-950 focus:border-green-500 focus:ring-2 focus:ring-green-200"
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className, 
    type, 
    variant = 'default',
    leftIcon,
    rightIcon,
    isLoading,
    error,
    success,
    showClearButton,
    onClear,
    value,
    onChange,
    ...props 
  }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false)
    const hasValue = value !== undefined && value !== ''

    const handleClear = React.useCallback(() => {
      if (onClear) {
        onClear()
      } else if (onChange) {
        onChange({ target: { value: '' } } as React.ChangeEvent<HTMLInputElement>)
      }
    }, [onClear, onChange])

    const currentVariant = error ? 'error' : success ? 'success' : variant

    return (
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {leftIcon}
          </div>
        )}
        
        <input
          type={type}
          className={cn(
            "flex h-10 w-full rounded-md border px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 transition-colors",
            inputVariants[currentVariant],
            leftIcon && "pl-10",
            (rightIcon || showClearButton || isLoading) && "pr-10",
            className
          )}
          ref={ref}
          value={value}
          onChange={onChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          {...props}
        />

        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
          {isLoading && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
          )}
          
          {showClearButton && hasValue && !isLoading && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-4 w-4 p-0 hover:bg-transparent"
              onClick={handleClear}
            >
              <X className="h-3 w-3" />
            </Button>
          )}
          
          {rightIcon && !isLoading && !(showClearButton && hasValue) && rightIcon}
          
          {error && (
            <AlertCircle className="h-4 w-4 text-red-500" />
          )}
          
          {success && !error && (
            <CheckCircle className="h-4 w-4 text-green-500" />
          )}
        </div>
      </div>
    )
  }
)
Input.displayName = "Input"

const PasswordInput = React.forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ showToggle = true, ...props }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false)

    const togglePasswordVisibility = () => {
      setShowPassword(!showPassword)
    }

    return (
      <Input
        {...props}
        ref={ref}
        type={showPassword ? "text" : "password"}
        rightIcon={
          showToggle ? (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-4 w-4 p-0 hover:bg-transparent"
              onClick={togglePasswordVisibility}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          ) : undefined
        }
      />
    )
  }
)
PasswordInput.displayName = "PasswordInput"

const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProps>(
  ({ onSearch, searchDelay = 300, ...props }, ref) => {
    const [searchValue, setSearchValue] = React.useState(props.value || '')
    const timeoutRef = React.useRef<NodeJS.Timeout | null>(null)

    React.useEffect(() => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }

      timeoutRef.current = setTimeout(() => {
        if (onSearch) {
          onSearch(String(searchValue))
        }
      }, searchDelay)

      return () => {
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current)
        }
      }
    }, [searchValue, onSearch, searchDelay])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setSearchValue(e.target.value)
      if (props.onChange) {
        props.onChange(e)
      }
    }

    return (
      <Input
        {...props}
        ref={ref}
        type="text"
        value={searchValue}
        onChange={handleChange}
        leftIcon={<Search className="h-4 w-4" />}
        showClearButton
        onClear={() => setSearchValue('')}
        placeholder={props.placeholder || "Search..."}
      />
    )
  }
)
SearchInput.displayName = "SearchInput"

const FileInput = React.forwardRef<HTMLInputElement, FileInputProps>(
  ({ 
    accept, 
    multiple, 
    maxSize, 
    onFileSelect, 
    preview, 
    className,
    ...props 
  }, ref) => {
    const [dragActive, setDragActive] = React.useState(false)
    const [selectedFiles, setSelectedFiles] = React.useState<FileList | null>(null)
    const [error, setError] = React.useState<string>('')

    const validateFiles = (files: FileList) => {
      if (maxSize) {
        for (let i = 0; i < files.length; i++) {
          if (files[i].size > maxSize) {
            return `File "${files[i].name}" is too large. Maximum size is ${(maxSize / 1024 / 1024).toFixed(1)}MB`
          }
        }
      }
      return null
    }

    const handleFiles = (files: FileList | null) => {
      if (!files) return

      const validationError = validateFiles(files)
      if (validationError) {
        setError(validationError)
        return
      }

      setError('')
      setSelectedFiles(files)
      if (onFileSelect) {
        onFileSelect(files)
      }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      handleFiles(e.target.files)
      if (props.onChange) {
        props.onChange(e)
      }
    }

    const handleDrag = (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      if (e.type === "dragenter" || e.type === "dragover") {
        setDragActive(true)
      } else if (e.type === "dragleave") {
        setDragActive(false)
      }
    }

    const handleDrop = (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setDragActive(false)
      handleFiles(e.dataTransfer.files)
    }

    return (
      <div
        className={cn(
          "relative border-2 border-dashed rounded-lg p-6 text-center transition-colors",
          dragActive ? "border-blue-500 bg-blue-50 dark:bg-blue-950" : "border-gray-300 dark:border-gray-600",
          error ? "border-red-500 bg-red-50 dark:bg-red-950" : "",
          className
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          {...props}
          ref={ref}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="space-y-2">
          <Upload className="mx-auto h-8 w-8 text-gray-400" />
          <div>
            <p className="text-sm font-medium">
              {dragActive ? "Drop files here" : "Click to upload or drag and drop"}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {accept && `Accepted formats: ${accept}`}
              {maxSize && ` • Max size: ${(maxSize / 1024 / 1024).toFixed(1)}MB`}
            </p>
          </div>
        </div>

        {selectedFiles && selectedFiles.length > 0 && (
          <div className="mt-4 text-left">
            <p className="text-sm font-medium mb-2">Selected files:</p>
            <ul className="text-xs space-y-1">
              {Array.from(selectedFiles).map((file, index) => (
                <li key={index} className="flex justify-between">
                  <span className="truncate">{file.name}</span>
                  <span className="text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(1)}MB
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {error && (
          <div className="mt-2 text-sm text-red-600">
            {error}
          </div>
        )}
      </div>
    )
  }
)
FileInput.displayName = "FileInput"

function FormField({ 
  label, 
  description, 
  error, 
  success, 
  required, 
  children, 
  className 
}: FormFieldProps) {
  const id = React.useId()

  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <Label htmlFor={id} className="flex items-center gap-1">
          {label}
          {required && <span className="text-red-500">*</span>}
        </Label>
      )}
      
      <div className="relative">
        {React.isValidElement(children) ? 
          React.cloneElement(children, { 
            id,
            error: error || undefined,
            success: success || undefined
          } as any) : children}
      </div>
      
      {description && !error && !success && (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {description}
        </p>
      )}
      
      {error && (
        <p className="text-sm text-red-600 flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </p>
      )}
      
      {success && !error && (
        <p className="text-sm text-green-600 flex items-center gap-1">
          <CheckCircle className="h-3 w-3" />
          {success}
        </p>
      )}
    </div>
  )
}

export { 
  Input, 
  PasswordInput, 
  SearchInput, 
  FileInput, 
  FormField,
  type InputProps,
  type PasswordInputProps,
  type SearchInputProps,
  type FileInputProps,
  type FormFieldProps
}