# Changelog & Implementation Record (change.md)

## Summary of Changes

This document records all architectural updates, model additions, view refactorings, and template enhancements applied to **Mama's Mart Inventory & Store Management System**.

---

## 1. Database & Models (`accounts/models.py`)

- **Notification Model**:
  - Added `Notification` model to store system notifications, stock alerts, and staff updates.
  - Fields: `recipient` (FK User, null=True for broadcast), `title`, `message`, `notification_type` (`info`, `warning`, `danger`, `success`), `link`, `is_read`, `created_at`.
- **InternalMessage Model**:
  - Added `InternalMessage` model for private staff-to-staff and admin-to-staff messaging.
  - Fields: `sender` (FK User), `recipient` (FK User, null=True for broadcast), `subject`, `body`, `is_read`, `created_at`.
- **Database Migrations**:
  - Generated and applied migration `accounts/migrations/0005_internalmessage_notification.py`.

---

## 2. Authentication System (`accounts/templates/accounts/` & `accounts/views.py`)

### Login Page (`accounts/templates/accounts/login.html`)
- **Centered Square Card Layout**: Fixed layout inheritance to ensure 100% viewport centering with ambient gradient backdrop and glassmorphism styling.
- **Role Switcher**: Added an interactive segmented role control (**Staff Login** | **Admin Login**) with live role expectation hints.
- **Password Visibility Toggle**: Integrated a show/hide eye toggle button.
- **Stray Database Text Removal**: Cleaned up stray database connection text present on line 1.

### Registration Page (`accounts/templates/accounts/register.html`)
- **Restricted Registration Access**: Non-admin users visiting `/register/` see an "Admin Only Access" notice explaining that credentials must be issued by an administrator.
- **Admin Registration Portal**: The page is prominently titled and styled as **Admin Registration**, allowing logged-in administrators (and initial superuser setup) to register users, assign custom roles (**Administrator**, **Manager**, **Staff**, **Cashier**), and set initial passwords.

### Authentication Views (`accounts/views.py`)
- Refactored `login_view` to validate role selections and provide clear feedback.
- Refactored `register` view to enforce admin-only checks (`request.user.is_superuser` or `request.user.is_staff`) and allow explicit initial password setting.

---

## 3. User Management & Admin Database Integration

### Web UI User Management (`accounts/templates/accounts/user_management.html`)
- **AJAX Endpoints**: Refactored `user_add`, `user_edit`, and `user_delete` in `accounts/views.py` to return JSON responses for modal interactions.
- **Add / Edit Modals**: Bound fields for Username, First & Last Name, Email, Phone Number, Role, Active Status, and Password updates.
- **Admin Database Button**: Added an **"Open Admin Database"** button linking directly to `/admin/accounts/user/`.

### Django Admin Registration (`accounts/admin.py`)
- Registered `CustomUserAdmin` with custom `AdminUserCreationForm` and `add_fieldsets` so administrators can create and manage users directly inside `/admin/` without validation errors.
- Registered `Notification` and `InternalMessage` models in Django Admin.

---

## 4. Product Page Enhancements (`products/`)

- **Header Add Button**: Added a prominent `+ Add Product` button in the main header of `products/templates/products/product_list.html`.
- **JS Modal Fix**: Fixed modal instance retrieval in `static/js/product.js` (`bootstrap.Modal.getOrCreateInstance`) to prevent modal lockups on submit.

---

## 5. Inventory System Updates (`inventory/`)

- **AJAX Validation & Response**: Updated `add_inventory` in `inventory/views.py` to handle both AJAX modal submissions returning JSON responses and regular form posts.

---

## 6. User Profile Dashboard (`accounts/templates/accounts/profile.html`)

- **Dedicated Profile Route**: Created `profile_view` in `accounts/views.py` and route `path('profile/', views.profile_view, name='profile')`.
- **Header Link**: Updated top header profile avatar/name to link directly to `{% url 'accounts:profile' %}`.
- **Profile Dashboard Features**:
  - Profile details overview (Avatar, Full Name, Role Badge, Department, Email, Phone, Date Joined, Status).
  - Profile Info edit form (Name, Email, Phone, Address, Profile Picture upload).
  - Security & Password change form.
  - Admin shortcuts for User Management and Django Admin database.

---

## 7. Independent Notifications & Staff Messaging Systems

- **Context Processor (`accounts/context_processors.py`)**: Added `header_context` context processor to inject unread notification and message counts into all templates via `TEMPLATES['OPTIONS']['context_processors']` in `settings.py`.
- **Header Dropdowns (`main/templates/main/base.html`)**:
  - Replaced static settings redirects with interactive Bootstrap dropdowns for recent notifications and staff messages.
  - Added unread badge counters.
- **Notification Center (`accounts/templates/accounts/notifications.html`)**: Dedicated view with "Mark All as Read" and type-based badges.
- **Staff Messaging Center (`accounts/templates/accounts/messages.html`)**: Dedicated view with Inbox, Sent Messages, and "Compose Message" modal.

---

## 8. Base Layout & Global Helpers (`main/templates/main/base.html`)

- **Full-Viewport Auth Wrapper**: Defined `.auth-layout` CSS rules to prevent sidebar margins from displacing login and registration screens.
- **Global Toast Alerts**: Added `window.showAlert(type, message)` helper function in `base.html` available across all pages.
- **Sidebar Navigation**: Added Profile, Notifications, and Messages items to `main/templates/main/includes/navigation.html`.

---

## Verified File Matrix

| File Path | Description of Change |
| :--- | :--- |
| [`accounts/models.py`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/models.py) | Added `Notification` and `InternalMessage` models |
| [`accounts/views.py`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/views.py) | Refactored auth, user management, added `profile_view`, `notifications_view`, `messages_view` |
| [`accounts/urls.py`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/urls.py) | Added routes for `profile/`, `notifications/`, `messages/` |
| [`accounts/context_processors.py`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/context_processors.py) | Context processor for header notifications/messages |
| [`accounts/admin.py`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/admin.py) | Custom admin forms and model registrations |
| [`accounts/templates/accounts/login.html`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/templates/accounts/login.html) | Square centered card layout with role switcher & eye toggle |
| [`accounts/templates/accounts/register.html`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/templates/accounts/register.html) | Restricted registration card with admin portal |
| [`accounts/templates/accounts/user_management.html`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/templates/accounts/user_management.html) | User management UI with modals & Admin Database button |
| [`accounts/templates/accounts/profile.html`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/templates/accounts/profile.html) | Dedicated profile dashboard template |
| [`accounts/templates/accounts/notifications.html`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/templates/accounts/notifications.html) | Notification center template |
| [`accounts/templates/accounts/messages.html`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/accounts/templates/accounts/messages.html) | Staff messaging center template |
| [`main/templates/main/base.html`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/main/templates/main/base.html) | Header dropdowns, auth layout CSS, global `showAlert` |
| [`main/templates/main/includes/navigation.html`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/main/templates/main/includes/navigation.html) | Added Profile, Notifications, Messages links |
| [`products/templates/products/product_list.html`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/products/templates/products/product_list.html) | Added `+ Add Product` button in header |
| [`static/js/product.js`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/static/js/product.js) | Fixed modal instance handling |
| [`inventory/views.py`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/inventory/views.py) | Updated `add_inventory` with AJAX response handling |
| [`mamas_mart/settings.py`](file:///c:/Users/chide/OneDrive/Desktop/mamas_mart-main/mamas_mart-main/mamas_mart/settings.py) | Added header context processor |
