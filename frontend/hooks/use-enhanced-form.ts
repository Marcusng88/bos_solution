"use client"

import React from 'react'
import { z } from 'zod'

// Types
interface ValidationRule<T = any> {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: T) => string | null
  asyncValidator?: (value: T) => Promise<string | null>
}

interface FieldConfig<T = any> {
  defaultValue?: T
  validation?: ValidationRule<T>
  transform?: (value: any) => T
  debounceMs?: number
}

interface FormConfig<T extends Record<string, any>> {
  fields: {
    [K in keyof T]: FieldConfig<T[K]>
  }
  onSubmit?: (data: T) => Promise<void> | void
  onValidationChange?: (isValid: boolean, errors: Partial<Record<keyof T, string>>) => void
  validateOnChange?: boolean
  validateOnBlur?: boolean
  resetOnSubmit?: boolean
}

interface FieldState<T = any> {
  value: T
  error: string | null
  touched: boolean
  dirty: boolean
  validating: boolean
}

interface FormState<T extends Record<string, any>> {
  fields: {
    [K in keyof T]: FieldState<T[K]>
  }
  isValid: boolean
  isDirty: boolean
  isSubmitting: boolean
  submitCount: number
  errors: Partial<Record<keyof T, string>>
}

// Validation helpers
const validateField = async <T,>(
  value: T,
  validation?: ValidationRule<T>
): Promise<string | null> => {
  if (!validation) return null

  // Required validation
  if (validation.required && (value === null || value === undefined || value === '')) {
    return 'This field is required'
  }

  // Skip other validations if field is empty and not required
  if (!validation.required && (value === null || value === undefined || value === '')) {
    return null
  }

  // String-specific validations
  if (typeof value === 'string') {
    if (validation.minLength && value.length < validation.minLength) {
      return `Minimum length is ${validation.minLength} characters`
    }
    
    if (validation.maxLength && value.length > validation.maxLength) {
      return `Maximum length is ${validation.maxLength} characters`
    }
    
    if (validation.pattern && !validation.pattern.test(value)) {
      return 'Invalid format'
    }
  }

  // Custom validation
  if (validation.custom) {
    const customError = validation.custom(value)
    if (customError) return customError
  }

  // Async validation
  if (validation.asyncValidator) {
    try {
      const asyncError = await validation.asyncValidator(value)
      if (asyncError) return asyncError
    } catch (error) {
      return 'Validation failed'
    }
  }

  return null
}

// Zod integration helper
export function createZodFormConfig<T extends Record<string, any>>(
  schema: z.ZodSchema<T>,
  options?: {
    onSubmit?: (data: T) => Promise<void> | void
    onValidationChange?: (isValid: boolean, errors: Partial<Record<keyof T, string>>) => void
    validateOnChange?: boolean
    validateOnBlur?: boolean
    resetOnSubmit?: boolean
  }
): Omit<FormConfig<T>, 'fields'> {
  return {
    onSubmit: options?.onSubmit,
    onValidationChange: options?.onValidationChange,
    validateOnChange: options?.validateOnChange ?? true,
    validateOnBlur: options?.validateOnBlur ?? true,
    resetOnSubmit: options?.resetOnSubmit ?? false
  }
}

// Main hook
export function useEnhancedForm<T extends Record<string, any>>(
  config: FormConfig<T>
) {
  const [formState, setFormState] = React.useState<FormState<T>>(() => {
    const initialFields = {} as FormState<T>['fields']
    
    for (const [fieldName, fieldConfig] of Object.entries(config.fields)) {
      initialFields[fieldName as keyof T] = {
        value: fieldConfig.defaultValue ?? '',
        error: null,
        touched: false,
        dirty: false,
        validating: false
      }
    }

    return {
      fields: initialFields,
      isValid: true,
      isDirty: false,
      isSubmitting: false,
      submitCount: 0,
      errors: {}
    }
  })

  const timeoutsRef = React.useRef<Record<string, NodeJS.Timeout>>({})

  // Validate single field
  const validateFieldAsync = React.useCallback(async (
    fieldName: keyof T,
    value: any
  ) => {
    const fieldConfig = config.fields[fieldName]
    if (!fieldConfig) return null

    setFormState(prev => ({
      ...prev,
      fields: {
        ...prev.fields,
        [fieldName]: {
          ...prev.fields[fieldName],
          validating: true
        }
      }
    }))

    try {
      const error = await validateField(value, fieldConfig.validation)
      
      setFormState(prev => {
        const newErrors = { ...prev.errors }
        if (error) {
          newErrors[fieldName] = error
        } else {
          delete newErrors[fieldName]
        }

        const isValid = Object.keys(newErrors).length === 0
        
        const newState = {
          ...prev,
          fields: {
            ...prev.fields,
            [fieldName]: {
              ...prev.fields[fieldName],
              error,
              validating: false
            }
          },
          errors: newErrors,
          isValid
        }

        // Call validation change callback
        if (config.onValidationChange) {
          config.onValidationChange(isValid, newErrors)
        }

        return newState
      })

      return error
    } catch (error) {
      setFormState(prev => ({
        ...prev,
        fields: {
          ...prev.fields,
          [fieldName]: {
            ...prev.fields[fieldName],
            validating: false,
            error: 'Validation failed'
          }
        }
      }))
      return 'Validation failed'
    }
  }, [config])

  // Set field value
  const setValue = React.useCallback((
    fieldName: keyof T,
    value: any,
    options?: { validate?: boolean; touch?: boolean }
  ) => {
    const fieldConfig = config.fields[fieldName]
    const transformedValue = fieldConfig?.transform ? fieldConfig.transform(value) : value
    const shouldValidate = options?.validate ?? config.validateOnChange ?? true
    const shouldTouch = options?.touch ?? true

    setFormState(prev => {
      const newFieldState = {
        ...prev.fields[fieldName],
        value: transformedValue,
        dirty: true,
        ...(shouldTouch && { touched: true })
      }

      return {
        ...prev,
        fields: {
          ...prev.fields,
          [fieldName]: newFieldState
        },
        isDirty: true
      }
    })

    // Debounced validation
    if (shouldValidate) {
      const debounceMs = fieldConfig?.debounceMs ?? 300
      
      if (timeoutsRef.current[fieldName as string]) {
        clearTimeout(timeoutsRef.current[fieldName as string])
      }

      timeoutsRef.current[fieldName as string] = setTimeout(() => {
        validateFieldAsync(fieldName, transformedValue)
      }, debounceMs)
    }
  }, [config, validateFieldAsync])

  // Touch field
  const setTouched = React.useCallback((fieldName: keyof T, touched = true) => {
    setFormState(prev => ({
      ...prev,
      fields: {
        ...prev.fields,
        [fieldName]: {
          ...prev.fields[fieldName],
          touched
        }
      }
    }))

    // Validate on blur if configured
    if (touched && config.validateOnBlur) {
      const value = formState.fields[fieldName].value
      validateFieldAsync(fieldName, value)
    }
  }, [config.validateOnBlur, formState.fields, validateFieldAsync])

  // Get field helpers
  const getFieldProps = React.useCallback((fieldName: keyof T) => {
    const field = formState.fields[fieldName]
    
    return {
      name: fieldName as string,
      value: field.value,
      error: field.touched ? field.error : null,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        setValue(fieldName, e.target.value)
      },
      onBlur: () => {
        setTouched(fieldName, true)
      }
    }
  }, [formState.fields, setValue, setTouched])

  // Validate all fields
  const validateAll = React.useCallback(async () => {
    const validationPromises = Object.keys(config.fields).map(async (fieldName) => {
      const value = formState.fields[fieldName as keyof T].value
      return validateFieldAsync(fieldName as keyof T, value)
    })

    const results = await Promise.all(validationPromises)
    return results.every(result => result === null)
  }, [config.fields, formState.fields, validateFieldAsync])

  // Submit form
  const handleSubmit = React.useCallback(async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault()
    }

    setFormState(prev => ({
      ...prev,
      isSubmitting: true,
      submitCount: prev.submitCount + 1
    }))

    try {
      // Touch all fields
      setFormState(prev => {
        const newFields = { ...prev.fields }
        for (const fieldName of Object.keys(newFields)) {
          newFields[fieldName as keyof T] = {
            ...newFields[fieldName as keyof T],
            touched: true
          }
        }
        return {
          ...prev,
          fields: newFields
        }
      })

      // Validate all fields
      const isValid = await validateAll()
      
      if (!isValid) {
        setFormState(prev => ({ ...prev, isSubmitting: false }))
        return false
      }

      // Submit data
      if (config.onSubmit) {
        const data = {} as T
        for (const [fieldName, field] of Object.entries(formState.fields)) {
          data[fieldName as keyof T] = field.value
        }
        
        await config.onSubmit(data)
      }

      // Reset form if configured
      if (config.resetOnSubmit) {
        reset()
      }

      setFormState(prev => ({ ...prev, isSubmitting: false }))
      return true
    } catch (error) {
      setFormState(prev => ({ ...prev, isSubmitting: false }))
      console.error('Form submission error:', error)
      return false
    }
  }, [config, formState.fields, validateAll])

  // Reset form
  const reset = React.useCallback(() => {
    setFormState(prev => {
      const resetFields = {} as FormState<T>['fields']
      
      for (const [fieldName, fieldConfig] of Object.entries(config.fields)) {
        resetFields[fieldName as keyof T] = {
          value: fieldConfig.defaultValue ?? '',
          error: null,
          touched: false,
          dirty: false,
          validating: false
        }
      }

      return {
        fields: resetFields,
        isValid: true,
        isDirty: false,
        isSubmitting: false,
        submitCount: 0,
        errors: {}
      }
    })

    // Clear all timeouts
    Object.values(timeoutsRef.current).forEach(timeout => {
      if (timeout) clearTimeout(timeout)
    })
    timeoutsRef.current = {}
  }, [config.fields])

  // Cleanup timeouts on unmount
  React.useEffect(() => {
    return () => {
      Object.values(timeoutsRef.current).forEach(timeout => {
        if (timeout) clearTimeout(timeout)
      })
    }
  }, [])

  return {
    // State
    fields: formState.fields,
    isValid: formState.isValid,
    isDirty: formState.isDirty,
    isSubmitting: formState.isSubmitting,
    submitCount: formState.submitCount,
    errors: formState.errors,

    // Actions
    setValue,
    setTouched,
    validateField: validateFieldAsync,
    validateAll,
    handleSubmit,
    reset,
    getFieldProps
  }
}

// Pre-built validation rules
export const ValidationRules = {
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    custom: (value: string) => {
      if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        return 'Please enter a valid email address'
      }
      return null
    }
  },
  
  password: {
    minLength: 8,
    custom: (value: string) => {
      if (value.length < 8) return 'Password must be at least 8 characters'
      if (!/(?=.*[a-z])/.test(value)) return 'Password must contain at least one lowercase letter'
      if (!/(?=.*[A-Z])/.test(value)) return 'Password must contain at least one uppercase letter'
      if (!/(?=.*\d)/.test(value)) return 'Password must contain at least one number'
      return null
    }
  },
  
  url: {
    pattern: /^https?:\/\/\S+$/,
    custom: (value: string) => {
      if (value && !/^https?:\/\/\S+$/.test(value)) {
        return 'Please enter a valid URL'
      }
      return null
    }
  },
  
  phoneNumber: {
    pattern: /^\+?[\d\s\-\(\)]+$/,
    custom: (value: string) => {
      if (value && !/^\+?[\d\s\-\(\)]+$/.test(value)) {
        return 'Please enter a valid phone number'
      }
      return null
    }
  }
}

export default useEnhancedForm