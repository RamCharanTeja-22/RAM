import pandas as pd
import numpy as np
from flask import Flask, render_template_string, request, jsonify, send_file
from io import BytesIO
import os
import plotly.graph_objects as go
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

class PerformanceAnalyzer:
    def _init_(self):
        self.initial_data = None
        self.improvement_data = None
        self.model = None
        
    def load_initial_data(self, file):
        if file.filename.endswith('.csv'):
            self.initial_data = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            self.initial_data = pd.read_excel(file)
        else:
            raise ValueError("Invalid file type")
    
    def load_improvement_data(self, file):
        if file.filename.endswith('.csv'):
            self.improvement_data = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            self.improvement_data = pd.read_excel(file)
        else:
            raise ValueError("Invalid file type")
    
    def analyze_performance(self):
        if self.initial_data is None:
            return None
        
        # Feature Engineering: Convert categorical data (e.g., Course Name) to numerical values
        self.initial_data['Course Code'] = self.initial_data['Course Name'].factorize()[0]
        
        # Prepare data for machine learning
        X = self.initial_data[['Marks', 'Course Code']]
        y = self.initial_data['Marks'].apply(lambda x: 1 if x >= 75 else (0 if x >= 60 else -1))  # 1 = Strong, 0 = Average, -1 = Weak
        
        # Split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Train a Random Forest Classifier
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Test the model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Categorize students based on predictions
        student_performance = self.initial_data.copy()
        student_performance['Predicted Category'] = self.model.predict(X[['Marks', 'Course Code']])
        student_performance['Category'] = student_performance['Predicted Category'].apply(
            lambda x: 'Strong' if x == 1 else ('Average' if x == 0 else 'Weak')
        )
        
        return student_performance, accuracy
    
    def recommend_courses(self):
        if self.initial_data is None:
            return None
        
        # We can use a simple rule-based approach or use collaborative filtering
        weak_students = self.initial_data[self.initial_data['Marks'] < 60]
        
        if weak_students.empty:
            return None  # If no weak students, return None
        
        # Sample course recommendation based on current performance
        recommended_courses = {
            'Python Basics': ['Data Structures', 'Algorithm Basics'],
            'SQL Essentials': ['Database Design', 'Advanced SQL'],
            'Java Fundamentals': ['Object Oriented Programming', 'Java Advanced'],
            'C Programming': ['Data Structures in C', 'System Programming']
        }
        
        recommendations = []
        for _, student in weak_students.iterrows():
            current_courses = set(student['Course Name'].split(', '))  # Ensure proper handling of course names
            todo_courses = []
            for course in current_courses:
                if course in recommended_courses:
                    todo_courses.extend(recommended_courses[course])
            
            recommendations.append({
                'Student Name': student['Candidate Name'],
                'Email': student['Candidate Email'],
                'Current Average': f"{student['Marks']:.2f}",
                'Recommended Courses': ', '.join(todo_courses)  # Join list of recommended courses as string
            })
        
        return recommendations
    
    def pair_students(self):
        student_performance, _ = self.analyze_performance()
        if student_performance is None:
            return None
        
        weak_students = student_performance[student_performance['Category'] == 'Weak']
        strong_students = student_performance[student_performance['Category'] == 'Strong']
        
        # Randomly pair weak students with strong ones
        pairs = []
        for _, weak in weak_students.iterrows():
            if not strong_students.empty:
                strong = strong_students.iloc[np.random.randint(len(strong_students))]
                pairs.append({
                    'Weak Student': weak['Candidate Name'],
                    'Weak Student Email': weak['Candidate Email'],
                    'Weak Student Average': f"{weak['Marks']:.2f}",
                    'Strong Student': strong['Candidate Name'],
                    'Strong Student Email': strong['Candidate Email'],
                    'Strong Student Average': f"{strong['Marks']:.2f}"
                })
                
        return pairs
    
    
    def analyze_improvement_data(self):
        if self.initial_data is None:
            return None
            
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        
        # Generate base improvement data
        improvement_data = []
        courses = ['Python Basics', 'Java Fundamentals', 'SQL Essentials', 'Data Structures', 
                'Web Development', 'Algorithm Basics', 'Database Design', 'C Programming']
        
        # Create training data for the ML model
        X_train = []
        y_train = []
        
        # Generate training data with patterns
        for _ in range(1000):
            initial_mark = np.random.uniform(40, 95)
            attempts = np.random.randint(1, 5)
            study_hours = np.random.uniform(1, 10)
            attendance = np.random.uniform(0.6, 1.0)
            
            # Create pattern: Higher study hours and attendance generally lead to better improvement
            improvement = (study_hours * 0.5 + attendance * 10) * (100 - initial_mark) / 100
            improvement *= np.random.uniform(0.8, 1.2)  # Add some randomness
            
            X_train.append([initial_mark, attempts, study_hours, attendance])
            y_train.append(min(improvement, 100 - initial_mark))  # Cap improvement
        
        # Train ML model
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Generate actual student data using the ML model
        for i in range(500):
            student_name = f'Student_{i+1}'
            student_email = f'student{i+1}@example.com'
            course = np.random.choice(courses)
            
            # Initial student characteristics
            initial_marks = np.random.uniform(40, 85)
            num_attempts = np.random.randint(2, 5)
            base_study_hours = np.random.uniform(2, 8)
            base_attendance = np.random.uniform(0.7, 0.95)
            
            previous_marks = initial_marks
            
            # Generate improvement trajectory for each attempt
            for attempt in range(num_attempts):
                attempt_id = f'ATT-{attempt+1}'
                
                if attempt == 0:
                    marks = initial_marks
                    improvement = 0
                else:
                    # Student characteristics might improve with each attempt
                    study_hours = base_study_hours * (1 + attempt * 0.1)  # Study hours increase with attempts
                    attendance = min(1.0, base_attendance * (1 + attempt * 0.05))  # Attendance improves
                    
                    # Predict improvement using ML model
                    features = np.array([[previous_marks, attempt + 1, study_hours, attendance]])
                    features_scaled = scaler.transform(features)
                    predicted_improvement = model.predict(features_scaled)[0]
                    
                    # Add some noise to the prediction
                    noise = np.random.normal(0, 2)
                    actual_improvement = max(0, min(predicted_improvement + noise, 100 - previous_marks))
                    
                    # Calculate new marks
                    marks = previous_marks + actual_improvement
                    improvement = marks - previous_marks
                    
                    # Occasionally simulate setbacks (20% chance)
                    if np.random.random() < 0.2:
                        marks = max(previous_marks - np.random.uniform(0, 5), 40)
                        improvement = marks - previous_marks
                
                # Record the data point
                improvement_data.append({
                    'Candidate Name': student_name,
                    'Candidate Email': student_email,
                    'Course Name': course,
                    'Initial Marks': round(initial_marks if attempt == 0 else previous_marks, 2),
                    'Improved Marks': round(marks, 2),
                    'Improvement': round(improvement, 2),
                    'Attempt ID': attempt_id,
                    'Study Hours': round(base_study_hours * (1 + attempt * 0.1), 2),
                    'Attendance Rate': round(min(1.0, base_attendance * (1 + attempt * 0.05)), 2)
                })
                
                previous_marks = marks
        
        return pd.DataFrame(improvement_data)
        
    def analyze_improvement(self):
        if self.initial_data is None or self.improvement_data is None:
            return None
        
        # Combine initial and improvement data
        all_data = pd.concat([self.initial_data, self.improvement_data])
        
        improvements = []
        for name, group in all_data.groupby('Candidate Email'):
            if len(group) > 1:  # If student has multiple attempts
                first_attempts = group[group['Attempt ID'] == 'ATT-1']
                last_attempts = group[group['Attempt ID'].str.contains('ATT-2')]
                
                if not first_attempts.empty and not last_attempts.empty:
                    initial_data_dict = first_attempts.set_index('Course Name')['Marks'].to_dict()
                    final_data_dict = last_attempts.set_index('Course Name')['Marks'].to_dict()
                    
                    # Compare course by course
                    for course_name, initial_marks in initial_data_dict.items():
                        if course_name in final_data_dict:
                            final_marks = final_data_dict[course_name]
                            if final_marks > initial_marks:
                                improvements.append({
                                    'Student Name': group['Candidate Name'].iloc[0],
                                    'Email': name,
                                    'Course Name': course_name,
                                    'Initial Marks': f"{initial_marks:.2f}",
                                    'Improved Marks': f"{final_marks:.2f}",
                                    'Improvement': f"{final_marks - initial_marks:.2f}"
                                })
        
        return improvements
    def generate_performance_distribution_chart_with_names(self):
        if self.initial_data is None:
            return None

        self.initial_data['Performance Category'] = self.initial_data['Marks'].apply(
            lambda x: 'Strong' if x >= 75 else ('Average' if x >= 60 else 'Weak')
        )
        category_counts = self.initial_data.groupby('Performance Category')['Candidate Name'].apply(
            lambda names: ', '.join(names)
        )
        
        fig = go.Figure(
            data=[go.Bar(
                x=category_counts.index,
                y=category_counts.str.split(', ').str.len(),
                text=category_counts,
                hoverinfo='x+y+text',
                marker=dict(color=['#4caf50', '#ffa000', '#f44336'])
            )]
        )
        fig.update_layout(
            title="Performance Distribution",
            xaxis_title="Performance Category",
            yaxis_title="Number of Students",
            template="plotly_white"
        )
        return fig.to_html(full_html=False)

    
    def generate_performance_distribution_chart(self):
            if self.initial_data is None:
                return None
            
            # Create performance distribution
            self.initial_data['Performance Category'] = self.initial_data['Marks'].apply(
                lambda x: 'Strong' if x >= 75 else ('Average' if x >= 60 else 'Weak')
            )
            category_counts = self.initial_data['Performance Category'].value_counts()

            # Create a bar chart with Plotly
            fig = go.Figure(
                data=[go.Bar(x=category_counts.index, y=category_counts.values, 
                            marker=dict(color=['#4caf50', '#ffa000', '#f44336']))]
            )
            fig.update_layout(
                title="Performance Distribution",
                xaxis_title="Performance Category",
                yaxis_title="Number of Students",
                template="plotly_white"
            )
            return fig.to_html(full_html=False)

    def generate_course_performance_chart(self):
        if self.initial_data is None:
            return None

        # Average marks by course
        course_performance = self.initial_data.groupby('Course Name')['Marks'].mean().sort_values()

        # Create a horizontal bar chart with Plotly
        fig = px.bar(
            course_performance,
            x=course_performance.values,
            y=course_performance.index,
            orientation='h',
            labels={"x": "Average Marks", "y": "Course Name"},
            title="Average Performance by Course",
            template="plotly_white"
        )
        return fig.to_html(full_html=False)
    def generate_course_performance_chart_with_names(self):
        if self.initial_data is None:
            return None

        course_students = self.initial_data.groupby('Course Name').apply(
            lambda group: ', '.join(group['Candidate Name'])
        )
        course_avg = self.initial_data.groupby('Course Name')['Marks'].mean()

        fig = px.bar(
            course_avg,
            x=course_avg.values,
            y=course_avg.index,
            text=course_students,
            orientation='h',
            labels={"x": "Average Marks", "y": "Course Name"},
            title="Average Performance by Course",
            template="plotly_white"
        )
        fig.update_traces(hovertemplate='Course: %{y}<br>Average Marks: %{x:.2f}<br>Students: %{text}')
        return fig.to_html(full_html=False)

    def generate_report(self):
        if self.initial_data is None:
            return None

        # Add summary statistics
        performance_summary = self.initial_data.groupby('Course Name')['Marks'].describe()

        # Save to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            self.initial_data.to_excel(writer, index=False, sheet_name='Raw Data')
            performance_summary.to_excel(writer, sheet_name='Summary Statistics')
        
        output.seek(0)
        return output

analyzer = PerformanceAnalyzer()


@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Performance Analysis</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(to bottom, #4facfe, #00f2fe);
            color: #fff;
        }

        .container {
            max-width: 1100px;
            margin: 50px auto;
            padding: 30px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            color: #333;
        }

        h1 {
            text-align: center;
            font-size: 3rem;
            color: #4facfe;
            margin-bottom: 20px;
            font-weight: 700;
        }

        .section {
            margin-bottom: 30px;
        }

        .card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .card h3 {
            margin: 0;
            color: #4facfe;
            font-weight: bold;
        }

        .card input[type="file"] {
            margin-right: 15px;
        }

        .button {
            background-color: #4facfe;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }

        .actions {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }

        .button:hover {
            background-color: #00c6ff;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 15px;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }

        th {
            background-color: #4facfe;
            color: white;
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            font-size: 14px;
            color: #666;
        }
        .dashboard-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px;
        }
    
        .chart-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
         .bar span {
            padding: 5px;
            writing-mode: vertical-lr;
            transform: rotate(180deg);
            text-align: center;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .dashboard-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .dashboard-table {
            width: 100%;
            margin-top: 10px;
        }
        .dashboard-table td {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        .chart {
            display: flex;
            justify-content: space-around;
            align-items: flex-end;
            height: 200px;
            margin-top: 20px;
        }
        .bar {
            width: 60px;
            min-height: 20px;
            margin: 0 10px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            color: white;
            border-radius: 4px;
            transition: height 0.3s ease;
        }
        
                
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }

        .dashboard-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .chart {
            height: 300px;
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            padding: 20px;
        }

        .bar {
            width: 60px;
            margin: 0 10px;
            position: relative;
            transition: height 0.3s ease;
            min-height: 30px;
        }

        .bar span {
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            width: 100%;
            font-size: 12px;
            color: #333;
        }

        .dashboard-table {
            width: 100%;
            margin-top: 10px;
        }

        .dashboard-table td {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }

        .dashboard-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .chart {
            height: 200px;
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            padding: 20px 20px 40px 20px;
        }

        .bar {
            width: 40px;
            margin: 0 5px;
            position: relative;
            transition: height 0.3s ease;
            min-height: 20px;
        }

        .bar span {
            position: absolute;
            bottom: -30px;
            left: 50%;
            transform: translateX(-50%) rotate(-45deg);
            transform-origin: left;
            text-align: left;
            width: max-content;
            font-size: 11px;
            color: #333;
            white-space: nowrap;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }

        .stat-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }

        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #2196F3;
        }

        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }

        .course-performance {
            margin-top: 20px;
        }

        .course-bar {
            display: flex;
            align-items: center;
            margin: 8px 0;
        }

        .course-name {
            width: 120px;
            font-size: 12px;
        }

        .course-progress {
            flex-grow: 1;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            transition: width 0.3s ease;
        }

        .progress-value {
            margin-left: 10px;
            font-size: 12px;
            width: 50px;
        }

        .trend-indicator {
            display: inline-block;
            margin-left: 5px;
            font-size: 14px;
        }

        .trend-up { color: #4CAF50; }
        .trend-down { color: #F44336; }

    
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Student Performance Analysis</h1>

        <div class="section">
            <div class="card">
                <h3>Upload Initial Data</h3>
                <div>
                    <input type="file" id="initialFile" accept=".csv,.xlsx">
                    <button class="button" onclick="uploadInitial()">Upload</button>
                </div>
            </div>
            <div class="card">
                <h3>Upload Improvement Data</h3>
                <div>
                    <input type="file" id="improvementFile" accept=".csv,.xlsx">
                    <button class="button" onclick="uploadImprovement()">Upload</button>
                </div>
            </div>
        </div>

        <div class="section actions">
            <button class="button" onclick="showAnalysis()">📊 Show Analysis</button>
            <button class="button" onclick="showTodoCourses()">📋 To-Do Courses</button>
            <button class="button" onclick="showPairs()">🤝 Pair Students</button>
            <button class="button" onclick="analyzeImprovementData()">📝 Generate Improvement Data</button>
            <button class="button" onclick="showImprovement()">📈 Show Improvement</button>
            <button class="button" onclick="window.location.href='/dashboard'">📊 View Dashboard</button>
            <button class="button" onclick="window.location.href='/download_report'">⬇️ Download Report</button>

        </div>

        <div id="results">
            <h3 style="text-align: center;">Results will appear here...</h3>
        </div>          
    </div>

    <div class="footer">
        &copy; 2025 Student Performance Analysis | Built with ❤ and 💻
    </div>

    <script>
        function uploadInitial() {
            const file = document.getElementById('initialFile').files[0];
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/upload_initial', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => alert(data.message));
        }

        function uploadImprovement() {
            const file = document.getElementById('improvementFile').files[0];
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/upload_improvement', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => alert(data.message));
        }

        function showAnalysis() {
            fetch('/analysis')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('results').innerHTML = data.html;
                });
        }

        function showTodoCourses() {
            fetch('/todo_courses')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('results').innerHTML = data.html;
                });
        }

        function showPairs() {
            fetch('/pair_students')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('results').innerHTML = data.html;
                });
        }
        function analyzeImprovementData() {
             window.location.href = '/analyze_improvement_data';
          }

        function showImprovement() {
            fetch('/improvement')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('results').innerHTML = data.html;
                });
        }
        function showDashboard() {
            fetch('/dashboard')
                .then(response => response.json())
                .then(data => {
                  document.getElementById('results').innerHTML = data.html;
                });
        }
        function showDashboard() {
            console.log('Fetching dashboard data...');
            fetch('/dashboard')
                .then(response => {
                    console.log('Response received:', response);
                    return response.json();
                })
                .then(data => {
                    console.log('Dashboard data:', data);
                    document.getElementById('results').innerHTML = data.html;
                })
                .catch(error => {
                    console.error('Error fetching dashboard:', error);
                    document.getElementById('results').innerHTML = 
                        '<div class="alert alert-danger">Error loading dashboard</div>';
                });
        }
       
    </script>
</body>
</html>''')

@app.route('/upload_initial', methods=['POST'])
def upload_initial():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    try:
        analyzer.load_initial_data(file)
        return jsonify({'success': True, 'message': 'Initial data uploaded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/upload_improvement', methods=['POST'])
def upload_improvement():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    try:
        analyzer.load_improvement_data(file)
        return jsonify({'success': True, 'message': 'Improvement data uploaded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/analysis')
def show_analysis():
    result, accuracy = analyzer.analyze_performance()
    if result is None:
        return jsonify({'html': '<p>No analysis available. Please upload data first.</p>'})
    
    html = '<h2>Performance Analysis</h2>'
    html += f'<p> Random forest Model Accuracy: {accuracy * 100:.2f}%</p>'
    html += result.to_html(classes='table', index=False)
    return jsonify({'html': html})


@app.route('/todo_courses')
def show_todo_courses():
    recommendations = analyzer.recommend_courses()
    if recommendations is None:
        return jsonify({'html': '<p>No recommendations found for weak students. Please check the data.</p>'})
    
    html = '<h2>Recommended Courses for Weak Students</h2>'
    html += pd.DataFrame(recommendations).to_html(classes='table', index=False)
    return jsonify({'html': html})


@app.route('/pair_students')
def show_pairs():
    pairs = analyzer.pair_students()
    if pairs is None:
        return jsonify({'html': '<p>No pairs found. Please check the data.</p>'})
    
    html = '<h2>Student Pairs (Weak with Strong)</h2>'
    html += pd.DataFrame(pairs).to_html(classes='table', index=False)
    return jsonify({'html': html})

@app.route('/analyze_improvement_data')
def analyze_improvement_data():
    improvement_df = analyzer.analyze_improvement_data()
    if improvement_df is None:
        return jsonify({'html': '<p>No initial data available. Please upload data first.</p>'})
    
    # Save to Excel
    excel_file = BytesIO()
    improvement_df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='improvement_data.xlsx'
    )


@app.route('/improvement')
def show_improvement():
    improvements = analyzer.analyze_improvement()
    if improvements is None:
        return jsonify({'html': '<p>No improvement data available. Please upload data first.</p>'})
    
    html = '<h2>Student Improvement</h2>'
    html += pd.DataFrame(improvements).to_html(classes='table', index=False)
    return jsonify({'html': html})
# First, make sure this function is in your PerformanceAnalyzer class
class PerformanceAnalyzer:
    def get_dashboard_stats(self):
        if self.initial_data is None:
            return {
                'total_students': 0,
                'strong_performers': 0,
                'average_performers': 0,
                'weak_performers': 0,
                'improved': 0,
                'not_improved': 0,
                'consistently_strong': 0
            }
            
        total_students = len(self.initial_data['Candidate Email'].unique())
        
        # Performance categories
        strong = len(self.initial_data[self.initial_data['Marks'] >= 75])
        average = len(self.initial_data[(self.initial_data['Marks'] >= 60) & (self.initial_data['Marks'] < 75)])
        weak = len(self.initial_data[self.initial_data['Marks'] < 60])
        
        # Improvement analysis
        improved = 0
        not_improved = 0
        consistently_strong = strong
        
        if self.improvement_data is not None:
            try:
                # Try to merge on both email and course name
                df = pd.merge(self.initial_data, self.improvement_data, 
                            on=['Candidate Email', 'Course Name'], 
                            suffixes=('_initial', '_improved'))
                
                improved = len(df[df['Marks_improved'] > df['Marks_initial']])
                not_improved = len(df[df['Marks_improved'] <= df['Marks_initial']])
                consistently_strong = len(df[(df['Marks_initial'] >= 75) & (df['Marks_improved'] >= 75)])
            except:
                # If merge fails, keep default values
                pass
        
        return {
            'total_students': total_students,
            'strong_performers': strong,
            'average_performers': average,
            'weak_performers': weak,
            'improved': improved,
            'not_improved': not_improved,
            'consistently_strong': consistently_strong
        }
@app.route('/dashboard')
def show_dashboard():
    if analyzer.initial_data is None:
        return '''
        <div class="container">
            <h1 style="color: red;">⚠️ Data Missing</h1>
            <p>Please upload the initial data first to view the dashboard.</p>
        </div>
        '''

    # Generate charts using Plotly
    performance_chart = analyzer.generate_performance_distribution_chart_with_names()
    course_chart = analyzer.generate_course_performance_chart_with_names()

    # Add descriptive statistics
    total_students = len(analyzer.initial_data['Candidate Email'].unique())
    strong_performers = len(analyzer.initial_data[analyzer.initial_data['Marks'] >= 75])
    average_performers = len(analyzer.initial_data[(analyzer.initial_data['Marks'] >= 60) & 
                                                   (analyzer.initial_data['Marks'] < 75)])
    weak_performers = len(analyzer.initial_data[analyzer.initial_data['Marks'] < 60])

    # Create a dynamic table of student data
    student_table = analyzer.initial_data.to_html(classes='table', index=False)

    # Combine charts, stats, and layout
    dashboard_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Student Performance Dashboard</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(to bottom, #4facfe, #00f2fe);
                color: #333;
            }}
            .container {{
                max-width: 1200px;
                margin: 50px auto;
                padding: 20px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            }}
            h1 {{
                text-align: center;
                color: #4facfe;
                margin-bottom: 30px;
                font-weight: bold;
            }}
            h3 {{
                color: #333;
                margin-bottom: 15px;
                border-left: 4px solid #4facfe;
                padding-left: 10px;
            }}
            .stats-container {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 40px;
            }}
            .stat-card {{
                background: #f9f9f9;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                text-align: center;
                flex: 1;
                margin: 0 10px;
            }}
            .stat-card h2 {{
                color: #4facfe;
                font-size: 36px;
                margin: 0;
            }}
            .stat-card p {{
                color: #666;
                margin: 10px 0 0;
            }}
            .chart-container {{
                margin-bottom: 40px;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                font-size: 14px;
                color: #666;
            }}
            .table-container {{
                margin-top: 40px;
            }}
            .table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            .table th, .table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .table th {{
                background-color: #4facfe;
                color: white;
            }}
            .table tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            .table tr:hover {{
                background-color: #ddd;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Dashboard: Student Performance</h1>
            
            <div class="stats-container">
                <div class="stat-card">
                    <h2>{total_students}</h2>
                    <p>Total Students</p>
                </div>
                <div class="stat-card">
                    <h2>{strong_performers}</h2>
                    <p>Strong Performers</p>
                </div>
                <div class="stat-card">
                    <h2>{average_performers}</h2>
                    <p>Average Performers</p>
                </div>
                <div class="stat-card">
                    <h2>{weak_performers}</h2>
                    <p>Weak Performers</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>Performance Distribution</h3>
                <div>{performance_chart}</div>
            </div>
            
            <div class="chart-container">
                <h3>Average Performance by Course</h3>
                <div>{course_chart}</div>
            </div>

            <div class="table-container">
                <h3>Student Data Table</h3>
                <p>Below is the detailed table of students with their marks and performance categories:</p>
                {student_table}
            </div>
        </div>

        <div class="footer">
            &copy; 2025 Student Performance Analysis | Built with ❤ and 💻
        </div>
    </body>
    </html>
    '''
    return dashboard_html


@app.route('/download_report')
def download_report():
    report = analyzer.generate_report()
    if report is None:
        return '<p>No data available. Please upload data first.</p>'

    return send_file(
        report,
        as_attachment=True,
        download_name='Student_Performance_Report.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
      app.run(debug=True)
