// Handle form submission
function handleFormSubmission(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
    } else {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Signing in...';
    }
    form.classList.add('was-validated');
}

// Function to toggle password visibility
function togglePasswordVisibility(inputId, buttonId) {
    const input = document.getElementById(inputId);
    const button = document.getElementById(buttonId);
    
    if (button) {
        button.addEventListener('click', function() {
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            // Toggle icon
            const icon = this.querySelector('i');
            if (type === 'password') {
                icon.classList.remove('ti-eye-off');
                icon.classList.add('ti-eye');
            } else {
                icon.classList.remove('ti-eye');
                icon.classList.add('ti-eye-off');
            }
        });
    }
}

// Function to check password strength
function checkPasswordStrength(password) {
    let strength = 0;
    const feedback = document.getElementById('passwordStrength');
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[!@#$%^&*(),.?":{}|<>]+/)) strength++;
    
    switch(strength) {
        case 0:
        case 1:
            feedback.className = 'form-text text-danger';
            feedback.textContent = 'Very weak password';
            break;
        case 2:
            feedback.className = 'form-text text-warning';
            feedback.textContent = 'Weak password';
            break;
        case 3:
            feedback.className = 'form-text text-info';
            feedback.textContent = 'Medium strength password';
            break;
        case 4:
            feedback.className = 'form-text text-success';
            feedback.textContent = 'Strong password';
            break;
        case 5:
            feedback.className = 'form-text text-success';
            feedback.textContent = 'Very strong password';
            break;
    }
}

// Function to check if passwords match
function checkPasswordMatch() {
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    const feedback = document.getElementById('passwordMatch');
    
    if (password2.value === '') {
        feedback.className = 'form-text';
        feedback.textContent = '';
    } else if (password1.value === password2.value) {
        feedback.className = 'form-text text-success';
        feedback.textContent = 'Passwords match';
    } else {
        feedback.className = 'form-text text-danger';
        feedback.textContent = 'Passwords do not match';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Setup password toggles
    togglePasswordVisibility('id_password', 'togglePassword');
    togglePasswordVisibility('id_password1', 'togglePassword1');
    togglePasswordVisibility('id_password2', 'togglePassword2');
    
    // Setup password strength checking
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    
    if (password1) {
        password1.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
    }
    
    if (password2) {
        password2.addEventListener('input', checkPasswordMatch);
    }
    
    // Form validation and submission handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmission);
        
        // Add input event listeners for real-time validation
        const inputs = form.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                if (this.value.trim()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
});
