/**
 * Modal JavaScript functionality for contact form
 * Handles modal open/close, form submission, and accessibility features
 */

(function() {
    'use strict';

    // Modal configuration
    const CONFIG = {
        FORM_ENDPOINT: 'https://formspree.io/f/xzzvkzkg',
        SUCCESS_MESSAGE: 'Thank you! Your message has been sent successfully.',
        ERROR_MESSAGE: 'Sorry, there was an error sending your message. Please try again.',
        LOADING_MESSAGE: 'Sending your message...'
    };

    // DOM elements
    const elements = {
        modal: null,
        trigger: null,
        closeButton: null,
        overlay: null,
        form: null,
        submitButton: null,
        statusMessage: null,
        focusableElements: []
    };

    // Modal state
    let isModalOpen = false;
    let lastFocusedElement = null;

    /**
     * Initialize modal functionality
     */
    function init() {
        cacheElements();
        if (!validateElements()) return;
        
        bindEvents();
        setupFocusTrap();
        setupFormValidation();
    }

    /**
     * Cache DOM elements
     */
    function cacheElements() {
        elements.modal = document.getElementById('contact-modal');
        elements.trigger = document.getElementById('contact-trigger');
        elements.closeButton = document.getElementById('modal-close');
        elements.overlay = document.querySelector('.modal-overlay');
        elements.form = document.getElementById('contact-form');
        elements.submitButton = elements.form?.querySelector('button[type="submit"]');
        elements.statusMessage = document.getElementById('form-status');
    }

    /**
     * Validate required elements exist
     */
    function validateElements() {
        const requiredElements = ['modal', 'trigger', 'closeButton', 'form'];
        const missing = requiredElements.filter(key => !elements[key]);
        
        if (missing.length > 0) {
            console.warn('Modal: Missing required elements:', missing);
            return false;
        }
        
        return true;
    }

    /**
     * Bind event listeners
     */
    function bindEvents() {
        // Modal open/close events
        elements.trigger.addEventListener('click', openModal);
        elements.closeButton.addEventListener('click', closeModal);
        
        // Overlay click to close
        if (elements.overlay) {
            elements.overlay.addEventListener('click', handleOverlayClick);
        }
        
        // Escape key to close
        document.addEventListener('keydown', handleKeyDown);
        
        // Form submission
        elements.form.addEventListener('submit', handleFormSubmit);
    }

    /**
     * Setup focus trap
     */
    function setupFocusTrap() {
        const focusableSelectors = [
            'a[href]',
            'button:not([disabled])',
            'textarea:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            '[tabindex]:not([tabindex="-1"])'
        ];
        
        elements.focusableElements = Array.from(
            elements.modal.querySelectorAll(focusableSelectors.join(','))
        ).filter(el => {
            // Ensure element is visible
            return el.offsetParent !== null &&
                   window.getComputedStyle(el).visibility !== 'hidden' &&
                   window.getComputedStyle(el).display !== 'none';
        });
    }

    /**
     * Open modal
     */
    function openModal() {
        if (isModalOpen) return;
        
        lastFocusedElement = document.activeElement;
        isModalOpen = true;
        
        // Show modal
        elements.modal.classList.add('is-open');
        elements.modal.setAttribute('aria-hidden', 'false');
        
        // Focus first focusable element
        const firstFocusable = elements.focusableElements[0];
        if (firstFocusable) {
            firstFocusable.focus();
        }
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Announce to screen readers
        announceToScreenReader('Contact form dialog opened');
    }

    /**
     * Close modal
     */
    function closeModal() {
        if (!isModalOpen) return;
        
        isModalOpen = false;
        
        // Hide modal
        elements.modal.classList.remove('is-open');
        elements.modal.setAttribute('aria-hidden', 'true');
        
        // Return focus to trigger
        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Clear form and status
        elements.form.reset();
        clearStatusMessage();
        
        // Announce to screen readers
        announceToScreenReader('Contact form dialog closed');
    }

    /**
     * Handle overlay click
     */
    function handleOverlayClick(event) {
        if (event.target === elements.overlay) {
            closeModal();
        }
    }

    /**
     * Handle keyboard events
     */
    function handleKeyDown(event) {
        if (!isModalOpen) return;
        
        switch (event.key) {
            case 'Escape':
                event.preventDefault();
                closeModal();
                break;
                
            case 'Tab':
                handleTabKey(event);
                break;
        }
    }

    /**
     * Handle tab key for focus trap
     */
    function handleTabKey(event) {
        const firstFocusable = elements.focusableElements[0];
        const lastFocusable = elements.focusableElements[elements.focusableElements.length - 1];
        
        if (event.shiftKey) {
            // Shift + Tab
            if (document.activeElement === firstFocusable) {
                event.preventDefault();
                lastFocusable.focus();
            }
        } else {
            // Tab
            if (document.activeElement === lastFocusable) {
                event.preventDefault();
                firstFocusable.focus();
            }
        }
    }

    /**
     * Handle form submission
     */
    async function handleFormSubmit(event) {
        event.preventDefault();
        
        // Validate form before submission
        if (!elements.form.checkValidity()) {
            // Trigger browser's built-in validation UI
            elements.form.reportValidity();
            return;
        }
        
        const formData = new FormData(elements.form);
        const submitButton = event.target.querySelector('button[type="submit"]');
        
        // Disable form during submission
        setFormState(false);
        showStatusMessage(CONFIG.LOADING_MESSAGE, 'info');
        
        try {
            const response = await fetch(CONFIG.FORM_ENDPOINT, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                showStatusMessage(CONFIG.SUCCESS_MESSAGE, 'success');
                elements.form.reset();
                
                // Close modal after delay
                setTimeout(() => {
                    closeModal();
                }, 3000);
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Form submission failed');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            showStatusMessage(error.message || CONFIG.ERROR_MESSAGE, 'error');
        } finally {
            // Re-enable form
            setFormState(true);
        }
    }

    /**
     * Set form state (enabled/disabled)
     */
    function setFormState(enabled) {
        const formElements = elements.form.elements;
        for (let element of formElements) {
            element.disabled = !enabled;
        }
        
        if (elements.submitButton) {
            elements.submitButton.disabled = !enabled;
        }
    }

    /**
     * Show status message
     */
    function showStatusMessage(message, type = 'info') {
        if (!elements.statusMessage) return;
        
        elements.statusMessage.textContent = message;
        elements.statusMessage.className = `form-status form-status--${type}`;
        elements.statusMessage.setAttribute('role', 'status');
        elements.statusMessage.setAttribute('aria-live', 'polite');
        
        // Ensure message is visible
        elements.statusMessage.style.display = 'block';
    }

    /**
     * Clear status message
     */
    function clearStatusMessage() {
        if (!elements.statusMessage) return;
        
        elements.statusMessage.textContent = '';
        elements.statusMessage.className = 'form-status';
        elements.statusMessage.style.display = 'none';
    }

    /**
     * Announce message to screen readers
     */
    function announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'assertive');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        
        document.body.appendChild(announcement);
        announcement.textContent = message;
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    /**
     * Handle form field validation
     */
    function setupFormValidation() {
        const inputs = elements.form.querySelectorAll('input[required], textarea[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);
        });
    }

    /**
     * Validate individual field
     */
    function validateField(event) {
        const field = event.target;
        const errorElement = field.parentElement.querySelector('.field-error');
        
        if (!field.validity.valid) {
            const message = field.validationMessage || 'This field is required';
            showFieldError(field, message);
        } else {
            clearFieldError(event);
        }
    }

    /**
     * Show field error
     */
    function showFieldError(field, message) {
        const errorElement = field.parentElement.querySelector('.field-error') || 
                           createErrorElement(field);
        
        errorElement.textContent = message;
        field.setAttribute('aria-invalid', 'true');
        field.setAttribute('aria-describedby', errorElement.id);
    }

    /**
     * Clear field error
     */
    function clearFieldError(event) {
        const field = event.target;
        const errorElement = field.parentElement.querySelector('.field-error');
        
        if (errorElement) {
            errorElement.textContent = '';
        }
        
        field.setAttribute('aria-invalid', 'false');
        field.removeAttribute('aria-describedby');
    }

    /**
     * Create error element for field
     */
    function createErrorElement(field) {
        const errorElement = document.createElement('span');
        errorElement.className = 'field-error';
        errorElement.id = `${field.name}-error`;
        errorElement.setAttribute('role', 'alert');
        errorElement.setAttribute('aria-live', 'polite');
        
        field.parentElement.appendChild(errorElement);
        return errorElement;
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Public API
    window.Modal = {
        open: openModal,
        close: closeModal
    };

})();