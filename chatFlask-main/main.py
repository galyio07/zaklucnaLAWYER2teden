from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "skrivni_kljuc_123"

USERS_FILE = 'uporabniki.json'

def load_users():
    try:
        if not os.path.exists(USERS_FILE):
            return {}
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_reviews():
    try:
        if not os.path.exists(REVIEWS_FILE):
            return []
        with open(REVIEWS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading reviews: {e}")
        return []

def save_reviews(reviews):
    with open(REVIEWS_FILE, 'w') as f:
        json.dump(reviews, f, indent=4)

@app.route('/')
def zacetna():
    return redirect(url_for('prijava'))

@app.route('/login', methods=['GET', 'POST'])
def prijava():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = load_users()
        
        if username in users and users[username]['geslo'] == password:
            session['uporabnisko_ime'] = username
            return redirect(url_for('lawyer_selection'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def registracija():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            return render_template('register.html', error="All fields are required")
        
        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")
        
        users = load_users()
        
        if username in users:
            return render_template('register.html', error="Username already exists")
        
        users[username] = {
            'e_posta': email,
            'geslo': password
        }
        
        save_users(users)
        return redirect(url_for('prijava'))
    
    return render_template('register.html')

@app.route('/menu')
def meni():
    if 'uporabnisko_ime' not in session:
        return redirect(url_for('prijava'))
    return render_template('menu.html', uporabnisko_ime=session['uporabnisko_ime'])

@app.route('/logout')
def logout():
    session.pop('uporabnisko_ime', None)
    return redirect(url_for('prijava'))

@app.route('/lawyer_selection')
def lawyer_selection():
    if 'uporabnisko_ime' not in session:
        return redirect(url_for('prijava'))
    return render_template('lawyer_selection.html', uporabnisko_ime=session['uporabnisko_ime'])

@app.route('/lawyer_chat')
def lawyer_chat():
    if 'uporabnisko_ime' not in session:
        return redirect(url_for('prijava'))

    lawyer_type = request.args.get('type', 'General')

    valid_types = ['Korporativni', 'Kazenska prava', 'Družinski', 'Intelektualni']
    if lawyer_type not in valid_types:
        return redirect(url_for('lawyer_selection'))
    
    return render_template('lawyer_chat.html', lawyer_type=lawyer_type, 
                         uporabnisko_ime=session['uporabnisko_ime'])

@app.route('/lawyer/<specialty>')
def lawyer_chat_specialty(specialty):
    return redirect(url_for('lawyer_chat.html', type=specialty))

if __name__ == '__main__':
    app.run(debug=True)