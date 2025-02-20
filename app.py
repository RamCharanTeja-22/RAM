from flask import Flask, request, jsonify, render_template_string, redirect, url_for, flash, session,send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import jwt
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.config.update(
    SECRET_KEY='your-secret-key-here',
    SQLALCHEMY_DATABASE_URI='sqlite:///edutrade.db',
    UPLOAD_FOLDER='static/uploads',
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='ramcharancai22@gmail.com',  # Update with your email
    MAIL_PASSWORD='zolt ahoa jxin isio'      # Update with your app password
)

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)
    profile_picture = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100))
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    listings = db.relationship('Listing', backref='seller', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    rent_price = db.Column(db.Float)
    category = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    is_for_rent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # New fields
    product_type = db.Column(db.String(50))  # Mobile, laptop, books, etc.
    branch = db.Column(db.String(50))        # CSE, etc.
    study_year = db.Column(db.String(20))    # 2nd year, etc.
    working_condition = db.Column(db.String(50))  # Fully functional, etc.
    warranty_status = db.Column(db.String(50))    # Yes/No
    subject = db.Column(db.String(100))      # For books
    is_fake_warning = db.Column(db.Boolean, default=False)
def save_image(image):
    if not image:
        return None
    filename = secure_filename(image.filename)
    # Generate unique filename to prevent overwrites
    unique_filename = f"{uuid.uuid4()}_{filename}"
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    image.save(image_path)
    return f"uploads/{unique_filename}"
@app.route('/')
def index():
    return render_template_string('''
                                  <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EduTrade - College Marketplace</title>
    <!-- Add modern dependencies -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@11.0.19/dist/sweetalert2.min.css">
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #3b82f6;
            --accent-color: #60a5fa;
            --success-color: #22c55e;
            --error-color: #ef4444;
            --text-dark: #1f2937;
            --text-light: #6b7280;
            --background-light: #f3f4f6;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--background-light);
            color: var(--text-dark);
        }

        .navbar {
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .navbar-brand {
            font-weight: 700;
            color: var(--primary-color);
        }

        .hero-section {
            background: linear-gradient(rgba(37,99,235,0.9), rgba(59,130,246,0.9));
            background-image: ('/static/images/hero-bg.jpg');
            background-size: cover;
            color: white;
            padding: 4rem 0;
            margin-bottom: 2rem;
        }

        .auth-card {
            background: white;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 2rem;
            margin-bottom: 2rem;
        }

        .form-control, .form-select {
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            border: 1px solid #e5e7eb;
        }

        .form-control:focus, .form-select:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(96,165,250,0.2);
        }

        .btn-primary {
            background-color: var(--primary-color);
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
        }

        .btn-primary:hover {
            background-color: var(--secondary-color);
        }

        .listing-card {
            background: white;
            border-radius: 1rem;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
            height: 100%;
        }

        .listing-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }

        .listing-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }

        .listing-content {
            padding: 1.5rem;
        }

        .price-tag {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .search-section {
            background: white;
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }

        .modal-content {
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .badge {
            padding: 0.5rem 1rem;
            border-radius: 2rem;
            font-weight: 600;
        }

        .skeleton-loading {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }

        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .hero-section {
                padding: 2rem 0;
            }
            
            .auth-card {
                margin: 1rem;
            }
        }
        /* Add these to your existing style section */
        .hero-section {
            background: linear-gradient(rgba(211, 213, 216, 0.9), rgba(59,130,246,0.9));
            min-height: 100vh;
            display: flex;
            align-items: center;
            padding: 4rem 0;
        }

        .choice-card {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 1rem;
            padding: 2rem;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .choice-card:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-5px);
        }

        .choice-card h3 {
            margin: 1rem 0;
        }

        .choice-card p {
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <!-- Enhanced Navbar -->
    <nav class="navbar navbar-expand-lg navbar-light sticky-top">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-graduation-cap me-2"></i>EduTrade
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item" id="authButtons">
                        <button class="btn btn-outline-primary me-2" onclick="showLoginModal()">
                            <i class="fas fa-sign-in-alt me-2"></i>Login
                        </button>
                        <button class="btn btn-primary" onclick="showRegisterModal()">
                            <i class="fas fa-user-plus me-2"></i>Register
                        </button>
                    </li>
                    <li class="nav-item dropdown d-none" id="userMenu">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-circle me-2"></i><span id="userName"></span>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="showMyListings()">
                                <i class="fas fa-list me-2"></i>My Listings
                            </a></li>
                            <li><a class="dropdown-item" href="#" onclick="showWishlist()">
                                <i class="fas fa-heart me-2"></i>Wishlist
                            </a></li>
                            <li><a class="dropdown-item" href="#" onclick="showMessages()">
                                <i class="fas fa-envelope me-2"></i>Messages
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="#" onclick="logout()">
                                <i class="fas fa-sign-out-alt me-2"></i>Logout
                            </a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section text-center">
        <div class="container">
            <h1 class="display-4 mb-4">The Fastest Campus Service Provider</h1>
            <p class="lead mb-4">Your one-stop marketplace for college essentials</p>
            <div class="row justify-content-center mt-5">
                <div class="col-md-4">
                    <div class="choice-card" onclick="handlePathSelection('buy')">
                        <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                        <h3>Buy Items</h3>
                        <p>Browse and purchase items from other students</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="choice-card" onclick="handlePathSelection('sell')">
                        <i class="fas fa-store fa-3x mb-3"></i>
                        <h3>Sell/Rent Items</h3>
                        <p>List your items for sale or rent</p>
                    </div>
                </div>
            </div>
        </div>
    </section>
    <div class="container">
        <div class="search-section">
            <div class="row g-3">
                <div class="col-md-6">
                    <div class="input-group">
                        <span class="input-group-text"><i class="fas fa-search"></i></span>
                        <input type="text" class="form-control" id="searchInput" placeholder="Search items...">
                    </div>
                </div>
                <div class="col-md-3">
                    <select class="form-select" id="categoryFilter">
                        <option value="">All Categories</option>
                        <option value="textbooks">Textbooks</option>
                        <option value="electronics">Electronics</option>
                        <option value="furniture">Furniture</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <select class="form-select" id="sortFilter">
                        <option value="newest">Newest First</option>
                        <option value="price_low">Price: Low to High</option>
                        <option value="price_high">Price: High to Low</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="row g-4" id="listingsGrid">
            <!-- Listings will be dynamically added here -->
        </div>

        <!-- Loading Skeleton -->
        <div class="row g-4" id="loadingSkeleton" style="display: none;">
            <!-- Skeleton cards will be added here -->
        </div>
    </div>
    <div id="listingsSection" style="display: none;">
        <!-- Your existing search-section and listings grid will go here -->
        <div class="container">
            <div class="search-section">
                <!-- Your existing search section content -->
            </div>
            <div class="row g-4" id="listingsGrid">
                <!-- Listings will be dynamically added here -->
            </div>
        </div>
    </div>
    
    

    <!-- Search Section -->
    

        <!-- Listings Grid -->
        

    <!-- Modals -->
    <!-- Login Modal -->
    <div class="modal fade" id="loginModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Login to EduTrade</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="loginForm">
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" name="password" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-sign-in-alt me-2"></i>Login
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Register Modal -->
    <div class="modal fade" id="registerModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create Account</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="registerForm">
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Full Name</label>
                            <input type="text" class="form-control" name="full_name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Department</label>
                            <input type="text" class="form-control" name="department" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Year</label>
                            <select class="form-select" name="year" required>
                                <option value="">Select Year</option>
                                <option value="1">1st Year</option>
                                <option value="2">2nd Year</option>
                                <option value="3">3rd Year</option>
                                <option value="4">4th Year</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" name="password" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-user-plus me-2"></i>Register
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Create Listing Modal -->
    <div class="modal fade" id="createListingModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create New Listing</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="createListingForm">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label">Category</label>
                                <select class="form-select" name="category" id="listingCategory" required>
                                    <option value="">Select Category</option>
                                    <option value="electronic">Electronic</option>
                                    <option value="books">Books</option>
                                    <option value="clothes">Clothes</option>
                                </select>
                            </div>
    
                            <div class="col-md-6">
                                <label class="form-label">Product Type</label>
                                <select class="form-select" name="product_type" id="productType" required>
                                    <option value="">Select Product Type</option>
                                </select>
                            </div>
    
                            <!-- Book-specific fields -->
                            <div class="col-md-6 book-field" style="display: none;">
                                <label class="form-label">Subject</label>
                                <input type="text" class="form-control" name="subject" id="subject">
                            </div>
    
                            <div class="col-md-6 book-field" style="display: none;">
                                <label class="form-label">Branch</label>
                                <select class="form-select" name="branch" id="branch">
                                    <option value="CSE">CSE</option>
                                </select>
                            </div>
    
                            <div class="col-md-6">
                                <label class="form-label">Year</label>
                                <select class="form-select" name="study_year" required>
                                    <option value="1st year">2nd year</option>
                                    <option value="2nd year">2nd year</option>
                                    <option value="3rd year">2nd year</option>
                                    <option value="4th year">2nd year</option>
                                </select>
                            </div>
    
                            <div class="col-md-12">
                                <label class="form-label">Title</label>
                                <input type="text" class="form-control" name="title" required>
                            </div>
    
                            <div class="col-md-12">
                                <label class="form-label">Description</label>
                                <textarea class="form-control" name="description" rows="4" required></textarea>
                            </div>
    
                            <div class="col-md-6">
                                <label class="form-label">Price (₹)</label>
                                <input type="number" class="form-control" name="price" required>
                            </div>
    
                            <div class="col-md-6">
                                <label class="form-label">Working Condition</label>
                                <select class="form-select" name="working_condition" required>
                                    <option value="Fully functional">Fully functional</option>
                                    <option value="Needs repair">Needs repair</option>
                                </select>
                            </div>
    
                            <div class="col-md-6">
                                <label class="form-label">Warranty</label>
                                <select class="form-select" name="warranty_status" required>
                                    <option value="No">No</option>
                                    <option value="Yes">Yes</option>
                                </select>
                            </div>
    
                            <div class="col-md-12">
                                <label class="form-label">Images</label>
                                <input type="file" class="form-control" name="image" accept="image/*" required>
                                <div id="imagePreview" class="mt-2" style="display: none;">
                                    <img src="" alt="Preview" style="max-width: 200px; max-height: 200px;">
                                </div>
                            </div>
    
                            <div class="col-md-12">
                                <div class="form-check">
                                    <input type="checkbox" class="form-check-input" name="is_fake_warning" id="fakeWarning">
                                    <label class="form-check-label" for="fakeWarning">
                                        Warning: Check if you suspect this might be a fake product
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div class="d-grid mt-4">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-plus-circle me-2"></i>Create Listing
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.0.19/dist/sweetalert2.min.js"></script>
    <script>
        // Enhanced JavaScript functionality
        let currentUser = null;
        const modals = {
            login: new bootstrap.Modal(document.getElementById('loginModal')),
            register: new bootstrap.Modal(document.getElementById('registerModal')),
            createListing: new bootstrap.Modal(document.getElementById('createListingModal'))
        };
        let currentPath = null;

// Add this function to handle path selection
        function handlePathSelection(path) {
            currentPath = path;
            
            if (!currentUser) {
                showLoginModal();
                return;
            }
            
            handlePathAfterAuth(path);
        }

        // Add this function to handle path after authentication
        function handlePathAfterAuth(path) {
            const heroSection = document.querySelector('.hero-section');
            const listingsSection = document.getElementById('listingsSection');
            
            if (path === 'buy') {
                heroSection.style.display = 'none';
                listingsSection.style.display = 'block';
                loadListings();
            } else if (path === 'sell') {
                showCreateListing();
            }
        }

        // Utility Functions
        function showLoading() {
            document.getElementById('loadingSkeleton').style.display = 'flex';
            document.getElementById('listingsGrid').style.display = 'none';
        }

        function hideLoading() {
            document.getElementById('loadingSkeleton').style.display = 'none';
            document.getElementById('listingsGrid').style.display = 'flex';
        }

        function showAlert(title, text, icon) {
            Swal.fire({
                title,
                text,
                icon,
                confirmButtonColor: '#2563eb'
            });
        }

        // Modal Functions
        function showLoginModal() {
            modals.login.show();
        }

        function showRegisterModal() {
            modals.register.show();
        }

        function showCreateListing() {
            if (!currentUser) {
                showAlert('Please Login', 'You need to login to create a listing', 'warning');
                return;
            }
            modals.createListing.show();
        }

        // Authentication Functions
        function updateAuthUI() {
            const authButtons = document.getElementById('authButtons');
            const userMenu = document.getElementById('userMenu');
            const userName = document.getElementById('userName');

            if (currentUser) {
                authButtons.classList.add('d-none');
                userMenu.classList.remove('d-none');
                userName.textContent = currentUser.full_name;
            } else {
                authButtons.classList.remove('d-none');
                userMenu.classList.add('d-none');
            }
        }

        async function logout() {
            try {
                await fetch('/logout', {
                    method: 'GET',
                    credentials: 'same-origin'
                });
                currentUser = null;
                updateAuthUI();
                showAlert('Success', 'Logged out successfully', 'success');
            } catch (error) {
                showAlert('Error', 'Failed to logout', 'error');
            }
        }

        // Listing Functions
        async function loadListings() {
            showLoading();
            try {
                const query = document.getElementById('searchInput').value;
                const category = document.getElementById('categoryFilter').value;
                const sort = document.getElementById('sortFilter').value;
                
                let sortBy = 'created_at';
                if (sort === 'price_low') sortBy = 'price_low';
                if (sort === 'price_high') sortBy = 'price_high';

                const response = await fetch(`/listings?q=${query}&category=${category}&sort_by=${sortBy}`, {
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to load listings: ${response.status}`);
                }
                
                const data = await response.json();
                const listings = data.listings;
                
                const grid = document.getElementById('listingsGrid');
                grid.innerHTML = '';

                if (listings.length === 0) {
                    grid.innerHTML = '<div class="col-12 text-center my-5"><h4>No listings found</h4></div>';
                    hideLoading();
                    return;
                }

                listings.forEach(listing => {
                    const card = document.createElement('div');
                    card.className = 'col-md-4 col-lg-3';
                    
                    // Handle image URL properly
                    const imageUrl = listing.image_url ? 
                        (listing.image_url.startsWith('http') ? listing.image_url : `/static/${listing.image_url}`) : 
                        '/static/images/placeholder.jpg';
                    
                    card.innerHTML = `
                        <div class="listing-card">
                            <img src="${imageUrl}" class="listing-image" alt="${listing.title}">
                            <div class="listing-content">
                                <h5 class="mb-2">${listing.title}</h5>
                                <p class="price-tag mb-2">₹${listing.price}</p>
                                ${listing.rent_price > 0 ? 
                                    `<p class="text-success mb-2">Rent: ₹${listing.rent_price}/month</p>` : ''}
                                <p class="mb-2">
                                    <span class="badge bg-primary">${listing.category}</span>
                                    <span class="badge bg-secondary">${listing.condition}</span>
                                </p>
                                <p class="text-muted mb-3">Posted by ${listing.seller.name}</p>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-primary" onclick="contactSeller(${listing.id})">
                                        <i class="fas fa-envelope me-2"></i>Contact Seller
                                    </button>
                                    <button class="btn btn-outline-primary" onclick="addToWishlist(${listing.id})">
                                        <i class="fas fa-heart me-2"></i>Add to Wishlist
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                    grid.appendChild(card);
                });
            } catch (error) {
                console.error('Error loading listings:', error);
                showAlert('Error', 'Failed to load listings: ' + error.message, 'error');
            } finally {
                hideLoading();
            }
        }

        function contactSeller(listingId) {
            if (!currentUser) {
                showAlert('Please Login', 'You need to login to contact sellers', 'warning');
                return;
            }
            
            // Implement contact functionality here
            showAlert('Coming Soon', 'This feature is coming soon!', 'info');
        }

        function addToWishlist(listingId) {
            if (!currentUser) {
                showAlert('Please Login', 'You need to login to add items to wishlist', 'warning');
                return;
            }
            
            // Implement wishlist functionality here
            showAlert('Coming Soon', 'This feature is coming soon!', 'info');
        }

        function showMyListings() {
            if (!currentUser) {
                showAlert('Please Login', 'You need to login to view your listings', 'warning');
                return;
            }
            
            // Implement my listings functionality here
            showAlert('Coming Soon', 'This feature is coming soon!', 'info');
        }

        function showWishlist() {
            if (!currentUser) {
                showAlert('Please Login', 'You need to login to view your wishlist', 'warning');
                return;
            }
            
            // Implement wishlist view functionality here
            showAlert('Coming Soon', 'This feature is coming soon!', 'info');
        }

        function showMessages() {
            if (!currentUser) {
                showAlert('Please Login', 'You need to login to view your messages', 'warning');
                return;
            }
            
            // Implement messages functionality here
            showAlert('Coming Soon', 'This feature is coming soon!', 'info');
        }

        // Check session status on page load
        async function checkSession() {
            try {
                const response = await fetch('/check-session', {
                    credentials: 'same-origin'
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.authenticated) {
                        currentUser = data.user;
                        updateAuthUI();
                    }
                }
            } catch (error) {
                console.error('Session check failed:', error);
            }
        }

        // Event Listeners
        // Modify your DOMContentLoaded event listener
        document.addEventListener('DOMContentLoaded', () => {
            // Create skeleton loading cards
            const skeleton = document.getElementById('loadingSkeleton');
            for (let i = 0; i < 8; i++) {
                skeleton.innerHTML += `
                    <div class="col-md-4 col-lg-3">
                        <div class="listing-card">
                            <div class="skeleton-loading" style="height: 200px;"></div>
                            <div class="listing-content">
                                <div class="skeleton-loading" style="height: 24px; width: 80%; margin-bottom: 12px;"></div>
                                <div class="skeleton-loading" style="height: 18px; width: 60%; margin-bottom: 12px;"></div>
                                <div class="skeleton-loading" style="height: 18px; width: 40%; margin-bottom: 12px;"></div>
                            </div>
                        </div>
                    </div>
                `;
            }

            // Check if user is logged in
            checkSession();

            // Don't load listings immediately anymore
            // Only load when user chooses "Buy" path
            
            // Add event listeners for search and filters
            document.getElementById('searchInput').addEventListener('input', debounce(loadListings, 500));
            document.getElementById('categoryFilter').addEventListener('change', loadListings);
            document.getElementById('sortFilter').addEventListener('change', loadListings);
        });
        // Form submission handlers with enhanced error handling and validation
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const formData = new FormData(e.target);
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.error || 'Login failed');
                }
                
                const data = await response.json();
                currentUser = data.user;
                updateAuthUI();
                modals.login.hide();
                e.target.reset();
                
                // Add this line to handle the path after successful login
                if (currentPath) {
                    handlePathAfterAuth(currentPath);
                }
                
                showAlert('Success', 'Logged in successfully', 'success');
                
            } catch (error) {
                showAlert('Error', error.message, 'error');
            }
        });

        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const formData = new FormData(e.target);
                const response = await fetch('/register', {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.error || 'Registration failed');
                }
                
                const data = await response.json();
                modals.register.hide();
                e.target.reset();
                showAlert('Success', data.message || 'Registration successful! Please check your email.', 'success');
                
            } catch (error) {
                showAlert('Error', error.message, 'error');
            }
        });

        

        // Utility function for debouncing
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        const productTypes = {
            'electronic': ['Mobile', 'laptop','calci'],
            'books': ['Text books', 'class book','running notes'],
            'clothes': ['Casual', 'Formal','Apron']
        };
        
        // Image preview handler
        document.querySelector('input[name="image"]').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('imagePreview');
                    preview.style.display = 'block';
                    preview.querySelector('img').src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
        
        // Category change handler
        document.getElementById('listingCategory').addEventListener('change', function() {
            const category = this.value;
            const productTypeSelect = document.getElementById('productType');
            const bookFields = document.querySelectorAll('.book-field');
        
            // Update product types
            productTypeSelect.innerHTML = '<option value="">Select Product Type</option>';
            if (productTypes[category]) {
                productTypes[category].forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.toLowerCase();
                    option.textContent = type;
                    productTypeSelect.appendChild(option);
                });
            }
        
            // Show/hide book-specific fields
            bookFields.forEach(field => {
                field.style.display = category === 'books' ? 'block' : 'none';
            });
        });
        
        // Modify the existing createListingForm submit handler
        document.getElementById('createListingForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                if (!currentUser) {
                    throw new Error('You must be logged in to create a listing');
                }
                
                // Show loading state
                const submitBtn = e.target.querySelector('button[type="submit"]');
                const originalBtnText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating...';
                
                // Create FormData object
                const formData = new FormData(e.target);
                
                // Additional validation for book category
                const category = formData.get('category');
                if (category === 'books') {
                    if (!formData.get('subject')) {
                        throw new Error('Please enter the subject for the book');
                    }
                    if (!formData.get('branch')) {
                        throw new Error('Please select a branch');
                    }
                }
                
                // Ensure proper boolean conversion for is_fake_warning
                const isFakeWarning = e.target.querySelector('[name="is_fake_warning"]').checked;
                formData.set('is_fake_warning', isFakeWarning);
        
                // Make the API call
                const response = await fetch('/create-listing', {
                    method: 'POST',
                    body: formData, // Send as FormData, not JSON
                    credentials: 'same-origin'
                });
        
                // Handle non-200 responses
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to create listing');
                }
        
                // Handle success
                const data = await response.json();
                modals.createListing.hide();
                e.target.reset();
                document.getElementById('imagePreview').style.display = 'none';
                showAlert('Success', 'Listing created successfully', 'success');
                loadListings(); // Refresh the listings
        
            } catch (error) {
                showAlert('Error', error.message, 'error');
            } finally {
                // Reset button state
                const submitBtn = e.target.querySelector('button[type="submit"]');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-plus-circle me-2"></i>Create Listing';
            }
        });
        // Enhanced JavaScript functionality

        // Add this at the start of your JavaScript

    </script>
</body>
</html>''')
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authentication Routes
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.form

        # Validate input
        if not all(k in data for k in ['email', 'password', 'full_name', 'department', 'year']):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Create verification token
        verification_token = str(uuid.uuid4())

        # Create new user
        user = User(
            email=data['email'],
            full_name=data['full_name'],
            department=data['department'],
            year=data['year'],
            verification_token=verification_token
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Send verification email
        send_verification_email(user.email, verification_token)

        return jsonify({
            'message': 'Registration successful! Please check your email to verify your account.',
            'user_id': user.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.form

        if not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Missing email or password'}), 400

        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401

        if not user.is_verified:
            return jsonify({'error': 'Please verify your email first'}), 401

        login_user(user)

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'department': user.department,
                'year': user.year
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/verify-email/<token>')
def verify_email(token):
    try:
        user = User.query.filter_by(verification_token=token).first()
        if not user:
            return jsonify({'error': 'Invalid verification token'}), 400

        user.is_verified = True
        user.verification_token = None
        db.session.commit()

        return jsonify({'message': 'Email verified successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        email = request.json.get('email')
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Email not found'}), 404

        # Generate reset token
        reset_token = str(uuid.uuid4())
        user.reset_token = reset_token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        # Send reset email
        send_reset_email(email, reset_token)

        return jsonify({'message': 'Password reset instructions sent to your email'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.json
        if not all(k in data for k in ['token', 'new_password']):
            return jsonify({'error': 'Missing required fields'}), 400

        user = User.query.filter_by(reset_token=data['token']).first()
        if not user or user.reset_token_expiry < datetime.utcnow():
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        user.set_password(data['new_password'])
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        return jsonify({'message': 'Password reset successful'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Listing Routes
@app.route('/create-listing', methods=['POST'])
@login_required
def create_listing():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image = request.files['image']
        if image.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        # Save the image and get its path
        image_url = save_image(image)
        if not image_url:
            return jsonify({'error': 'Failed to save image'}), 500

        # Create listing
        listing = Listing(
            title=request.form['title'],
            description=request.form['description'],
            price=float(request.form['price']),
            category=request.form['category'],
            condition=request.form.get('working_condition', 'Not specified'),
            image_url=image_url,
            seller_id=current_user.id,
            product_type=request.form.get('product_type'),
            branch=request.form.get('branch'),
            study_year=request.form.get('study_year'),
            working_condition=request.form.get('working_condition'),
            warranty_status=request.form.get('warranty_status'),
            subject=request.form.get('subject'),
            is_fake_warning=bool(request.form.get('is_fake_warning', False))
        )

        db.session.add(listing)
        db.session.commit()

        return jsonify({
            'message': 'Listing created successfully',
            'id': listing.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/listings')
def get_listings():
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        sort_by = request.args.get('sort_by', 'created_at')

        listings_query = Listing.query

        if query:
            listings_query = listings_query.filter(
                db.or_(
                    Listing.title.ilike(f'%{query}%'),
                    Listing.description.ilike(f'%{query}%')
                )
            )

        if category:
            listings_query = listings_query.filter_by(category=category)

        if sort_by == 'price_low':
            listings_query = listings_query.order_by(Listing.price.asc())
        elif sort_by == 'price_high':
            listings_query = listings_query.order_by(Listing.price.desc())
        else:
            listings_query = listings_query.order_by(Listing.created_at.desc())

        listings = listings_query.all()

        return jsonify({
            'listings': [{
                'id': l.id,
                'title': l.title,
                'description': l.description,
                'price': l.price,
                'rent_price': l.rent_price,
                'category': l.category,
                'condition': l.condition,
                'image_url': l.image_url,
                'is_for_rent': l.is_for_rent,
                'created_at': l.created_at.isoformat(),
                'seller': {
                    'id': l.seller.id,
                    'name': l.seller.full_name
                },
                # New fields in response
                'product_type': l.product_type,
                'branch': l.branch,
                'study_year': l.study_year,
                'working_condition': l.working_condition,
                'warranty_status': l.warranty_status,
                'subject': l.subject,
                'is_fake_warning': l.is_fake_warning
            } for l in listings]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Utility functions
def send_verification_email(email, token):
    try:
        msg = Message('Verify your EduTrade account',
                     sender=app.config['MAIL_USERNAME'],
                     recipients=[email])
        msg.body = f'Click the following link to verify your email: {url_for("verify_email", token=token, _external=True)}'
        mail.send(msg)
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")

def send_reset_email(email, token):
    try:
        msg = Message('Reset your EduTrade password',
                     sender=app.config['MAIL_USERNAME'],
                     recipients=[email])
        msg.body = f'Click the following link to reset your password: {url_for("reset_password", token=token, _external=True)}'
        mail.send(msg)
    except Exception as e:
        print(f"Error sending reset email: {str(e)}")
@app.route('/check-session')
def check_session():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'full_name': current_user.full_name,
                'department': current_user.department,
                'year': current_user.year
            }
        })
    return jsonify({'authenticated': False})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
