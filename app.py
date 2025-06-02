from flask import Flask, render_template, request, redirect, session, url_for, flash
import json, random, os

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Ensure these paths are correct
USER_DB = os.path.join(app.root_path, 'users.json')
QUESTION_DB = os.path.join(app.root_path, 'questions.json')

def load_users():
    if not os.path.exists(USER_DB):
        with open(USER_DB, 'w') as f:
            json.dump({}, f)
    with open(USER_DB, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, 'w') as f:
        json.dump(users, f)

def load_questions():
    try:
        with open(QUESTION_DB, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading questions: {e}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        avatar = request.form['avatar']

        if username in users:
            flash('Username already exists!')
            return redirect('/register')

        users[username] = {'password': password, 'avatar': avatar}
        save_users(users)
        session['username'] = username
        return redirect('/quiz')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect('/quiz')
        else:
            flash('Invalid credentials')
            return redirect('/login')

    return render_template('login.html')

@app.route('/quiz')
def quiz():
    if 'username' not in session:
        return redirect('/login')

    questions = load_questions()
    if not questions:
        return render_template('quiz.html', error="No questions available")
    
    random.shuffle(questions)
    session['questions'] = questions
    session['score'] = 0
    session['current'] = 0
    return render_template('quiz.html')

@app.route('/answer', methods=['POST'])
def answer():
    if 'questions' not in session:
        return redirect('/quiz')
    
    selected = request.form['option']
    idx = session['current']
    correct = session['questions'][idx]['answer']
    
    if selected == correct:
        session['score'] += 1

    session['current'] += 1
    if session['current'] >= len(session['questions']):
        score = session['score']
        return redirect(url_for('result', score=score))

    return render_template('quiz.html')

@app.route('/result')
def result():
    score = int(request.args.get('score', 0))
    total = len(session.get('questions', []))
    return render_template('result.html', score=score, total=total)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)