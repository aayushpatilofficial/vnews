from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Mineral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    image = db.Column(db.String(100))

@app.route('/')
def home():
    minerals = Mineral.query.all()
    return render_template('index.html', minerals=minerals)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/minerals')
def minerals():
    minerals = Mineral.query.all()
    return render_template('minerals.html', minerals=minerals)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'adminpass':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    minerals = Mineral.query.all()
    return render_template('admin_dashboard.html', minerals=minerals)

@app.route('/admin/add', methods=['POST'])
def add_mineral():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    name = request.form['name']
    description = request.form['description']
    image = request.form['image']
    new_mineral = Mineral(name=name, description=description, image=image)
    db.session.add(new_mineral)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:mineral_id>', methods=['POST'])
def delete_mineral(mineral_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    mineral = Mineral.query.get_or_404(mineral_id)
    db.session.delete(mineral)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
