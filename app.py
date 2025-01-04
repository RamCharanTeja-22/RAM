from flask import Flask, render_template_string, jsonify, request, send_from_directory
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'videos'
app.secret_key = 'your_secret_key_here'  # Added for session management

# Ensure video directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Education data structure
education_data = {
    'classes': {
        '8th': {
            'subjects': {
                'Mathematics': {
                    'topics': [
                        'Algebra Basics',
                        'Geometry Fundamentals',
                        'Linear Equations',
                        'Statistics'
                    ]
                },
                'Science': {
                    'topics': [
                        'Cell Structure',
                        'Force and Motion',
                        'Chemical Reactions',
                        'Energy Forms'
                    ]
                }
            }
        },
        '9th': {
            'subjects': {
                'Mathematics': {
                    'topics': [
                        'Advanced Algebra',
                        'Trigonometry',
                        'Coordinate Geometry',
                        'Probability'
                    ]
                },
                'Science': {
                    'topics': [
                        'Atomic Structure',
                        'Motion Laws',
                        'Life Processes',
                        'Environmental Science'
                    ]
                }
            }
        }
    }
}

# Content database
content_db = {
    "Algebra Basics": [
        "Algebraic Expressions: An algebraic expression is a combination of terms connected by addition, subtraction, multiplication, or division. Terms are parts of an expression separated by addition or subtraction. Coefficients are numbers multiplying variables in a term. Constants are fixed numbers without variables. Solve more complex equations and inequalities. Learn about polynomials and how to factor them. Explore quadratic equations and their graphs."
    ],
    "Geometry Fundamentals": [
        "Geometry involves shapes, sizes, and the properties of space. Basic concepts include points (dots on paper), lines (straight paths extending in both directions), angles (where two lines meet), and shapes like triangles, squares, and circles."
    ],
    "Linear Equations": [
        "Understand equations that form straight lines when graphed, solve problems like y=2x+3, and learn how to find the slope and intercepts of a line."
    ],
    "Statistics": [
        "Collect and organize data using tables and graphs, learn about mean, median, and mode, and interpret bar graphs, pie charts, and line graphs."
    ],
    "Cell Structure": [
        "Discover the basic unit of life, the cell, learn about its parts (nucleus, mitochondria, cell membrane), and compare plant and animal cells."
    ],
    "Force and Motion": [
        "Understand how forces make objects move, stop, or change direction, learn about Newton’s laws of motion, and explore speed, velocity, and acceleration."
    ],
    "Chemical Reactions": [
        "Study how substances combine or break apart to form new materials, learn about signs of a chemical reaction (bubbles, heat, color change), and explore simple reactions like burning or rusting."
    ],
    "Energy Forms": [
        "Discover different types of energy (kinetic, potential, heat, light), learn how energy is transferred and transformed, and explore renewable and non-renewable energy sources."
    ],
    "Advanced Algebra": [
        "Solve complex equations and inequalities, learn about polynomials and factoring, and explore quadratic equations and their graphs."
    ],
    "Trigonometry": [
        "Study triangles and their angles, learn about sine, cosine, and tangent ratios, and apply trigonometry to solve real-world problems like finding heights or distances."
    ],
    "Coordinate Geometry": [
        "Plot points on a graph using coordinates (x, y), learn how to find the distance between two points and the midpoint of a line, and explore the equations of lines and circles."
    ],
    "Probability": [
        "Understand the chances of events happening, learn to calculate probabilities using fractions, decimals, and percentages, and explore independent and dependent events."
    ],
    "Atomic Structure": [
        "Dive into the structure of atoms (protons, neutrons, electrons), learn about the periodic table and how elements are organized, and explore isotopes and atomic models."
    ],
    "Motion Laws": [
        "Study Newton’s three laws of motion in detail, understand concepts like inertia, force, and momentum, and solve problems involving motion and forces."
    ],
    "Life Processes": [
        "Learn how living organisms function (nutrition, respiration, excretion), explore the human body systems (digestive, respiratory, circulatory), and understand how plants and animals adapt to their environments."
    ],
    "Environmental Science": [
        "Study ecosystems and the balance of nature, learn about natural resources and their conservation, and explore environmental issues like pollution, deforestation, and climate change."
    ]
}

# HTML template with integrated login/registration
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TutorTeach.ai - Modern Learning Experience</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        /* CSS Styles */
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3bc9db;
            --accent-color: #ffd803;
            --danger-color: #e63946;
            --text-color: #2b2d42;
            --text-light: #6b7280;
            --light-bg: #f8f9fa;
            --white: #ffffff;
            --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            transition: all 0.3s ease;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--light-bg);
            color: var(--text-color);
            line-height: 1.6;
        }

        .page {
            display: none;
            animation: fadeIn 0.5s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .page.active {
            display: block;
        }

        header {
            background: var(--gradient);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
        }

        nav {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--white);
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            cursor: pointer;
        }

        nav ul {
            display: flex;
            gap: 2rem;
            list-style: none;
        }

        nav ul li a {
            color: var(--white);
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        nav ul li a:hover {
            background-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }

        .dropdown {
            position: relative;
        }

        .dropdown-content {
            display: none;
            position: absolute;
            background-color: var(--white);
            min-width: 160px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            z-index: 1;
            border-radius: 8px;
            overflow: hidden;
        }

        .dropdown-content a {
            color: var(--text-color);
            padding: 12px 16px;
            text-decoration: none;
            display: block;
            transition: background-color 0.3s ease;
        }

        .dropdown-content a:hover {
            background-color: var(--light-bg);
        }

        .dropdown:hover .dropdown-content {
            display: block;
        }

        main {
            margin-top: 80px;
            padding: 2rem;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }

        .auth-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background: var(--white);
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .auth-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .form-group label {
            font-weight: 500;
            color: var(--text-color);
        }

        .form-group input {
            padding: 0.75rem;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            font-size: 1rem;
        }

        .auth-switch {
            margin-top: 1rem;
            text-align: center;
            color: var(--text-light);
        }

        .auth-switch a {
            color: var(--primary-color);
            text-decoration: none;
            cursor: pointer;
            font-weight: 500;
        }

        .error-message {
            color: var(--danger-color);
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }

        .success-message {
            color: #10B981;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }

        .hero {
            text-align: center;
            padding: 6rem 2rem;
            background: var(--gradient);
            border-radius: 30px;
            margin-bottom: 3rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }

        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1.5rem;
            color: var(--white);
            position: relative;
        }

        .hero p {
            font-size: 1.3rem;
            color: var(--white);
            max-width: 700px;
            margin: 0 auto 2rem;
            position: relative;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .card {
            background: var(--white);
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
        }

        .button {
            background: var(--gradient);
            color: var(--white);
            padding: 1rem 2rem;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }

        .button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }

        .button:disabled {
            background: var(--text-light);
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .content-display {
            font-size: 1.2rem;
            line-height: 1.6;
            margin: 1rem 0;
            padding: 1rem;
            background: var(--light-bg);
            border-radius: 8px;
        }

        #video-player {
            border-radius: 8px;
            margin-top: 1rem;
        }

        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }

            nav ul {
                display: none;
                position: absolute;
                top: 100%;
                left: 0;
                width: 100%;
                background: var(--gradient);
                padding: 1rem;
                flex-direction: column;
                align-items: center;
            }

            nav ul.active {
                display: flex;
            }

            .menu-toggle {
                display: block;
                color: var(--white);
                font-size: 1.5rem;
                cursor: pointer;
            }
        }
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="logo" onclick="showPage('home')">TutorTeach.ai</div>
            <div class="menu-toggle">
                <i class="fas fa-bars"></i>
            </div>
            <ul>
                <li><a onclick="showPage('home')"><i class="fas fa-home"></i> Home</a></li>
                <li><a onclick="showPage('features')"><i class="fas fa-star"></i> Features</a></li>
                <li><a onclick="showPage('learning-path')"><i class="fas fa-road"></i> Learning Path</a></li>
                <li class="dropdown">
                    <a id="authButton"><i class="fas fa-user"></i> Profile</a>
                    <div class="dropdown-content">
                        <a onclick="showProfile()">My Profile</a>
                        <a onclick="showDashboard()">My Dashboard</a>
                        <a onclick="logout()">Logout</a>
                    </div>
                </li>
            </ul>
        </nav>
    </header>

    <main>
        <!-- Home Page -->
        <div id="home-page" class="page active">
            <section class="hero">
                <h1>Transform Your Learning Journey</h1>
                <p>Welcome to TutorTeach.ai - Your AI-powered learning companion that adapts to your unique needs.</p>
                <button class="button" onclick="showPage('learning-path')">Start Learning Now</button>
            </section>
        </div>

        <!-- Features Page -->
        <div id="features-page" class="page">
            <section class="hero">
                <h1>Our Features</h1>
                <div class="grid">
                    <div class="card">
                        <h2>Personalized Learning</h2>
                        <p>AI-driven content tailored to your learning style and pace.</p>
                    </div>
                    <div class="card">
                        <h2>Interactive Lessons</h2>
                        <p>Engage with dynamic content and real-time feedback.</p>
                    </div>
                    <div class="card">
                        <h2>Progress Tracking</h2>
                        <p>Monitor your growth with detailed analytics and insights.</p>
                    </div>
                </div>
            </section>
        </div>

        <!-- Learning Path Page -->
        <div id="learning-path-page" class="page">
            <div class="breadcrumb" id="breadcrumb"></div>
            <div id="class-selection" class="grid fade-in">
                <!-- Classes will be dynamically inserted here -->
            </div>
            <div id="subject-selection" class="grid fade-in hidden">
                <!-- Subjects will be dynamically inserted here -->
            </div>
            <div id="topic-selection" class="grid fade-in hidden">
                <!-- Topics will be dynamically inserted here -->
            </div>
            <div id="content-section" class="hidden">
                <div class="card">
                    <h2 id="content-title"></h2>
                    <div id="content-display" class="content-display"></div>
                    <button id="mark-complete-button" class="button" onclick="markComplete()" disabled>Mark as Complete</button>
                </div>
            </div>
            <div id="video-section" class="hidden">
                <div class="card">
                    <h2>Video: <span id="video-title"></span></h2>
                    <video id="video-player" controls width="100%">
                        Your browser does not support the video tag.
                    </video>
                </div>
            </div>
            <div id="navigation" class="hidden">
                <button class="back-button" onclick="goBack()">
                    <i class="fas fa-arrow-left"></i> Go Back
                </button>
            </div>
        </div>

        <!-- Profile Page -->
        <div id="profile-page" class="page">
            <div class="auth-container">
                <h2 class="text-2xl font-bold mb-4 text-center">My Profile</h2>
                <form class="auth-form" onsubmit="updateProfile(event)">
                    <div class="form-group">
                        <label for="registeredName">Registered Name</label>
                        <input type="text" id="registeredName" disabled>
                    </div>
                    <div class="form-group">
                        <label for="displayName">Display Name</label>
                        <input type="text" id="displayName" required>
                    </div>
                    <div class="form-group">
                        <label for="profileEmail">Email</label>
                        <input type="email" id="profileEmail" disabled>
                    </div>
                    <div class="form-group">
                        <label for="profilePhoto">Profile Photo</label>
                        <input type="file" id="profilePhoto" accept="image/*">
                    </div>
                    <div class="form-group">
                        <label for="currentPassword">Current Password</label>
                        <input type="password" id="currentPassword" required>
                    </div>
                    <div class="form-group">
                        <label for="newPassword">New Password</label>
                        <input type="password" id="newPassword" required>
                    </div>
                    <div class="form-group">
                        <label for="confirmNewPassword">Confirm New Password</label>
                        <input type="password" id="confirmNewPassword" required>
                    </div>
                    <button type="submit" class="button">Update Profile</button>
                    <div id="profileMessage"></div>
                </form>
            </div>
        </div>

        <!-- Dashboard Page -->
        <div id="dashboard-page" class="page">
            <div class="auth-container">
                <h2 class="text-2xl font-bold mb-4 text-center">My Dashboard</h2>
                <div class="card">
                    <h2>Progress</h2>
                    <div class="progress-bar">
                        <div style="width: 50%;"></div> <!-- Example progress -->
                    </div>
                </div>
                <div class="card">
                    <h2>Lessons Completed</h2>
                    <p id="lessons-completed">5</p> <!-- Example data -->
                </div>
                <div class="card">
                    <h2>Lessons Ongoing</h2>
                    <p id="lessons-ongoing">3</p> <!-- Example data -->
                </div>
                <div class="card">
                    <h2>Percentage of Progress</h2>
                    <p id="progress-percentage">50%</p> <!-- Example data -->
                </div>
            </div>
        </div>

        <!-- Login Page -->
        <div id="login-page" class="page">
            <div class="auth-container">
                <h2 class="text-2xl font-bold mb-4 text-center">Login</h2>
                <form class="auth-form" onsubmit="handleLogin(event)">
                    <div class="form-group">
                        <label for="loginEmail">Email</label>
                        <input type="email" id="loginEmail" required>
                    </div>
                    <div class="form-group">
                        <label for="loginPassword">Password</label>
                        <input type="password" id="loginPassword" required>
                    </div>
                    <button type="submit" class="button">Login</button>
                    <div id="loginMessage"></div>
                </form>
                <div class="auth-switch">
                   Don't have an account? <a onclick="showPage('register')">Register</a>
                </div>
            </div>
        </div>

        <!-- Register Page -->
        <div id="register-page" class="page">
            <div class="auth-container">
                <h2 class="text-2xl font-bold mb-4 text-center">Register</h2>
                <form class="auth-form" onsubmit="handleRegister(event)">
                    <div class="form-group">
                        <label for="registerName">Full Name</label>
                        <input type="text" id="registerName" required>
                    </div>
                    <div class="form-group">
                        <label for="registerEmail">Email</label>
                        <input type="email" id="registerEmail" required>
                    </div>
                    <div class="form-group">
                        <label for="registerPassword">Password</label>
                        <input type="password" id="registerPassword" required minlength="6">
                    </div>
                    <div class="form-group">
                        <label for="confirmPassword">Confirm Password</label>
                        <input type="password" id="confirmPassword" required>
                    </div>
                    <button type="submit" class="button">Register</button>
                    <div id="registerMessage"></div>
                </form>
                <div class="auth-switch">
                    Already have an account? <a onclick="showPage('login')">Login</a>
                </div>
            </div>
        </div>
    </main>

    <script>
        // State management
        let currentClass = null;
        let currentSubject = null;
        let currentTopic = null;
        let contentIndex = 0;
        let contentComplete = false;
        let videoComplete = false;
        let isMobileMenuOpen = false;
        let users = JSON.parse(localStorage.getItem('users')) || [];
        let currentUser = JSON.parse(localStorage.getItem('currentUser'));

        // Update auth button based on login status
        function updateAuthButton() {
            const authButton = document.getElementById('authButton');
            if (currentUser) {
                authButton.innerHTML = <i class="fas fa-user"></i> ${currentUser.displayName || currentUser.name};
            } else {
                authButton.innerHTML = <i class="fas fa-user"></i> Login;
            }
        }

        // Show Profile Page
        function showProfile() {
            if (!currentUser) {
                showPage('login');
                return;
            }
            document.getElementById('registeredName').value = currentUser.name;
            document.getElementById('displayName').value = currentUser.displayName || currentUser.name;
            document.getElementById('profileEmail').value = currentUser.email;
            showPage('profile');
        }

        // Show Dashboard Page
        function showDashboard() {
            if (!currentUser) {
                showPage('login');
                return;
            }
            // Example data for dashboard (you can replace this with actual data)
            document.getElementById('lessons-completed').textContent = '5';
            document.getElementById('lessons-ongoing').textContent = '3';
            document.getElementById('progress-percentage').textContent = '50%';
            showPage('dashboard');
        }

        // Handle registration
        function handleRegister(event) {
            event.preventDefault();
            const messageDiv = document.getElementById('registerMessage');
            const name = document.getElementById('registerName').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (password !== confirmPassword) {
                messageDiv.className = 'error-message';
                messageDiv.textContent = 'Passwords do not match!';
                return;
            }

            if (users.some(user => user.email === email)) {
                messageDiv.className = 'error-message';
                messageDiv.textContent = 'Email already registered!';
                return;
            }

            users.push({ name, email, password });
            localStorage.setItem('users', JSON.stringify(users));
            
            messageDiv.className = 'success-message';
            messageDiv.textContent = 'Registration successful! Redirecting to login...';
            
            setTimeout(() => {
                showPage('login');
            }, 2000);
        }

        // Handle login
        function handleLogin(event) {
            event.preventDefault();
            const messageDiv = document.getElementById('loginMessage');
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            const user = users.find(u => u.email === email && u.password === password);
            
            if (user) {
                currentUser = user;
                localStorage.setItem('currentUser', JSON.stringify(user));
                updateAuthButton();
                
                messageDiv.className = 'success-message';
                messageDiv.textContent = 'Login successful! Redirecting...';
                
                setTimeout(() => {
                    showPage('home');
                }, 1000);
            } else {
                messageDiv.className = 'error-message';
                messageDiv.textContent = 'Invalid email or password!';
            }
        }

        // Handle logout
        function logout() {
            currentUser = null;
            localStorage.removeItem('currentUser');
            updateAuthButton();
            showPage('home');
        }

        // Initialize the learning path
        function initLearningPath() {
            renderClasses();
            updateBreadcrumb();
        }

        // Render class selection
        function renderClasses() {
            fetch('/api/classes')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('class-selection');
                    container.innerHTML = Object.keys(data.classes).map(className => `
                        <div class="card" onclick="selectClass('${className}')">
                            <h2 class="card-title">Class ${className}</h2>
                            <p class="card-content">Explore subjects and topics for Class ${className}</p>
                        </div>
                    `).join('');
                });
        }

        // Select a class
        function selectClass(className) {
            currentClass = className;
            fetch(/api/subjects/${className})
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('subject-selection');
                    container.innerHTML = Object.keys(data.subjects).map(subject => `
                        <div class="card" onclick="selectSubject('${subject}')">
                            <h2 class="card-title">${subject}</h2>
                            <p class="card-content">Explore topics in ${subject}</p>
                        </div>
                    `).join('');
                    
                    showSection('subject-selection');
                    updateBreadcrumb();
                });
        }

        // Select a subject
        function selectSubject(subject) {
            if (!currentUser) {
                showPage('login');
                return;
            }
            currentSubject = subject;
            fetch(/api/topics/${currentClass}/${subject})
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('topic-selection');
                    container.innerHTML = data.topics.map(topic => `
                        <div class="card" onclick="selectTopic('${topic}')">
                            <h2 class="card-title">${topic}</h2>
                            <p class="card-content">Learn about ${topic}</p>
                        </div>
                    `).join('');
                    
                    showSection('topic-selection');
                    updateBreadcrumb();
                });
        }

        // Select a topic
        function selectTopic(topic) {
            currentTopic = topic;
            fetch(/api/content/${topic})
                .then(response => response.json())
                .then(data => {
                    if (data.content) {
                        document.getElementById('topic-selection').classList.add('hidden');
                        document.getElementById('content-section').classList.remove('hidden');
                        displayContentWordByWord(data.content);
                    } else {
                        alert('No content available for this topic.');
                    }
                });
            updateBreadcrumb();
        }

        // Display content word by word
        function displayContentWordByWord(content) {
            const contentContainer = document.getElementById('content-display');
            contentContainer.innerHTML = ''; // Clear previous content
            const words = content.split(' ');
            let index = 0;

            const interval = setInterval(() => {
                if (index >= words.length) {
                    clearInterval(interval);
                    document.getElementById('mark-complete-button').disabled = false; // Enable "Mark as Complete" button
                    return;
                }
                contentContainer.innerHTML += words[index] + ' ';
                index++;
            }, 100); // Adjust speed as needed
        }

        // Mark a topic as complete
        function markComplete() {
            contentComplete = true;
            document.getElementById('content-section').classList.add('hidden');
            document.getElementById('video-section').classList.remove('hidden');
            fetch(/api/video/${currentTopic})
                .then(response => response.json())
                .then(data => {
                    if (data.video_path) {
                        const videoPlayer = document.getElementById('video-player');
                        videoPlayer.src = /videos/${data.video_path};
                        videoPlayer.load();
                        videoPlayer.play();
                    } else {
                        alert('No video available for this topic.');
                    }
                });
        }

        // Show page function
        function showPage(pageId) {
            // If trying to access learning path while not logged in
            if (pageId === 'learning-path' && !currentUser) {
                showPage('login');
                return;
            }

            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            document.getElementById(pageId + '-page').classList.add('active');
            
            if (pageId === 'learning-path') {
                initLearningPath();
            }
            
            if (isMobileMenuOpen) {
                document.querySelector('nav ul').classList.remove('active');
                isMobileMenuOpen = false;
            }
        }

        // Navigation
        function goBack() {
            if (currentTopic) {
                currentTopic = null;
                showSection('topic-selection');
            } else if (currentSubject) {
                currentSubject = null;
                showSection('subject-selection');
            } else if (currentClass) {
                currentClass = null;
                showSection('class-selection');
                document.getElementById('navigation').classList.add('hidden');
            }
            updateBreadcrumb();
        }

        // Update breadcrumb
        function updateBreadcrumb() {
            const breadcrumb = document.getElementById('breadcrumb');
            let path = [];
            if (currentClass) path.push(Class ${currentClass});
            if (currentSubject) path.push(currentSubject);
            if (currentTopic) path.push(currentTopic);
            breadcrumb.textContent = path.join(' → ');
        }

        // Show/hide sections
        function showSection(sectionId) {
            ['class-selection', 'subject-selection', 'topic-selection', 'content-section', 'video-section'].forEach(id => {
                document.getElementById(id).classList.add('hidden');
            });
            document.getElementById(sectionId).classList.remove('hidden');
            document.getElementById('navigation').classList.remove('hidden');
        }

        // Initialize auth state and mobile menu
        updateAuthButton();
        const menuToggle = document.querySelector('.menu-toggle');
        menuToggle.addEventListener('click', () => {
            const navUl = document.querySelector('nav ul');
            navUl.classList.toggle('active');
            isMobileMenuOpen = !isMobileMenuOpen;
        });

        // Initial check for mobile menu
        if (window.innerWidth <= 768) {
            menuToggle.style.display = 'block';
        }
    </script>
</body>
</html>
'''

# Flask routes
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/classes')
def get_classes():
    return jsonify({"classes": education_data['classes']})

@app.route('/api/subjects/<class_name>')
def get_subjects(class_name):
    if class_name not in education_data['classes']:
        return jsonify({"error": "Class not found"}), 404
    return jsonify({"subjects": education_data['classes'][class_name]['subjects']})

@app.route('/api/topics/<class_name>/<subject>')
def get_topics(class_name, subject):
    if class_name not in education_data['classes'] or \
       subject not in education_data['classes'][class_name]['subjects']:
        return jsonify({"error": "Invalid class or subject"}), 404
    return jsonify({"topics": education_data['classes'][class_name]['subjects'][subject]['topics']})

@app.route('/api/content/<topic>')
def get_content(topic):
    if topic not in content_db:
        return jsonify({"content": None})
    return jsonify({"content": content_db[topic][0]})  # Return the first content item for simplicity

@app.route('/api/video/<topic>')
def get_video(topic):
    video_path = f"{topic.lower().replace(' ', '_')}.mp4"
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], video_path)):
        return jsonify({"video_path": video_path})
    return jsonify({"video_path": None})

@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5000)
