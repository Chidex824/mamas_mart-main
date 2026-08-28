window.initializeProductPage = function() {
    // Use event delegation for add product button click handler
    document.body.addEventListener('click', function(e) {
        const target = e.target.closest('.js-add-product, [data-bs-target="#addProductModal"]');
        if (target) {
            e.preventDefault();
            e.stopPropagation();
            const addProductModal = new bootstrap.Modal(document.getElementById('addProductModal'));
            addProductModal.show();
        }
    });

    // Initialize Bootstrap modals
    document.querySelectorAll('.modal').forEach(modalEl => {
        if (!bootstrap.Modal.getInstance(modalEl)) {
            new bootstrap.Modal(modalEl, {
                keyboard: true,
                backdrop: true,
                focus: true
            });
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize product page elements
    initializeProductPage();

    // Initialize forms
    const addProductForm = document.getElementById('addProductForm');
    
    // Initialize add product form handler
    if (addProductForm) {
        addProductForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const submitBtn = this.querySelector('button[type="submit"]');
            const spinner = submitBtn.querySelector('.spinner-border');
            
            // Show loading state
            submitBtn.disabled = true;
            if (spinner) spinner.classList.remove('d-none');
            
            const formData = new FormData(this);
            fetch(addProductForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close modal and reset form
                    const modal = bootstrap.Modal.getInstance(addProductModal);
                    modal.hide();
                    this.reset();
                    
                    // Update product table
                    updateProductTable();
                    
                    // Show success message
                    showAlert('success', 'Product added successfully!');
                } else {
                    showAlert('danger', data.error || 'Error adding product');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'Error adding product');
            })
            .finally(() => {
                // Reset button state
                submitBtn.disabled = false;
                if (spinner) spinner.classList.add('d-none');
            });
        });
    }

    // Filter click handlers
    document.querySelectorAll('.product-nav-item').forEach(item => {
        if (item.getAttribute('data-bs-toggle') === 'modal') {
            return; // Skip modal triggers
        }

        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active state
            document.querySelectorAll('.product-nav-item').forEach(i => {
                i.classList.remove('active');
            });
            this.classList.add('active');

            // Get filter type
            const filterType = this.getAttribute('data-filter');
            updateProductTable(filterType);
        });
    });

    // Search input handler with debounce
    const searchInput = document.getElementById('productSearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            updateProductTable();
        }, 300));
    }

    // Pagination click handlers
    document.addEventListener('click', function(e) {
        if (e.target.matches('.page-link')) {
            e.preventDefault();
            const page = e.target.getAttribute('data-page');
            if (page) {
                updateProductTable(null, page);
            }
        }
    });

    // Product edit handler
    window.editProduct = function(productId) {
        fetch(`${productId}/edit/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            // Populate edit modal with product data
            document.getElementById('editProductId').value = data.id;
            document.getElementById('editName').value = data.name;
            document.getElementById('editCategory').value = data.category;
            document.getElementById('editPrice').value = data.price;
            document.getElementById('editStock').value = data.stock;
            document.getElementById('editDescription').value = data.description;
            document.getElementById('editIsAvailable').checked = data.is_available;
            
            // Show current image if exists
            const currentImageContainer = document.getElementById('currentImage');
            if (data.image_url) {
                currentImageContainer.innerHTML = `<img src="${data.image_url}" alt="Current image" class="img-thumbnail" style="height: 100px;">`;
            } else {
                currentImageContainer.innerHTML = '<p class="text-muted">No image uploaded</p>';
            }

            // Show the modal
            const editModal = new bootstrap.Modal(document.getElementById('editProductModal'));
            editModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading product data');
        });
    };

    // Product delete handler
    window.deleteProduct = function(productId) {
        if (confirm('Are you sure you want to delete this product?')) {
            const row = document.querySelector(`tr[data-product-id="${productId}"]`);
            if (row) {
                row.classList.add('fade-out-row');
            }

            fetch(`${productId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    setTimeout(() => updateProductTable(), 300); // Wait for animation to finish
                } else {
                    if (row) row.classList.remove('fade-out-row');
                    showAlert('danger', 'Error deleting product: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (row) row.classList.remove('fade-out-row');
                showAlert('danger', 'Error deleting product');
            });
        }
    };
});

// Helper function to show alerts
function showAlert(type, message) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    const alertContainer = document.querySelector('.alert-container') || createAlertContainer();
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alerts = alertContainer.querySelectorAll('.alert');
        if (alerts.length) {
            alerts[0].remove();
        }
    }, 5000);
}

// Helper function to create alert container
function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container position-fixed end-0 p-3';
    container.style.cssText = 'z-index: 1050; top: 70px; max-width: 350px;';
    document.body.appendChild(container);
    return container;
}

// Helper function to update product table
function updateProductTable(filterType = null, page = null) {
    const searchQuery = document.getElementById('productSearch')?.value || '';
    const params = new URLSearchParams();

    // Add search query if exists
    if (searchQuery) {
        params.set('search', searchQuery);
    }

    // Add filter if exists
    if (filterType) {
        params.set(filterType, filterType);
    }

    // Add page number if exists
    if (page) {
        params.set('page', page);
    }

    // Show loading state
    const tableContainer = document.querySelector('.card-body');
    tableContainer.innerHTML = 
        '<div class="text-center p-5"><div class="spinner-border" role="status">' +
        '<span class="visually-hidden">Loading...</span></div></div>';

    // Fetch updated table content
    fetch(`?${params.toString()}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(html => {
        tableContainer.innerHTML = html;
        
        // Re-initialize modals for new content
        document.querySelectorAll('.modal').forEach(modalEl => {
            if (!bootstrap.Modal.getInstance(modalEl)) {
                new bootstrap.Modal(modalEl);
            }
        });

        // Re-attach event handlers
        initializeProductForms();
    })
    .catch(error => {
        console.error('Error:', error);
        tableContainer.innerHTML = '<div class="alert alert-danger">Error loading products</div>';
        showAlert('danger', 'Error loading products: ' + error.message);
    });
}

// Debounce helper function
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Initialize product page
function initializeProductPage() {
    // Initialize Bootstrap modals
    document.querySelectorAll('.modal').forEach(modalEl => {
        if (!bootstrap.Modal.getInstance(modalEl)) {
            new bootstrap.Modal(modalEl, {
                keyboard: true,
                backdrop: true,
                focus: true
            });
        }
    });

    // Add click handler for add product button
    document.querySelectorAll('[data-bs-target="#addProductModal"]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('addProductModal'));
            modal.show();
        });
    });

    // Initialize product form handlers
    initializeProductForms();
}

// Initialize product forms
function initializeProductForms() {
    const addProductForm = document.getElementById('addProductForm');
    const editProductForm = document.getElementById('editProductForm');

    // Form validation function
    function validateForm(form) {
        let isValid = true;
        form.querySelectorAll('input[required], select[required], textarea[required]').forEach(field => {
            field.classList.remove('is-invalid', 'is-valid');
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
                const feedback = field.nextElementSibling || document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = 'This field is required';
                if (!field.nextElementSibling) {
                    field.parentNode.appendChild(feedback);
                }
            } else {
                field.classList.add('is-valid');
            }
        });
        return isValid;
    }

    // File input validation and preview
    function initFileInput(form) {
        const fileInput = form.querySelector('input[type="file"]');
        if (!fileInput) return;

        fileInput.addEventListener('change', function(e) {
            const file = this.files[0];
            const previewContainer = this.closest('.form-group').querySelector('.image-preview');
            
            // Reset validation state
            this.classList.remove('is-invalid', 'is-valid');
            
            if (file) {
                // Validate file type
                const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    this.classList.add('is-invalid');
                    const feedback = this.nextElementSibling || document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'Please select a valid image file (JPEG, PNG, GIF)';
                    if (!this.nextElementSibling) {
                        this.parentNode.appendChild(feedback);
                    }
                    return;
                }

                // Validate file size (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    this.classList.add('is-invalid');
                    const feedback = this.nextElementSibling || document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'File size must be less than 5MB';
                    if (!this.nextElementSibling) {
                        this.parentNode.appendChild(feedback);
                    }
                    return;
                }

                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (previewContainer) {
                        previewContainer.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="height: 100px;">`;
                    }
                };
                reader.readAsDataURL(file);
                this.classList.add('is-valid');
            } else if (previewContainer) {
                previewContainer.innerHTML = '<p class="text-muted">No image selected</p>';
            }
        });
    }

    if (addProductForm) {
        addProductForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!validateForm(this)) return;
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const spinner = submitBtn.querySelector('.spinner-border');
            const errorContainer = document.getElementById('addProductError');
            
            // Reset error state
            errorContainer.classList.add('d-none');
            errorContainer.textContent = '';
            
            // Show loading state
            submitBtn.disabled = true;
            spinner.classList.remove('d-none');
            
            const formData = new FormData(this);
            
            fetch(addProductForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json().then(data => ({ status: response.status, data })))
            .then(({ status, data }) => {
                if (data.success) {
                    // Close modal and reset form
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addProductModal'));
                    modal.hide();
                    this.reset();
                    
                    // Update product table
                    updateProductTable();
                    
                    // Show success message
                    showAlert('success', 'Product added successfully!');
                } else {
                    // Show error in modal and as alert
                    errorContainer.textContent = data.error || 'Error adding product';
                    errorContainer.classList.remove('d-none');
                    showAlert('danger', data.error || 'Error adding product');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'Error adding product');
            })
            .finally(() => {
                // Reset button state
                submitBtn.disabled = false;
                spinner.classList.add('d-none');
            });
        });
    }

    if (editProductForm) {
        editProductForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!validateForm(this)) return;

            const submitBtn = this.querySelector('button[type="submit"]');
            const spinner = submitBtn.querySelector('.spinner-border');
            
            // Show loading state
            submitBtn.disabled = true;
            spinner.classList.remove('d-none');
            
            const formData = new FormData(this);
            const productId = this.querySelector('#editProductId').value;
            
            fetch(`${productId}/edit/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editProductModal'));
                    modal.hide();
                    
                    // Update product table
                    updateProductTable();
                    
                    // Show success message
                    showAlert('success', 'Product updated successfully!');
                } else {
                    showAlert('danger', data.error || 'Error updating product');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'Error updating product');
            })
            .finally(() => {
                // Reset button state
                submitBtn.disabled = false;
                spinner.classList.add('d-none');
            });
        });
    }

    // Initialize file inputs for both forms
    if (addProductForm) initFileInput(addProductForm);
    if (editProductForm) initFileInput(editProductForm);

    // Handle image preview
    document.querySelectorAll('input[type="file"][accept="image/*"]').forEach(input => {
        input.addEventListener('change', function() {
            const preview = this.parentElement.querySelector('.image-preview');
            const img = preview.querySelector('img');
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    img.src = e.target.result;
                    preview.style.display = 'block';
                }
                reader.readAsDataURL(this.files[0]);
            } else {
                preview.style.display = 'none';
            }
        });
    });
}

// Handle form submission
function submitProductForm(form, action) {
    const formData = new FormData(form);
    const url = action === 'add' ? '' : formData.get('product_id') + '/edit/';

    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(form.closest('.modal'));
            modal.hide();
            
            // Reset form
            form.reset();
            
            // Update table
            updateProductTable();
        } else {
            alert('Error: ' + (data.error || 'Unknown error occurred'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error submitting form');
    });
}
