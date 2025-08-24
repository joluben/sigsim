import { useCallback, useState } from 'react';

// Custom hook for form validation
export const useFormValidation = (initialValues = {}, validationRules = {}) => {
    const [values, setValues] = useState(initialValues);
    const [errors, setErrors] = useState({});
    const [touched, setTouched] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Validate a single field
    const validateField = useCallback((name, value) => {
        const rules = validationRules[name];
        if (!rules) return null;

        for (const rule of rules) {
            const error = rule(value, values);
            if (error) return error;
        }
        return null;
    }, [validationRules, values]);

    // Validate all fields
    const validateForm = useCallback(() => {
        const newErrors = {};
        let isValid = true;

        Object.keys(validationRules).forEach(fieldName => {
            const error = validateField(fieldName, values[fieldName]);
            if (error) {
                newErrors[fieldName] = error;
                isValid = false;
            }
        });

        setErrors(newErrors);
        return isValid;
    }, [validationRules, values, validateField]);

    // Handle input change
    const handleChange = useCallback((name, value) => {
        setValues(prev => ({ ...prev, [name]: value }));

        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: null }));
        }
    }, [errors]);

    // Handle input blur
    const handleBlur = useCallback((name) => {
        setTouched(prev => ({ ...prev, [name]: true }));

        // Validate field on blur
        const error = validateField(name, values[name]);
        setErrors(prev => ({ ...prev, [name]: error }));
    }, [validateField, values]);

    // Handle form submission
    const handleSubmit = useCallback(async (onSubmit) => {
        setIsSubmitting(true);

        // Mark all fields as touched
        const allTouched = Object.keys(validationRules).reduce((acc, key) => {
            acc[key] = true;
            return acc;
        }, {});
        setTouched(allTouched);

        // Validate form
        const isValid = validateForm();

        if (isValid) {
            try {
                await onSubmit(values);
            } catch (error) {
                console.error('Form submission error:', error);
            }
        }

        setIsSubmitting(false);
        return isValid;
    }, [values, validationRules, validateForm]);

    // Reset form
    const resetForm = useCallback(() => {
        setValues(initialValues);
        setErrors({});
        setTouched({});
        setIsSubmitting(false);
    }, [initialValues]);

    // Set form values (useful for editing)
    const setFormValues = useCallback((newValues) => {
        setValues(newValues);
        setErrors({});
        setTouched({});
    }, []);

    // Calculate if form is valid
    const isValid = useCallback(() => {
        // Check if there are any errors
        const hasErrors = Object.values(errors).some(error => error !== null && error !== undefined);
        if (hasErrors) return false;

        // Check if all required fields are filled
        for (const [fieldName, rules] of Object.entries(validationRules)) {
            const hasRequiredRule = rules.some(rule => rule === validationRules.required);
            if (hasRequiredRule) {
                const value = values[fieldName];
                if (!value || (typeof value === 'string' && value.trim() === '')) {
                    return false;
                }
            }
        }

        return true;
    }, [errors, values, validationRules]);

    return {
        values,
        errors,
        touched,
        isSubmitting,
        handleChange,
        handleBlur,
        handleSubmit,
        resetForm,
        setFormValues,
        validateForm,
        isValid: isValid(),
    };
};

// Common validation rules
export const validationRules = {
    required: (value) => {
        if (!value || (typeof value === 'string' && value.trim() === '')) {
            return 'This field is required';
        }
        return null;
    },

    minLength: (min) => (value) => {
        if (value && value.length < min) {
            return `Must be at least ${min} characters`;
        }
        return null;
    },

    maxLength: (max) => (value) => {
        if (value && value.length > max) {
            return `Must be no more than ${max} characters`;
        }
        return null;
    },

    email: (value) => {
        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            return 'Please enter a valid email address';
        }
        return null;
    },

    url: (value) => {
        if (value && !/^https?:\/\/.+/.test(value)) {
            return 'Please enter a valid URL';
        }
        return null;
    },

    number: (value) => {
        if (value && isNaN(Number(value))) {
            return 'Please enter a valid number';
        }
        return null;
    },

    positiveNumber: (value) => {
        if (value && (isNaN(Number(value)) || Number(value) <= 0)) {
            return 'Please enter a positive number';
        }
        return null;
    },

    integer: (value) => {
        if (value && (!Number.isInteger(Number(value)))) {
            return 'Please enter a whole number';
        }
        return null;
    },

    range: (min, max) => (value) => {
        const num = Number(value);
        if (value && (!isNaN(num) && (num < min || num > max))) {
            return `Value must be between ${min} and ${max}`;
        }
        return null;
    },

    json: (value) => {
        if (value) {
            try {
                JSON.parse(value);
            } catch {
                return 'Please enter valid JSON';
            }
        }
        return null;
    },
};