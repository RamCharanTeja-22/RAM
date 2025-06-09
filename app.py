from flask import Flask, render_template, request, jsonify,render_template_string
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import random
from deap import base, creator, tools, algorithms
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from typing import List, Dict, Tuple, Any
import warnings
import io
import base64
import json
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

@dataclass
class SymbolicRule:
    """Represents a symbolic IF-THEN rule for medical diagnosis"""
    feature: str
    operator: str  # '>', '<', '>=', '<=', '=='
    threshold: float
    prediction: int
    confidence: float

    def evaluate(self, patient_data: Dict[str, float]) -> Tuple[bool, int, float]:
        """Evaluate rule against patient data"""
        feature_value = patient_data.get(self.feature, 0)

        if self.operator == '>':
            applies = feature_value > self.threshold
        elif self.operator == '<':
            applies = feature_value < self.threshold
        elif self.operator == '>=':
            applies = feature_value >= self.threshold
        elif self.operator == '<=':
            applies = feature_value <= self.threshold
        else:  # ==
            applies = abs(feature_value - self.threshold) < 0.1

        return applies, self.prediction, self.confidence

    def __str__(self):
        return f"IF {self.feature} {self.operator} {self.threshold:.2f} THEN diagnosis={self.prediction} (conf={self.confidence:.2f})"

class MedicalDatasetGenerator:
    """Generate synthetic medical dataset with realistic patterns"""

    def __init__(self, n_samples=1000):
        self.n_samples = n_samples
        self.feature_names = [
            'age', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'cholesterol', 'blood_sugar', 'heart_rate', 'bmi',
            'exercise_hours_per_week', 'smoking_years', 'family_history'
        ]
        self.conditions = ['Healthy', 'Diabetes', 'Heart Disease', 'Hypertension']

    def generate_dataset(self):
        """Generate realistic medical dataset"""
        data = []
        labels = []

        for _ in range(self.n_samples):
            # Base patient profile
            age = np.random.normal(45, 15)
            age = max(18, min(90, age))

            # Generate correlated features
            # Healthy patients (25%)
            if np.random.random() < 0.25:
                bp_sys = np.random.normal(120, 10)
                bp_dia = np.random.normal(80, 8)
                cholesterol = np.random.normal(180, 20)
                blood_sugar = np.random.normal(90, 10)
                heart_rate = np.random.normal(70, 10)
                bmi = np.random.normal(22, 3)
                exercise = np.random.normal(4, 2)
                smoking = 0 if np.random.random() > 0.2 else np.random.normal(2, 3)
                family_hist = 1 if np.random.random() < 0.3 else 0
                label = 0  # Healthy

            # Diabetes patients (25%)
            elif np.random.random() < 0.33:
                bp_sys = np.random.normal(140, 15)
                bp_dia = np.random.normal(90, 10)
                cholesterol = np.random.normal(220, 30)
                blood_sugar = np.random.normal(160, 40)  # High blood sugar
                heart_rate = np.random.normal(75, 12)
                bmi = np.random.normal(28, 4)  # Higher BMI
                exercise = np.random.normal(2, 1.5)  # Less exercise
                smoking = np.random.normal(8, 5) if np.random.random() > 0.4 else 0
                family_hist = 1 if np.random.random() < 0.6 else 0  # Higher family history
                label = 1  # Diabetes

            # Heart Disease patients (25%)
            elif np.random.random() < 0.5:
                bp_sys = np.random.normal(150, 20)
                bp_dia = np.random.normal(95, 12)
                cholesterol = np.random.normal(240, 35)  # High cholesterol
                blood_sugar = np.random.normal(100, 15)
                heart_rate = np.random.normal(80, 15)
                bmi = np.random.normal(27, 4)
                exercise = np.random.normal(1.5, 1)  # Low exercise
                smoking = np.random.normal(12, 6) if np.random.random() > 0.3 else 0
                family_hist = 1 if np.random.random() < 0.7 else 0
                label = 2  # Heart Disease

            # Hypertension patients (25%)
            else:
                bp_sys = np.random.normal(160, 20)  # High BP
                bp_dia = np.random.normal(100, 15)  # High BP
                cholesterol = np.random.normal(200, 25)
                blood_sugar = np.random.normal(95, 12)
                heart_rate = np.random.normal(75, 12)
                bmi = np.random.normal(26, 4)
                exercise = np.random.normal(2.5, 1.5)
                smoking = np.random.normal(6, 4) if np.random.random() > 0.5 else 0
                family_hist = 1 if np.random.random() < 0.5 else 0
                label = 3  # Hypertension

            # Ensure realistic bounds
            patient = [
                max(18, min(90, age)),
                max(80, min(200, bp_sys)),
                max(50, min(120, bp_dia)),
                max(120, min(350, cholesterol)),
                max(60, min(300, blood_sugar)),
                max(50, min(120, heart_rate)),
                max(15, min(45, bmi)),
                max(0, min(10, exercise)),
                max(0, smoking),  # Can be 0
                family_hist
            ]

            data.append(patient)
            labels.append(label)

        df = pd.DataFrame(data, columns=self.feature_names)
        df['diagnosis'] = labels
        return df
HTML_TEMPLATE='''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neuro-Symbolic Medical Diagnosis System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            animation: backgroundShift 10s ease-in-out infinite alternate;
        }

        @keyframes backgroundShift {
            0% { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            100% { background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 24px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3498db 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"><animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite"/></circle><circle cx="80" cy="30" r="1.5" fill="rgba(255,255,255,0.1)"><animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite" begin="1s"/></circle><circle cx="40" cy="70" r="1" fill="rgba(255,255,255,0.1)"><animate attributeName="opacity" values="0;1;0" dur="4s" repeatCount="indefinite" begin="2s"/></circle></svg>');
            pointer-events: none;
        }

        .header h1 {
            font-size: 3em;
            margin-bottom: 15px;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
            font-weight: 700;
            letter-spacing: -1px;
            position: relative;
            z-index: 1;
        }

        .header p {
            font-size: 1.3em;
            opacity: 0.95;
            font-weight: 300;
            position: relative;
            z-index: 1;
        }

        .system-status {
            display: inline-flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 25px;
            margin-top: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #e74c3c;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }

        .status-indicator.trained {
            background: #27ae60;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            padding: 40px;
        }

        .section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #3498db, #2ecc71, #f39c12, #e74c3c);
            background-size: 300% 100%;
            animation: gradientShift 3s ease-in-out infinite;
        }

        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        .section:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
        }

        .section h2 {
            color: #2c3e50;
            margin-bottom: 25px;
            font-size: 1.8em;
            font-weight: 600;
            position: relative;
            padding-bottom: 15px;
        }

        .section h2::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 50px;
            height: 3px;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            border-radius: 2px;
        }

        .train-section {
            text-align: center;
        }

        .btn {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            border: none;
            padding: 18px 36px;
            border-radius: 50px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.4s ease;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
            min-width: 200px;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 25px rgba(52, 152, 219, 0.4);
        }

        .btn:active {
            transform: translateY(-1px);
        }

        .btn:disabled {
            background: linear-gradient(135deg, #bdc3c7, #95a5a6);
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .btn-success {
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        }

        .btn-success:hover {
            box-shadow: 0 15px 25px rgba(39, 174, 96, 0.4);
        }

        .form-group {
            margin-bottom: 25px;
            position: relative;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 600;
            font-size: 0.95em;
            transition: color 0.3s ease;
        }

        .form-group input, .form-group select {
            width: 100%;
            padding: 15px 18px;
            border: 2px solid #ecf0f1;
            border-radius: 12px;
            font-size: 1em;
            transition: all 0.3s ease;
            background: #fafbfc;
        }

        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #3498db;
            background: white;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
            transform: translateY(-1px);
        }

        .form-group input:focus + .form-group label,
        .form-group select:focus + .form-group label {
            color: #3498db;
        }

        .feature-info {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
        }

        .feature-info h3 {
            color: #495057;
            margin-bottom: 10px;
            font-size: 1.1em;
        }

        .feature-info p {
            color: #6c757d;
            font-size: 0.9em;
            line-height: 1.4;
        }

        .status {
            margin: 25px 0;
            padding: 18px;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .status::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: currentColor;
            animation: statusSlide 1.5s ease-in-out;
        }

        @keyframes statusSlide {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        .status.success {
            background: linear-gradient(135deg, #d5edda 0%, #c3e6cb 100%);
            color: #155724;
            border: 2px solid #c3e6cb;
        }

        .status.error {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            color: #721c24;
            border: 2px solid #f5c6cb;
        }

        .status.info {
            background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
            color: #0c5460;
            border: 2px solid #bee5eb;
        }

        .loading {
            display: inline-block;
            width: 24px;
            height: 24px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-top: 3px solid currentColor;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 12px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .results {
            margin-top: 25px;
        }

        .prediction-result {
            background: linear-gradient(135deg, #e8f8f5 0%, #d5f4e6 100%);
            border: 3px solid #27ae60;
            border-radius: 16px;
            padding: 25px;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
            animation: slideIn 0.5s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .prediction-result::before {
            content: '🏥';
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 2em;
            opacity: 0.3;
        }

        .diagnosis {
            font-size: 1.5em;
            font-weight: 700;
            color: #27ae60;
            margin-bottom: 15px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
        }

        .explanation {
            color: #2c3e50;
            font-style: italic;
            line-height: 1.6;
            background: rgba(255, 255, 255, 0.7);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }

        .rules-list {
            max-height: 400px;
            overflow-y: auto;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #dee2e6;
        }

        .rules-list::-webkit-scrollbar {
            width: 8px;
        }

        .rules-list::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }

        .rules-list::-webkit-scrollbar-thumb {
            background: #3498db;
            border-radius: 4px;
        }

        .rule-item {
            background: white;
            margin: 12px 0;
            padding: 16px;
            border-radius: 10px;
            border-left: 5px solid #3498db;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-size: 0.9em;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .rule-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .accuracy-display {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 3px solid #f0ad4e;
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
        }

        .accuracy-display::before {
            content: '📊';
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 2em;
            opacity: 0.3;
        }

        .accuracy-display .accuracy-value {
            font-size: 2.5em;
            font-weight: 800;
            color: #e67e22;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }

        .accuracy-label {
            font-size: 1.1em;
            color: #d68910;
            font-weight: 600;
            margin-top: 5px;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .hidden {
            display: none;
        }

        .tabs {
            display: flex;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px;
            padding: 5px;
            border: 1px solid #dee2e6;
        }

        .tab {
            flex: 1;
            padding: 12px 20px;
            text-align: center;
            background: transparent;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            color: #6c757d;
        }

        .tab.active {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .progress-bar {
            width: 100%;
            height: 6px;
            background: #ecf0f1;
            border-radius: 3px;
            overflow: hidden;
            margin: 15px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 3px;
        }

        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
                gap: 30px;
                padding: 30px;
            }
        }

        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 16px;
            }

            .main-content {
                padding: 20px;
                gap: 20px;
            }

            .form-row {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 2.2em;
            }

            .header p {
                font-size: 1.1em;
            }

            .section {
                padding: 20px;
            }
        }

        .tooltip {
            position: relative;
        }

        .tooltip::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background: #2c3e50;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.8em;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 1000;
        }

        .tooltip:hover::after {
            opacity: 1;
            visibility: visible;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Neuro-Symbolic Medical AI</h1>
            <p>Advanced Hybrid Intelligence for Medical Diagnosis</p>
            <div class="system-status">
                <div class="status-indicator" id="statusIndicator"></div>
                <span id="statusText">System Not Trained</span>
            </div>
        </div>

        <div class="main-content">
            <div class="section train-section">
                <h2>🚀 System Training</h2>
                <div class="feature-info">
                    <h3>Hybrid AI Architecture</h3>
                    <p>This system combines deep neural networks with evolutionary symbolic reasoning to provide explainable medical diagnoses with high accuracy.</p>
                </div>

                <button id="trainBtn" class="btn" onclick="trainSystem()">
                    <span id="trainBtnText">Initialize Training</span>
                </button>

                <div id="trainingProgress" class="hidden">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <p>Training neural networks and evolving symbolic rules...</p>
                </div>

                <div id="trainStatus"></div>

                <div id="accuracyDisplay" class="hidden">
                    <div class="accuracy-display">
                        <div class="accuracy-value" id="accuracyValue">0%</div>
                        <div class="accuracy-label">System Accuracy</div>
                    </div>
                </div>

                <div id="rulesSection" class="hidden">
                    <h3>🔍 Discovered Rules</h3>
                    <div class="rules-list" id="rulesList"></div>
                </div>
            </div>

            <div class="section">
                <h2>🏥 Patient Diagnosis</h2>

                <div class="tabs">
                    <button class="tab active" onclick="switchTab('basic')">Basic Info</button>
                    <button class="tab" onclick="switchTab('vitals')">Vitals</button>
                    <button class="tab" onclick="switchTab('lifestyle')">Lifestyle</button>
                </div>

                <form id="patientForm">
                    <div class="tab-content active" id="basic-content">
                        <div class="form-row">
                            <div class="form-group">
                                <label class="tooltip" data-tooltip="Patient's age in years">Age (years)</label>
                                <input type="number" id="age" min="1" max="120" value="45" required>
                            </div>
                            <div class="form-group">
                                <label class="tooltip" data-tooltip="Body Mass Index calculated from height and weight">BMI</label>
                                <input type="number" id="bmi" step="0.1" min="10" max="50" value="25" required>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="tooltip" data-tooltip="Family history of medical conditions (0=No, 1=Yes)">Family History</label>
                            <select id="family_history" required>
                                <option value="0">No Family History</option>
                                <option value="1">Yes, Family History Present</option>
                            </select>
                        </div>
                    </div>

                    <div class="tab-content" id="vitals-content">
                        <div class="form-row">
                            <div class="form-group">
                                <label class="tooltip" data-tooltip="Systolic blood pressure (top number)">Systolic BP (mmHg)</label>
                                <input type="number" id="blood_pressure_systolic" min="70" max="250" value="120" required>
                            </div>
                            <div class="form-group">
                                <label class="tooltip" data-tooltip="Diastolic blood pressure (bottom number)">Diastolic BP (mmHg)</label>
                                <input type="number" id="blood_pressure_diastolic" min="40" max="150" value="80" required>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label class="tooltip" data-tooltip="Resting heart rate in beats per minute">Heart Rate (bpm)</label>
                                <input type="number" id="heart_rate" min="40" max="200" value="70" required>
                            </div>
                            <div class="form-group">
                                <label class="tooltip" data-tooltip="Blood sugar level in mg/dL">Blood Sugar (mg/dL)</label>
                                <input type="number" id="blood_sugar" min="50" max="400" value="90" required>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="tooltip" data-tooltip="Total cholesterol level in mg/dL">Cholesterol (mg/dL)</label>
                            <input type="number" id="cholesterol" min="100" max="400" value="180" required>
                        </div>
                    </div>

                    <div class="tab-content" id="lifestyle-content">
                        <div class="form-row">
                            <div class="form-group">
                                <label class="tooltip" data-tooltip="Hours of exercise per week">Exercise (hours/week)</label>
                                <input type="number" id="exercise_hours_per_week" step="0.5" min="0" max="20" value="3" required>
                            </div>
                            <div class="form-group">
                                <label class="tooltip" data-tooltip="Number of years of smoking (0 if never smoked)">Smoking Years</label>
                                <input type="number" id="smoking_years" min="0" max="70" value="0" required>
                            </div>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-success" id="predictBtn" disabled>
                        <span id="predictBtnText">🔮 Generate Diagnosis</span>
                    </button>
                </form>

                <div id="predictStatus"></div>
                <div id="results" class="results"></div>
            </div>
        </div>
    </div>

    <script>
        let isSystemTrained = false;

        function switchTab(tabName) {
            // Remove active class from all tabs and contents
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            // Add active class to clicked tab and corresponding content
            event.target.classList.add('active');
            document.getElementById(tabName + '-content').classList.add('active');
        }

        async function trainSystem() {
            const trainBtn = document.getElementById('trainBtn');
            const trainBtnText = document.getElementById('trainBtnText');
            const trainStatus = document.getElementById('trainStatus');
            const trainingProgress = document.getElementById('trainingProgress');
            const progressFill = document.getElementById('progressFill');

            trainBtn.disabled = true;
            trainBtnText.innerHTML = '<div class="loading"></div>Training in Progress';
            trainingProgress.classList.remove('hidden');

            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 95) progress = 95;
                progressFill.style.width = progress + '%';
            }, 300);

            try {
                const response = await fetch('/train', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const data = await response.json();
                clearInterval(progressInterval);
                progressFill.style.width = '100%';

                if (data.success) {
                    trainStatus.innerHTML = `<div class="status success">${data.message}</div>`;

                    // Update system status
                    isSystemTrained = true;
                    document.getElementById('statusIndicator').classList.add('trained');
                    document.getElementById('statusText').textContent = 'System Ready';
                    document.getElementById('predictBtn').disabled = false;

                    // Show accuracy
                    document.getElementById('accuracyDisplay').classList.remove('hidden');
                    document.getElementById('accuracyValue').textContent = data.accuracy + '%';

                    // Show rules
                    if (data.rules && data.rules.length > 0) {
                        document.getElementById('rulesSection').classList.remove('hidden');
                        const rulesList = document.getElementById('rulesList');
                        rulesList.innerHTML = data.rules.map(rule =>
                            `<div class="rule-item">${rule}</div>`
                        ).join('');
                    }

                    trainBtnText.textContent = '✅ System Trained';
                    trainBtn.classList.add('btn-success');
                } else {
                    trainStatus.innerHTML = `<div class="status error">Training failed: ${data.message}</div>`;
                    trainBtn.disabled = false;
                    trainBtnText.textContent = '🔄 Retry Training';
                }
            } catch (error) {
                clearInterval(progressInterval);
                trainStatus.innerHTML = `<div class="status error">Training failed: ${error.message}</div>`;
                trainBtn.disabled = false;
                trainBtnText.textContent = '🔄 Retry Training';
            }

            setTimeout(() => {
                trainingProgress.classList.add('hidden');
            }, 1000);
        }

        document.getElementById('patientForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            if (!isSystemTrained) {
                document.getElementById('predictStatus').innerHTML =
                    '<div class="status error">Please train the system first!</div>';
                return;
            }

            const predictBtn = document.getElementById('predictBtn');
            const predictBtnText = document.getElementById('predictBtnText');
            const predictStatus = document.getElementById('predictStatus');
            const results = document.getElementById('results');

            predictBtn.disabled = true;
            predictBtnText.innerHTML = '<div class="loading"></div>Analyzing...';
            predictStatus.innerHTML = '<div class="status info">🔍 AI is analyzing patient data...</div>';

            const formData = {
                age: document.getElementById('age').value,
                blood_pressure_systolic: document.getElementById('blood_pressure_systolic').value,
                blood_pressure_diastolic: document.getElementById('blood_pressure_diastolic').value,
                cholesterol: document.getElementById('cholesterol').value,
                blood_sugar: document.getElementById('blood_sugar').value,
                heart_rate: document.getElementById('heart_rate').value,
                bmi: document.getElementById('bmi').value,
                exercise_hours_per_week: document.getElementById('exercise_hours_per_week').value,
                smoking_years: document.getElementById('smoking_years').value,
                family_history: document.getElementById('family_history').value
            };

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (data.success) {
                    results.innerHTML = `
                        <div class="prediction-result">
                            <div class="diagnosis">Diagnosis: ${data.diagnosis}</div>
                            <div class="confidence">Confidence: ${data.confidence}%</div>
                            <div class="explanation">
                                <h4>🧠 AI Explanation:</h4>
                                <p>${data.explanation}</p>
                                <p>${data.recommendations}</p>
                            </div>
                        </div>
                    `;
                    predictStatus.innerHTML = `<div class="status success">✅ Diagnosis completed successfully</div>`;
                } else {
                    predictStatus.innerHTML = `<div class="status error">❌ Diagnosis failed: ${data.message}</div>`;
                }
            } catch (error) {
                predictStatus.innerHTML = `<div class="status error">❌ Network error: ${error.message}</div>`;
            }

            predictBtn.disabled = false;
            predictBtnText.innerHTML = '🔮 Generate Diagnosis';
        });

        // Tooltip functionality
        document.querySelectorAll('.tooltip').forEach(element => {
            element.addEventListener('mouseenter', function() {
                this.setAttribute('data-tooltip', this.getAttribute('data-tooltip'));
            });
        });

        // Initialize tabs
        document.querySelectorAll('.tab-content').forEach((content, index) => {
            if (index > 0) content.classList.remove('active');
        });
    </script>
</body>
</html>'''
class NeuroSymbolicEvolutionarySystem:
    """Main system combining neural networks with evolutionary symbolic rules"""

    def __init__(self):
        self.neural_model = None
        self.symbolic_rules = []
        self.feature_names = []
        self.scaler = StandardScaler()
        self.conditions = ['Healthy', 'Diabetes', 'Heart Disease', 'Hypertension']
        self.is_trained = False

        # Setup DEAP for evolutionary algorithm
        if not hasattr(creator, "FitnessMax"):
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()

    def prepare_data(self, df):
        """Prepare dataset for training"""
        X = df.drop('diagnosis', axis=1)
        y = df['diagnosis']
        self.feature_names = X.columns.tolist()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test, X_train, X_test

    def train_neural_model(self, X_train, y_train):
        """Train neural network component"""
        print("Training Neural Network...")
        self.neural_model = MLPClassifier(
            hidden_layer_sizes=(100, 50),
            max_iter=500,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
        self.neural_model.fit(X_train, y_train)
        print(f"Neural Network Training Complete. Iterations: {self.neural_model.n_iter_}")

    def create_individual(self):
        """Create a random symbolic rule (individual for evolution)"""
        feature = random.choice(self.feature_names)
        operator = random.choice(['>', '<', '>=', '<='])

        # Set reasonable thresholds based on feature
        if feature == 'age':
            threshold = random.uniform(20, 80)
        elif 'blood_pressure' in feature:
            threshold = random.uniform(80, 180)
        elif feature == 'cholesterol':
            threshold = random.uniform(150, 300)
        elif feature == 'blood_sugar':
            threshold = random.uniform(70, 200)
        elif feature == 'heart_rate':
            threshold = random.uniform(50, 120)
        elif feature == 'bmi':
            threshold = random.uniform(18, 40)
        elif feature == 'exercise_hours_per_week':
            threshold = random.uniform(0, 8)
        elif feature == 'smoking_years':
            threshold = random.uniform(0, 30)
        else:  # family_history
            threshold = 0.5

        prediction = random.randint(0, 3)
        confidence = random.uniform(0.5, 1.0)

        return [feature, operator, threshold, prediction, confidence]

    def evaluate_rule(self, individual, X_data, y_true):
        """Evaluate fitness of a symbolic rule"""
        feature, operator, threshold, prediction, confidence = individual

        correct_predictions = 0
        total_applicable = 0

        for idx, (i, row) in enumerate(X_data.iterrows()):
            patient_data = row.to_dict()
            rule = SymbolicRule(feature, operator, threshold, prediction, confidence)
            applies, pred, conf = rule.evaluate(patient_data)

            if applies:
                total_applicable += 1
                if pred == y_true.iloc[idx]:
                    correct_predictions += 1

        if total_applicable == 0:
            return (0.0,)  # Rule doesn't apply to any cases

        accuracy = correct_predictions / total_applicable
        coverage = total_applicable / len(X_data)

        # Fitness combines accuracy and coverage
        fitness = accuracy * 0.7 + coverage * 0.3
        return (fitness,)

    def evolve_symbolic_rules(self, X_train_raw, y_train, generations=15):
        """Evolve symbolic rules using genetic algorithm"""
        print("Evolving Symbolic Rules...")

        # Setup toolbox
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.create_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate_rule, X_data=X_train_raw, y_true=y_train)
        self.toolbox.register("mate", self.crossover_rules)
        self.toolbox.register("mutate", self.mutate_rule)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        # Create initial population
        population = self.toolbox.population(n=50)

        # Evaluate initial population
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        # Evolution loop
        for gen in range(generations):
            # Select next generation
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            # Crossover and mutation
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.5:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < 0.2:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate offspring
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            population[:] = offspring

        # Extract best rules
        best_individuals = tools.selBest(population, k=10)
        self.symbolic_rules = []

        for ind in best_individuals:
            feature, operator, threshold, prediction, confidence = ind
            rule = SymbolicRule(feature, operator, threshold, prediction, confidence)
            self.symbolic_rules.append(rule)

        print(f"Evolution Complete. Generated {len(self.symbolic_rules)} rules.")

    def crossover_rules(self, ind1, ind2):
        """Crossover operation for symbolic rules"""
        # Swap random components
        if random.random() < 0.5:
            ind1[0], ind2[0] = ind2[0], ind1[0]  # feature
        if random.random() < 0.5:
            ind1[1], ind2[1] = ind2[1], ind1[1]  # operator
        if random.random() < 0.5:
            ind1[2], ind2[2] = ind2[2], ind1[2]  # threshold
        if random.random() < 0.5:
            ind1[3], ind2[3] = ind2[3], ind1[3]  # prediction

        return ind1, ind2

    def mutate_rule(self, individual):
        """Mutation operation for symbolic rules"""
        mutation_type = random.randint(0, 4)

        if mutation_type == 0:  # Mutate feature
            individual[0] = random.choice(self.feature_names)
        elif mutation_type == 1:  # Mutate operator
            individual[1] = random.choice(['>', '<', '>=', '<='])
        elif mutation_type == 2:  # Mutate threshold
            individual[2] += random.gauss(0, individual[2] * 0.1)
        elif mutation_type == 3:  # Mutate prediction
            individual[3] = random.randint(0, 3)
        else:  # Mutate confidence
            individual[4] = max(0.1, min(1.0, individual[4] + random.gauss(0, 0.1)))

        return (individual,)

    def hybrid_predict(self, X_test_scaled, X_test_raw):
        """Make predictions using hybrid neuro-symbolic approach"""
        neural_preds = self.neural_model.predict_proba(X_test_scaled)
        hybrid_preds = []
        explanations = []

        for i, (neural_prob, row) in enumerate(zip(neural_preds, X_test_raw.iterrows())):
            patient_data = row[1].to_dict()

            # Check if any symbolic rule applies
            applicable_rules = []
            for rule in self.symbolic_rules:
                applies, pred, conf = rule.evaluate(patient_data)
                if applies:
                    applicable_rules.append((rule, pred, conf))

            if applicable_rules:
                # Use symbolic rule with highest confidence
                best_rule, symbolic_pred, confidence = max(applicable_rules, key=lambda x: x[2])

                # Combine neural and symbolic predictions
                neural_pred = np.argmax(neural_prob)
                neural_confidence = np.max(neural_prob)

                # Weighted combination
                if confidence > neural_confidence:
                    final_pred = symbolic_pred
                    explanation = f"Symbolic Rule: {best_rule}"
                else:
                    final_pred = neural_pred
                    explanation = f"Neural Network (conf: {neural_confidence:.3f})"
            else:
                # Use neural network prediction
                final_pred = np.argmax(neural_prob)
                explanation = f"Neural Network (conf: {np.max(neural_prob):.3f})"

            hybrid_preds.append(final_pred)
            explanations.append(explanation)

        return np.array(hybrid_preds), explanations

    def predict_single_patient(self, patient_data):
        """Make prediction for a single patient"""
        if not self.is_trained:
            return None, "System not trained yet"

        # Convert to DataFrame for scaling
        df = pd.DataFrame([patient_data])
        df_scaled = self.scaler.transform(df)

        # Get neural network prediction
        neural_prob = self.neural_model.predict_proba(df_scaled)[0]

        # Check symbolic rules
        applicable_rules = []
        for rule in self.symbolic_rules:
            applies, pred, conf = rule.evaluate(patient_data)
            if applies:
                applicable_rules.append((rule, pred, conf))

        if applicable_rules:
            # Use symbolic rule with highest confidence
            best_rule, symbolic_pred, confidence = max(applicable_rules, key=lambda x: x[2])

            # Combine neural and symbolic predictions
            neural_pred = np.argmax(neural_prob)
            neural_confidence = np.max(neural_prob)

            # Weighted combination
            if confidence > neural_confidence:
                final_pred = symbolic_pred
                explanation = f"Symbolic Rule: {best_rule}"
            else:
                final_pred = neural_pred
                explanation = f"Neural Network (conf: {neural_confidence:.3f})"
        else:
            # Use neural network prediction
            final_pred = np.argmax(neural_prob)
            explanation = f"Neural Network (conf: {np.max(neural_prob):.3f})"

        return final_pred, explanation

# Global system instance
system = NeuroSymbolicEvolutionarySystem()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/train', methods=['POST'])
def train_system():
    try:
        # Generate dataset
        dataset_gen = MedicalDatasetGenerator(n_samples=800)  # Reduced for faster training
        df = dataset_gen.generate_dataset()

        # Prepare data
        X_train_scaled, X_test_scaled, y_train, y_test, X_train_raw, X_test_raw = system.prepare_data(df)

        # Train neural component
        system.train_neural_model(X_train_scaled, y_train)

        # Evolve symbolic rules
        system.evolve_symbolic_rules(X_train_raw, y_train, generations=10)  # Reduced generations

        # Mark as trained
        system.is_trained = True

        # Get accuracy
        hybrid_preds, explanations = system.hybrid_predict(X_test_scaled, X_test_raw)
        accuracy = accuracy_score(y_test, hybrid_preds)

        # Get rules for display
        rules = [str(rule) for rule in system.symbolic_rules[:5]]  # Show top 5 rules

        return jsonify({
            'success': True,
            'accuracy': round(accuracy * 100, 2),
            'rules': rules,
            'message': 'System trained successfully!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Training failed: {str(e)}'
        })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if not system.is_trained:
            return jsonify({
                'success': False,
                'message': 'System not trained yet. Please train the system first.'
            })

        data = request.json

        # Extract patient data
        patient_data = {
            'age': float(data['age']),
            'blood_pressure_systolic': float(data['blood_pressure_systolic']),
            'blood_pressure_diastolic': float(data['blood_pressure_diastolic']),
            'cholesterol': float(data['cholesterol']),
            'blood_sugar': float(data['blood_sugar']),
            'heart_rate': float(data['heart_rate']),
            'bmi': float(data['bmi']),
            'exercise_hours_per_week': float(data['exercise_hours_per_week']),
            'smoking_years': float(data['smoking_years']),
            'family_history': float(data['family_history'])
        }

        # Make prediction
        prediction, explanation = system.predict_single_patient(patient_data)

        if prediction is None:
            return jsonify({
                'success': False,
                'message': explanation
            })

        diagnosis = system.conditions[prediction]

        return jsonify({
            'success': True,
            'diagnosis': diagnosis,
            'explanation': explanation,
            'prediction_code': int(prediction)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Prediction failed: {str(e)}'
        })

@app.route('/get_rules')
def get_rules():
    if not system.is_trained:
        return jsonify({
            'success': False,
            'message': 'System not trained yet.'
        })

    rules = [str(rule) for rule in system.symbolic_rules]
    return jsonify({
        'success': True,
        'rules': rules
    })

if __name__ == '__main__':
    app.run(debug=True)
