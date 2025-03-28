from flask import Flask, render_template_string, jsonify, request, send_from_directory
from flask_mail import Mail, Message
import os
import random
import string

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'videos'
app.secret_key = 'your_secret_key_here'  # Added for session management

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your email provider's SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tutorteach.ai@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'TUTOR@123'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'jmadhan087@gmail.com'  # Replace with your email

mail = Mail(app)

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
        },
        '10th': {
            'subjects': {
                'Mathematics': {
                    'topics': [
                        'Quadratic Equations',
                        'Arithmetic Progressions',
                        'Circles',
                        'Probability'
                    ]
                },
                'Science': {
                    'topics': [
                        'Chemical Reactions and Equations',
                        'Acids, Bases and Salts',
                        'Life Processes',
                        'Heredity and Evolution'
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
    ],
    "Quadratic Equations": [
        "Learn about quadratic equations, their solutions, and how to graph them. Understand the discriminant and its significance in determining the nature of roots."
    ],
    "Arithmetic Progressions": [
        "Understand the concept of arithmetic progressions, find the nth term, and the sum of the first n terms. Solve real-world problems using arithmetic progressions."
    ],
    "Circles": [
        "Explore the properties of circles, including chords, tangents, and angles subtended by chords. Learn about the theorems related to circles and their applications."
    ],
    "Chemical Reactions and Equations": [
        "Understand the types of chemical reactions, balancing chemical equations, and the importance of chemical reactions in daily life."
    ],
    "Acids, Bases and Salts": [
        "Learn about the properties of acids, bases, and salts. Understand the pH scale, neutralization reactions, and the uses of acids, bases, and salts."
    ],
    "Heredity and Evolution": [
        "Study the principles of heredity and variation. Understand the concepts of evolution, natural selection, and the evidence for evolution."
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
        /* CSS Variables for Color Scheme */
        :root {
            --primary-color: #4A90E2; /* Soft blue */
            --secondary-color: #50E3C2; /* Teal */
            --accent-color: #F5A623; /* Orange */
            --danger-color: #D0021B; /* Red */
            --text-color: #2C3E50; /* Dark gray */
            --text-light: #7F8C8D; /* Light gray */
            --light-bg: #F5F7FA; /* Light background */
            --white: #FFFFFF; /* White */
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
            background: var(--primary-color);
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
            background: var(--primary-color);
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
                background: var(--primary-color);
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

        /* Animations */
        @keyframes slideInFromLeft {
            0% {
                transform: translateX(-100%);
                opacity: 0;
            }
            100% {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideInFromRight {
            0% {
                transform: translateX(100%);
                opacity: 0;
            }
            100% {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideInFromTop {
            0% {
                transform: translateY(-100%);
                opacity: 0;
            }
            100% {
                transform: translateY(0);
                opacity: 1;
            }
        }

        @keyframes slideInFromBottom {
            0% {
                transform: translateY(100%);
                opacity: 0;
            }
            100% {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .slide-in-left {
            animation: slideInFromLeft 1s ease-out;
        }

        .slide-in-right {
            animation: slideInFromRight 1s ease-out;
        }

        .slide-in-top {
            animation: slideInFromTop 1s ease-out;
        }

        .slide-in-bottom {
            animation: slideInFromBottom 1s ease-out;
        }

        /* Background bubbles */
        .bubbles {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }

        .bubbles li {
            position: absolute;
            list-style: none;
            display: block;
            width: 20px;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            animation: animate 25s linear infinite;
            bottom: -150px;
        }

        .bubbles li:nth-child(1) {
            left: 25%;
            width: 80px;
            height: 80px;
            animation-delay: 0s;
        }

        .bubbles li:nth-child(2) {
            left: 10%;
            width: 20px;
            height: 20px;
            animation-delay: 2s;
            animation-duration: 12s;
        }

        .bubbles li:nth-child(3) {
            left: 70%;
            width: 20px;
            height: 20px;
            animation-delay: 4s;
        }

        .bubbles li:nth-child(4) {
            left: 40%;
            width: 60px;
            height: 60px;
            animation-delay: 0s;
            animation-duration: 18s;
        }

        .bubbles li:nth-child(5) {
            left: 65%;
            width: 20px;
            height: 20px;
            animation-delay: 0s;
        }

        .bubbles li:nth-child(6) {
            left: 75%;
            width: 110px;
            height: 110px;
            animation-delay: 3s;
        }

        .bubbles li:nth-child(7) {
            left: 35%;
            width: 150px;
            height: 150px;
            animation-delay: 7s;
        }

        .bubbles li:nth-child(8) {
            left: 50%;
            width: 25px;
            height: 25px;
            animation-delay: 15s;
            animation-duration: 45s;
        }

        .bubbles li:nth-child(9) {
            left: 20%;
            width: 15px;
            height: 15px;
            animation-delay: 2s;
            animation-duration: 35s;
        }

        .bubbles li:nth-child(10) {
            left: 85%;
            width: 150px;
            height: 150px;
            animation-delay: 0s;
            animation-duration: 11s;
        }

        @keyframes animate {
            0% {
                transform: translateY(0) rotate(0deg);
                opacity: 1;
                border-radius: 0;
            }
            100% {
                transform: translateY(-1000px) rotate(720deg);
                opacity: 0;
                border-radius: 50%;
            }
        }

        /* Profile image */
        .profile-image {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 10px;
        }

        /* Contact form */
        .contact-form {
            max-width: 600px;
            margin: 0 auto;
            padding: 2rem;
            background: var(--white);
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .contact-form .form-group {
            margin-bottom: 1rem;
        }

        .contact-form .form-group label {
            font-weight: 500;
            color: var(--text-color);
        }

        .contact-form .form-group input,
        .contact-form .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            font-size: 1rem;
        }

        .contact-form .form-group textarea {
            resize: vertical;
            min-height: 150px;
        }

        .contact-form .button {
            width: 100%;
            margin-top: 1rem;
        }

        /* Testimonials Section */
        .testimonials {
            padding: 4rem 2rem;
            background: var(--light-bg);
        }

        .testimonials h2 {
            text-align: center;
            margin-bottom: 2rem;
        }

        .testimonial-card {
            background: var(--white);
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }

        .testimonial-card img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 1rem;
        }

        .testimonial-card h3 {
            margin-bottom: 0.5rem;
        }

        .testimonial-card p {
            font-style: italic;
            color: var(--text-light);
        }

        /* Footer Section */
        footer {
            background: var(--primary-color);
            color: var(--white);
            padding: 2rem;
            text-align: center;
        }

        footer .footer-links {
            margin-bottom: 1rem;
        }

        footer .footer-links a {
            color: var(--white);
            text-decoration: none;
            margin: 0 1rem;
        }

        footer .footer-links a:hover {
            text-decoration: underline;
        }

        footer .social-icons {
            margin-bottom: 1rem;
        }

        footer .social-icons a {
            color: var(--white);
            margin: 0 0.5rem;
            font-size: 1.5rem;
        }

        footer .social-icons a:hover {
            color: var(--secondary-color);
        }

        footer .copyright {
            font-size: 0.875rem;
            color: var(--white);
        }

        /* Live Chat Icon */
        .live-chat {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--primary-color);
            color: var(--white);
            padding: 1rem;
            border-radius: 50%;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            cursor: pointer;
        }

        .live-chat:hover {
            background: var(--secondary-color);
        }

        /* AI Stats Section */
        .ai-stats {
            padding: 4rem 2rem;
            background: var(--gradient);
            color: var(--white);
            text-align: center;
        }

        .ai-stats h2 {
            margin-bottom: 2rem;
        }

        .ai-stats .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }

        .ai-stats .stat {
            background: rgba(255, 255, 255, 0.1);
            padding: 1.5rem;
            border-radius: 1rem;
        }

        .ai-stats .stat h3 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .ai-stats .stat p {
            font-size: 1rem;
        }

        /* Video Demo Section */
        .video-demo {
            padding: 4rem 2rem;
            background: var(--light-bg);
            text-align: center;
        }

        .video-demo h2 {
            margin-bottom: 2rem;
        }

        .video-container {
            max-width: 800px;
            margin: 0 auto;
        }

        .video-container iframe {
            width: 100%;
            height: 400px;
            border-radius: 8px;
        }

        /* Blurred Class Selection */
        .blurred {
            filter: blur(5px);
            pointer-events: none;
        }

        /* Testimonials Scroll Animation */
        .testimonials-scroll {
            display: flex;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            gap: 1.5rem;
            padding-bottom: 1rem;
        }

        .testimonials-scroll .testimonial-card {
            flex: 0 0 auto;
            scroll-snap-align: start;
            width: 300px;
        }

        /* AI Stats Counter Animation */
        @keyframes countUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .stat h3 {
            animation: countUp 1s ease-out;
        }

        /* About Developers Section */
        .about-developers {
            padding: 4rem 2rem;
            background: var(--light-bg);
            text-align: center;
        }

        .about-developers h2 {
            margin-bottom: 2rem;
        }

        .developers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }

        .developer-card {
            background: var(--white);
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }

        .developer-card img {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 1rem;
        }

        .developer-card h3 {
            margin-bottom: 0.5rem;
        }

        .developer-card p {
            font-style: italic;
            color: var(--text-light);
        }

        .developer-card .social-links {
            margin-top: 1rem;
        }

        .developer-card .social-links a {
            color: var(--primary-color);
            margin: 0 0.5rem;
            font-size: 1.5rem;
        }

        .developer-card .social-links a:hover {
            color: var(--secondary-color);
        }

        /* What's New Section */
        .whats-new {
            padding: 4rem 2rem;
            background: var(--light-bg);
            text-align: center;
        }

        .whats-new h2 {
            margin-bottom: 2rem;
        }

        .whats-new .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .whats-new .card {
            background: var(--white);
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .whats-new .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
        }

        .whats-new .card h3 {
            margin-bottom: 1rem;
        }

        .whats-new .card p {
            font-size: 1rem;
            color: var(--text-light);
        }

        /* Learning Path Navigation */
        .learning-path-nav {
            display: flex;
            justify-content: space-between;
            margin-top: 1rem;
        }

        .learning-path-nav .button {
            width: 48%; 
        }
        #features-page {
            padding: 2rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            min-height: 100vh;
        }

        .hero {
            text-align: center;
            margin-bottom: 3rem;
            position: relative;
        }

        .hero h1 {
            font-size: 3rem;
            color: #2d3748;
            margin-bottom: 2rem;
            font-weight: 700;
            position: relative;
            display: inline-block;
        }

        .hero h1::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 3px;
            background: #4a90e2;
            animation: underline 1s ease forwards 0.5s;
        }

        @keyframes underline {
            to {
                width: 100%;
            }
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }

        .feature-card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }

        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #4a90e2, #63b3ed);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }

        .feature-card:hover::before {
            transform: scaleX(1);
        }

        .feature-icon {
            font-size: 2.5rem;
            color: #4a90e2;
            margin-bottom: 1.5rem;
            text-align: center;
            transition: transform 0.3s ease;
        }

        .feature-card:hover .feature-icon {
            transform: scale(1.1) rotate(5deg);
        }

        .feature-card h2 {
            font-size: 1.5rem;
            color: #2d3748;
            margin-bottom: 1rem;
            font-weight: 600;
            transition: color 0.3s ease;
        }

        .feature-card:hover h2 {
            color: #4a90e2;
        }

        .feature-card p {
            color: #4a5568;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .feature-explanation {
            padding-top: 1rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 1rem;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            max-height: 0;
            overflow: hidden;
        }

        .feature-card:hover .feature-explanation {
            opacity: 1;
            transform: translateY(0);
            max-height: 200px;
        }

        .feature-explanation p {
            font-size: 0.95rem;
            color: #718096;
        }

        /* Animation Classes */
        .slide-in-left {
            opacity: 0;
            animation: slideInLeft 0.6s ease-out forwards;
        }

        .slide-in-right {
            opacity: 0;
            animation: slideInRight 0.6s ease-out forwards;
        }

        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        /* Stagger animation delay for cards */
        .feature-card:nth-child(1) { animation-delay: 0.1s; }
        .feature-card:nth-child(2) { animation-delay: 0.2s; }
        .feature-card:nth-child(3) { animation-delay: 0.3s; }
        .feature-card:nth-child(4) { animation-delay: 0.4s; }
        .feature-card:nth-child(5) { animation-delay: 0.5s; }
        .feature-card:nth-child(6) { animation-delay: 0.6s; }
        .feature-card:nth-child(7) { animation-delay: 0.7s; }
        .feature-card:nth-child(8) { animation-delay: 0.8s; }

        /* Responsive Design */
        @media (max-width: 768px) {
            #features-page {
                padding: 1rem;
            }
            
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .grid {
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }
            
            .feature-card {
                padding: 1.5rem;
            }
        }

        /* Ensure Font Awesome icons are styled properly */
        .fas {
            display: inline-block;
            width: 1em;
            height: 1em;
            vertical-align: -0.125em;
        }
        /* ... (keeping previous base styles) ... */

/* Add these new styles to your existing CSS */

/* Modify the existing p styles for first paragraph */
        .feature-card p:first-of-type {
            color: #4a5568;
            line-height: 1.6;
            margin-bottom: 1rem;
            opacity: 0;
            transform: translateY(-20px);
            transition: opacity 0.3s ease, transform 0.3s ease;
            position: relative;
            z-index: 2;
        }

        .feature-card:hover p:first-of-type {
            opacity: 1;
            transform: translateY(0);
        }

        /* Replace your existing feature-explanation styles with these */
        .feature-explanation {
            padding-top: 1rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 1rem;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.5s ease;
            max-height: 0;
            overflow: hidden;
            /* Add delay for second stage */
            transition-delay: 0.3s;
        }

        .feature-card:hover .feature-explanation {
            opacity: 1;
            transform: translateY(0);
            max-height: 200px;
        }

        /* Add this new indicator style */
        .feature-card::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 2px;
            background: #4a90e2;
            transition: width 0.3s ease;
        }

        .feature-card:hover::after {
            width: 90%;
        }

        /* Add loading indicator animation */
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }

        .feature-card:hover::before {
            animation: pulse 2s infinite;
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
                 <img src="../images/1.jpeg" alt="Home Banner" class="hero-image">
        
                <h1>Transform Your Learning Journey</h1>
                <p>Welcome to TutorTeach.ai - Your AI-powered learning companion that adapts to your unique needs.</p>
                <button class="button" onclick="startJourney()">Start Your Journey</button>
            </section>
            <section class="why-choose-us">
                <h2>Why Choose Us?</h2>
                <div class="grid">
                    <div class="card slide-in-left">
                        <h2>Personalized Learning</h2>
                        <p>AI-driven content tailored to your learning style and pace.</p>
                    </div>
                    <div class="card slide-in-right">
                        <h2>Interactive Lessons</h2>
                        <p>Engage with dynamic content and real-time feedback.</p>
                    </div>
                    <div class="card slide-in-left">
                        <h2>Progress Tracking</h2>
                        <p>Monitor your growth with detailed analytics and insights.</p>
                    </div>
                    <div class="card slide-in-right">
                        <h2>AI-Generated Video Content</h2>
                        <p>Generates tailored video lessons based on the user's selected topic, providing an engaging and dynamic learning experience.</p>
                    </div>
                    <div class="card slide-in-left">
                        <h2>Knowledge Assessment</h2>
                        <p>Creates fill-in-the-blank and other interactive questions to test user understanding of the selected topic, predicting scores based on responses.</p>
                    </div>
                    <div class="card slide-in-right">
                        <h2>Strength and Weakness Analysis</h2>
                        <p>Identifies the user’s stronger and weaker sections in the chosen topic to provide personalized insights for improvement.</p>
                    </div>
                    <div class="card slide-in-left">
                        <h2>Focused Remedial Content</h2>
                        <p>Generates additional video solutions focusing on weaker sections, ensuring comprehensive understanding and mastery of the topic.</p>
                    </div>
                    <div class="card slide-in-right">
                        <h2>Holistic Learning Support</h2>
                        <p>Monitors individual performance to teach values, ethics, discipline, and communication skills alongside academic content, fostering overall development.</p>
                    </div>
                </div>
            </section>
                <section class="testimonials">
                <h2>What Our Users Say</h2>
                <div class="testimonials-scroll">
                    <div class="testimonial-card">
                        <img src="https://i.ibb.co/PjZVfr3/Screenshot-2025-01-08-052901.png"  alt="User 1">
                        <h3>Karthik</h3>
                        <p>"TutorTeach.ai has completely transformed the way I learn. The personalized lessons are amazing!"</p>
                    </div>
                    <div class="testimonial-card">
                        <img src="https://i.ibb.co/RHpQ4tK/vkr.jpg" alt="User 2">
                        <h3>Vinodh Kumar</h3>
                        <p>"The AI-generated videos are so engaging. I’ve never enjoyed learning this much before!"</p>
                    </div>
                    <div class="testimonial-card">
                        <img src="https://i.ibb.co/MBLrSTQ/karna.jpg" " alt="User 3">
                        <h3>Karuna Karan</h3>
                        <p>"The progress tracking feature helps me stay motivated and focused on my goals."</p>
                    </div>
                    <div class="testimonial-card">
                        <img src="https://i.ibb.co/Jcxy1JW/vijay.jpg" alt="User 4">
                        <h3>Vijay</h3>
                        <p>"The AI-driven content is tailored perfectly to my learning style. Highly recommended!"</p>
                    </div>
                    <div class="testimonial-card">
                        <img src="https://i.ibb.co/hd1bNRn/nikhil.jpg" alt="User 5">
                        <h3>Nikhil</h3>
                        <p>"The interactive lessons and real-time feedback have made learning so much more effective."</p>
                    </div>
                </div>
            </section>
            <section class="ai-stats">
                <h2>AI Stats</h2>
                <div class="stats-grid">
                    <div class="stat">
                        <h3 id="topics-covered">0</h3>
                        <p>Topics Covered</p>
                    </div>
                    <div class="stat">
                        <h3 id="students-benefited">0</h3>
                        <p>Students Benefited</p>
                    </div>
                    <div class="stat">
                        <h3 id="satisfaction-rate">0</h3>
                        <p>Satisfaction Rate</p>
                    </div>
                </div>
            </section>
            <section class="video-demo">
                <h2>How It Works</h2>
                <div class="video-container">
                    <iframe width="100%" height="400" src="https://www.youtube.com/embed/nKl2FgALO-c" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                </div>
            </section>
            <section class="about-developers">
                <h2>About Developers</h2>
                <div class="developers-grid">
                    <div class="developer-card">
                        <img src="https://i.ibb.co/6Nr58md/myprofile1.jpg" alt="My Profile">
                        <h3>J Madhan</h3>
                        <p>AI & Machine Learning Expert, GEN_AI Explorer </p>
                        <div class="social-links">
                            <a href="https://www.linkedin.com/in/j-madhan-6b90a32b1" target="_blank"><i class="fab fa-linkedin"></i></a>
                            <a href="https://www.instagram.com/_officialmadhan?igsh=ZjFjaXg3a21jZmw0" target="_blank"><i class="fab fa-instagram"></i></a>
                        </div>
                    </div>
                    <div class="developer-card">
                        <img src="https://i.postimg.cc/50qpjsc6/ram.jpg" alt="profile">
                        <h3> N L Ram Charan Teja </h3>
                        <p>Full Stack Developer</p>
                        <div class="social-links">
                            <a href="https://www.linkedin.com/in/n-l-ram-charan-teja-ba2b25288/" target="_blank"><i class="fab fa-linkedin"></i></a>
                            <a href="https://www.instagram.com/ramcharanteja_nl?igsh=MWJncmNhNnpuNDVndQ==" target="_blank"><i class="fab fa-instagram"></i></a>
                        </div>
                    </div>
                    <div class="developer-card">
                        <img src="https://i.ibb.co/18XVx3D/Whats-App-Image-2025-01-07-at-21-09-01-6e1dc378.jpg" alt="Developer 3">
                        <h3>M Praveen</h3>
                        <p>UI/UX Designer</p>
                        <div class="social-links">
                            <a href="https://www.linkedin.com/in/m-praveen-kumar-64bb19315?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app" target="_blank"><i class="fab fa-linkedin"></i></a>
                            <a href="https://www.instagram.com/professional_praveen3?igsh=MzNwOTk2M2FwanE3" target="_blank"><i class="fab fa-instagram"></i></a>
                        </div>
                    </div>
                    <div class="developer-card">
                        <img src="https://i.ibb.co/fMSncvP/Whats-App-Image-2025-01-07-at-20-57-53-31232a64.jpg" alt="Developer 4">
                        <h3>K Harsha Vardhan</h3>
                        <p>Backend Developer</p>
                        <div class="social-links">
                            <a href="https://linkedin.com/in/bobbrown" target="_blank"><i class="fab fa-linkedin"></i></a>
                            <a href="https://www.instagram.com/harsha_harry._?igsh=MWVpM3Vxanl0N2pkZQ==" target="_blank"><i class="fab fa-instagram"></i></a>
                        </div>
                    </div>
                </div>
            </section>
            <section class="contact-us">
                <h2>Contact Us</h2>
                <div class="contact-form">
                    <form onsubmit="handleContactForm(event)">
                        <div class="form-group">
                            <label for="contactName">Name</label>
                            <input type="text" id="contactName" required>
                        </div>
                        <div class="form-group">
                            <label for="contactEmail">Email</label>
                            <input type="email" id="contactEmail" required>
                        </div>
                        <div class="form-group">
                            <label for="contactMessage">Message</label>
                            <textarea id="contactMessage" required></textarea>
                        </div>
                        <button type="submit" class="button">Send Message</button>
                    </form>
                </div>
            </section>
            <section class="whats-new">
                <h2>What's New</h2>
                <div class="grid">
                    <div class="card">
                        <h3>Latest Innovations and Updates in AI and Technology</h3>
                        <p>Explore advanced AI solutions like TutorTeach.ai and Teachmate.ai.</p>
                    </div>
                    <div class="card">
                        <h3>AI-Based Learning Solutions</h3>
                        <p>Real-time AI models for personalized education. Tools for assignment creation, video learning, and student progress tracking.</p>
                    </div>
                    <div class="card">
                        <h3>Explore Our Features</h3>
                        <p>Topic Selection: Choose from a wide range of educational topics. Video Generation: AI-generated video content for in-depth learning. Knowledge Assessment: Interactive quizzes and score prediction. Performance Insights: Identify strengths and weaknesses in learning. Customized Solutions: AI-based feedback to improve weak areas.</p>
                    </div>
                    <div class="card">
                        <h3>For Educators and Institutions</h3>
                        <p>Comprehensive Tools: Create, track, and enhance student engagement. Development Programs: Enhance teaching methodologies using AI. Integration Options: Seamlessly integrate with existing systems like Microsoft Teams and Azure.</p>
                    </div>
                    <div class="card">
                        <h3>For Students and Parents</h3>
                        <p>Exclusive deals on AI-based educational tools. Free access to Azure and learning platforms for students. Personalized learning experiences with real-time feedback.</p>
                    </div>
                    <div class="card">
                        <h3>Developer & IT</h3>
                        <p>Access APIs for AI video processing, student tracking, and quiz generation. Explore open-source tools like TensorFlow, Hugging Face, and Flask. Documentation and tutorials for seamless integration into educational environments.</p>
                    </div>
                    <div class="card">
                        <h3>Get Involved</h3>
                        <p>Participate in educational hackathons and competitions. Leverage cloud solutions for scalable learning platforms. Stay updated with community support and insights.</p>
                    </div>
                    <div class="card">
                        <h3>About Us</h3>
                        <p>Innovating education with AI-powered tools. Committed to privacy, sustainability, and accessibility. Partnering with global leaders to redefine learning experiences.</p>
                    </div>
                </div>
            </section>
            <div class="bubbles">
                <li></li>
                <li></li>
                <li></li>
                <li></li>
                <li></li>
                <li></li>
                <li></li>
                <li></li>
                <li></li>
                <li></li>
            </div>
        </div>

        <!-- Features Page -->
        <div id="features-page" class="page">
            <section class="hero">
                <h1>Our Features</h1>
                <div class="grid">
                    <!-- Personalized Learning -->
                    <div class="feature-card slide-in-left">
                        <div class="feature-icon">
                            <i class="fas fa-user-graduate"></i>
                        </div>
                        <h2>Personalized Learning</h2>
                        <p>AI-driven content tailored to your learning style and pace.</p>
                        <div class="feature-explanation">
                            <p>Our AI analyzes your learning patterns and adapts the content to match your strengths and weaknesses, ensuring a personalized learning experience.</p>
                        </div>
                    </div>

                    <!-- Interactive Lessons -->
                    <div class="feature-card slide-in-right">
                        <div class="feature-icon">
                            <i class="fas fa-chalkboard-teacher"></i>
                        </div>
                        <h2>Interactive Lessons</h2>
                        <p>Engage with dynamic content and real-time feedback.</p>
                        <div class="feature-explanation">
                            <p>Interactive lessons with quizzes, polls, and real-time feedback keep you engaged and help reinforce your understanding of the topic.</p>
                        </div>
                    </div>

                    <!-- Progress Tracking -->
                    <div class="feature-card slide-in-left">
                        <div class="feature-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <h2>Progress Tracking</h2>
                        <p>Monitor your growth with detailed analytics and insights.</p>
                        <div class="feature-explanation">
                            <p>Track your progress with detailed analytics, including completed lessons, quiz scores, and time spent on each topic.</p>
                        </div>
                    </div>

                    <!-- AI-Generated Video -->
                    <div class="feature-card slide-in-right">
                        <div class="feature-icon">
                            <i class="fas fa-video"></i>
                        </div>
                        <h2>AI-Generated Video</h2>
                        <p>Generates tailored video lessons based on your selected topic.</p>
                        <div class="feature-explanation">
                            <p>Our AI creates custom video lessons tailored to your learning needs, making complex topics easier to understand.</p>
                        </div>
                    </div>

                    <!-- Knowledge Assessment -->
                    <div class="feature-card slide-in-left">
                        <div class="feature-icon">
                            <i class="fas fa-question-circle"></i>
                        </div>
                        <h2>Knowledge Assessment</h2>
                        <p>Tests your understanding with interactive questions.</p>
                        <div class="feature-explanation">
                            <p>Take quizzes and tests to assess your knowledge. Our AI predicts your score and provides feedback to help you improve.</p>
                        </div>
                    </div>

                    <!-- Strength and Weakness Analysis -->
                    <div class="feature-card slide-in-right">
                        <div class="feature-icon">
                            <i class="fas fa-balance-scale"></i>
                        </div>
                        <h2>Strength and Weakness Analysis</h2>
                        <p>Identifies your stronger and weaker sections.</p>
                        <div class="feature-explanation">
                            <p>Our AI analyzes your performance to identify your strengths and weaknesses, helping you focus on areas that need improvement.</p>
                        </div>
                    </div>

                    <!-- Focused Remedial Content -->
                    <div class="feature-card slide-in-left">
                        <div class="feature-icon">
                            <i class="fas fa-book-open"></i>
                        </div>
                        <h2>Focused Remedial Content</h2>
                        <p>Generates additional content for weaker sections.</p>
                        <div class="feature-explanation">
                            <p>Get additional video lessons and practice questions tailored to your weaker sections to ensure comprehensive understanding.</p>
                        </div>
                    </div>

                    <!-- Holistic Learning Support -->
                    <div class="feature-card slide-in-right">
                        <div class="feature-icon">
                            <i class="fas fa-hands-helping"></i>
                        </div>
                        <h2>Holistic Learning Support</h2>
                        <p>Teaches values, ethics, and communication skills.</p>
                        <div class="feature-explanation">
                            <p>Beyond academics, our platform helps you develop values, ethics, discipline, and communication skills for overall growth.</p>
                        </div>
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
                    <div class="learning-path-nav">
                        <button class="button" onclick="previousTopic()">Previous</button>
                        <button class="button" onclick="startQuiz()" id="next-button" disabled>Take Quiz</button>
                    </div>
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
                    <div class="form-group">
                        <label for="loginClass">Select Class</label>
                        <select id="loginClass" required>
                            <option value="8th">8th</option>
                            <option value="9th">9th</option>
                            <option value="10th">10th</option>
                        </select>
                    </div>
                    <button type="submit" class="button">Login</button>
                    <div id="loginMessage"></div>
                </form>
                <div class="auth-switch">
                   Don't have an account? <a onclick="showPage('register')">Register</a>
                </div>
                <div class="auth-switch">
                    Forgot Password? <a onclick="showPage('forgot-password')">Reset Password</a>
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
                    <div class="form-group">
                        <label for="registerClass">Select Class</label>
                        <select id="registerClass" required>
                            <option value="8th">8th</option>
                            <option value="9th">9th</option>
                            <option value="10th">10th</option>
                        </select>
                    </div>
                    <button type="submit" class="button">Register</button>
                    <div id="registerMessage"></div>
                </form>
                <div class="auth-switch">
                    Already have an account? <a onclick="showPage('login')">Login</a>
                </div>
            </div>
        </div>

        <!-- Forgot Password Page -->
        <div id="forgot-password-page" class="page">
            <div class="auth-container">
                <h2 class="text-2xl font-bold mb-4 text-center">Forgot Password</h2>
                <form class="auth-form" onsubmit="handleForgotPassword(event)">
                    <div class="form-group">
                        <label for="forgotEmail">Email</label>
                        <input type="email" id="forgotEmail" required>
                    </div>
                    <button type="submit" class="button">Send OTP</button>
                    <div id="forgotMessage"></div>
                </form>
                <div class="auth-switch">
                    Remember your password? <a onclick="showPage('login')">Login</a>
                </div>
            </div>
        </div>

        <!-- Reset Password Page -->
        <div id="reset-password-page" class="page">
            <div class="auth-container">
                <h2 class="text-2xl font-bold mb-4 text-center">Reset Password</h2>
                <form class="auth-form" onsubmit="handleResetPassword(event)">
                    <div class="form-group">
                        <label for="resetOTP">OTP</label>
                        <input type="text" id="resetOTP" required>
                    </div>
                    <div class="form-group">
                        <label for="newPassword">New Password</label>
                        <input type="password" id="newPassword" required>
                    </div>
                    <div class="form-group">
                        <label for="confirmNewPassword">Confirm New Password</label>
                        <input type="password" id="confirmNewPassword" required>
                    </div>
                    <button type="submit" class="button">Reset Password</button>
                    <div id="resetMessage"></div>
                </form>
            </div>
        </div>
    </main>

    <!-- Footer Section -->
    <footer>
        <div class="footer-links">
            <a href="#">Terms of Service</a>
            <a href="#">Privacy Policy</a>
            <a href="#">FAQs</a>
        </div>
        <div class="social-icons">
            <a href="#"><i class="fab fa-linkedin"></i></a>
            <a href="#"><i class="fab fa-twitter"></i></a>
            <a href="#"><i class="fab fa-facebook"></i></a>
            <a href="#"><i class="fab fa-instagram"></i></a>
        </div>
        <div class="copyright">
            © 2025 TutorTeach.ai. All Rights Reserved.
        </div>
    </footer>

    <!-- Live Chat Icon -->
    <div class="live-chat" onclick="openChat()">
        <i class="fas fa-comment"></i>
    </div>

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
        let otp = null;

        // Update auth button based on login status
        function updateAuthButton() {
            const authButton = document.getElementById('authButton');
            if (currentUser) {
                authButton.innerHTML = `<i class="fas fa-user"></i> ${currentUser.displayName || currentUser.name}`;
            } else {
                authButton.innerHTML = `<i class="fas fa-user"></i> Login`;
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
            const selectedClass = document.getElementById('registerClass').value;

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

            users.push({ name, email, password, class: selectedClass });
            localStorage.setItem('users', JSON.stringify(users));
            
            messageDiv.className = 'success-message';
            messageDiv.textContent = 'Registration successful! Redirecting to login...';
            
            // Send registration confirmation email
            sendEmail(email, 'Registration Successful', 'You have successfully registered to TutorTeach.ai.');
            
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
            const selectedClass = document.getElementById('loginClass').value;

            const user = users.find(u => u.email === email && u.password === password);
            
            if (user) {
                currentUser = user;
                currentUser.class = selectedClass; // Update user's class
                localStorage.setItem('currentUser', JSON.stringify(user));
                updateAuthButton();
                
                messageDiv.className = 'success-message';
                messageDiv.textContent = 'Login successful! Redirecting...';
                
                setTimeout(() => {
                    showPage('learning-path');
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

        // Handle forgot password
        function handleForgotPassword(event) {
            event.preventDefault();
            const messageDiv = document.getElementById('forgotMessage');
            const email = document.getElementById('forgotEmail').value;

            const user = users.find(u => u.email === email);
            
            if (user) {
                otp = generateOTP();
                sendEmail(email, 'Password Reset OTP', `Your OTP for password reset is: ${otp}`);
                
                messageDiv.className = 'success-message';
                messageDiv.textContent = 'OTP sent to your email.';
                showPage('reset-password');
            } else {
                messageDiv.className = 'error-message';
                messageDiv.textContent = 'Email not found!';
            }
        }

        // Handle reset password
        function handleResetPassword(event) {
            event.preventDefault();
            const messageDiv = document.getElementById('resetMessage');
            const enteredOTP = document.getElementById('resetOTP').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmNewPassword = document.getElementById('confirmNewPassword').value;

            if (enteredOTP !== otp) {
                messageDiv.className = 'error-message';
                messageDiv.textContent = 'Invalid OTP!';
                return;
            }

            if (newPassword !== confirmNewPassword) {
                messageDiv.className = 'error-message';
                messageDiv.textContent = 'Passwords do not match!';
                return;
            }

            const user = users.find(u => u.email === document.getElementById('forgotEmail').value);
            user.password = newPassword;
            localStorage.setItem('users', JSON.stringify(users));
            
            messageDiv.className = 'success-message';
            messageDiv.textContent = 'Password reset successful! Redirecting to login...';
            
            setTimeout(() => {
                showPage('login');
            }, 2000);
        }

        // Generate OTP
        function generateOTP() {
            return Math.floor(100000 + Math.random() * 900000).toString();
        }

        // Send email
        function sendEmail(to, subject, body) {
            const msg = Message(subject, recipients=[to], body=body);
            mail.send(msg);
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
                        <div class="card ${currentUser && currentUser.class !== className ? 'blurred' : ''}" onclick="selectClass('${className}')">
                            <h2 class="card-title">Class ${className}</h2>
                            <p class="card-content">Explore subjects and topics for Class ${className}</p>
                        </div>
                    `).join('');
                });
        }

        // Select a class
        function selectClass(className) {
            if (currentUser && currentUser.class !== className) {
                alert('You can only access your registered class.');
                return;
            }
            currentClass = className;
            fetch(`/api/subjects/${className}`)
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
            fetch(`/api/topics/${currentClass}/${subject}`)
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
            fetch(`/api/content/${topic}`)
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
            contentContainer.innerHTML = '';
            const words = content.split(' ');
            let index = 0;
            
            const interval = setInterval(() => {
                if (index >= words.length) {
                    clearInterval(interval);
                    document.getElementById('mark-complete-button').disabled = false;
                    return;
                }
                contentContainer.innerHTML += words[index] + ' ';
                index++;
            }, 300); // Changed from 50 to 300 milliseconds
        }
        // Mark a topic as complete
        function markComplete() {
            contentComplete = true;
            document.getElementById('content-section').classList.add('hidden');
            document.getElementById('video-section').classList.remove('hidden');
            fetch(`/api/video/${currentTopic}`)
                .then(response => response.json())
                .then(data => {
                    if (data.video_path) {
                        const videoPlayer = document.getElementById('video-player');
                        videoPlayer.src = `/videos/${data.video_path}`;
                        videoPlayer.load();       
                        videoPlayer.play();
                        document.getElementById('next-button').disabled = false; // Enable "Next" button
                    } else {
                        alert('No video available for this topic.');
                    }
                });
        }

        // Navigate to the next topic
        function nextTopic() {
            const topics = education_data['classes'][currentClass]['subjects'][currentSubject]['topics'];
            const currentIndex = topics.indexOf(currentTopic);
            if (currentIndex < topics.length - 1) {
                selectTopic(topics[currentIndex + 1]);
            } else {
                alert('No more topics in this subject.');
            }
        }

        // Navigate to the previous topic
        function previousTopic() {
            const topics = education_data['classes'][currentClass]['subjects'][currentSubject]['topics'];
            const currentIndex = topics.indexOf(currentTopic);
            if (currentIndex > 0) {
                selectTopic(topics[currentIndex - 1]);
            } else {
                alert('This is the first topic.');
            }
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
            if (currentClass) path.push(`Class ${currentClass}`);
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

        // Open live chat
        function openChat() {
            alert("Live chat feature coming soon!");
        }

        // Handle contact form submission
        function handleContactForm(event) {
            event.preventDefault();
            const name = document.getElementById('contactName').value;
            const email = document.getElementById('contactEmail').value;
            const message = document.getElementById('contactMessage').value;

            // Send email to TutorTeach.ai
            sendEmail('tutorteach.ai@gmail.com', 'New Contact Form Submission', `
                Name: ${name}
                Email: ${email}
                Message: ${message}
            `);

            alert("Thank you for contacting us! We will get back to you soon.");
        }

        // AI Stats Counter Animation
        function animateStats() {
            const topicsCovered = document.getElementById('topics-covered');
            const studentsBenefited = document.getElementById('students-benefited');
            const satisfactionRate = document.getElementById('satisfaction-rate');

            const stats = [
                { element: topicsCovered, target: 100, duration: 2000 },
                { element: studentsBenefited, target: 5000, duration: 2000 },
                { element: satisfactionRate, target: 95, duration: 2000 }
            ];

            stats.forEach(stat => {
                let start = 0;
                const increment = stat.target / (stat.duration / 10);
                const interval = setInterval(() => {
                    start += increment;
                    stat.element.textContent = Math.floor(start);
                    if (start >= stat.target) {
                        clearInterval(interval);
                        stat.element.textContent = stat.target;
                    }
                }, 10);
            });
        }

        // Initialize AI Stats Animation
        animateStats();

        // Start Journey Button
        function startJourney() {
            if (!currentUser) {
                showPage('login');
            } else {
                showPage('learning-path');
            }
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
    app.run(debug=True, host='0.0.0.0', port=5000)
