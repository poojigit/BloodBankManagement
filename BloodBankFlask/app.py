from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        whatsapp = request.form['whatsapp']
        password = request.form['password']
        role = request.form['role'].lower()

        blood_group = request.form['blood_group'] if role == 'donor' else None


        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, email, password, role, blood_group, phone, whatsapp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, password, role, blood_group, phone, whatsapp))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['role'] = user[4]  # role
            if user[4].lower() == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('donor_dashboard'))
        else:
            return "Invalid credentials"

    return render_template('login.html')


@app.route('/donor')
def donor_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    return render_template('donor_dashboard.html', user=user)

@app.route("/admin")
def admin_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    admin = cursor.fetchone()
    cursor.execute("SELECT blood_group, COUNT(*) FROM users WHERE role = 'donor' GROUP BY blood_group")
    stock = cursor.fetchall()
    cursor.execute("SELECT * FROM users WHERE role = 'donor'")
    donors = cursor.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", stock=stock, donors=donors, admin=admin)



@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_account', methods=['POST'])
def delete_own_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    session.clear()
    return "<h2>Your account has been deleted.</h2><a href='/'>Home</a>"

if __name__ == '__main__':
    app.run(debug=True)
