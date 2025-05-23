from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# NewsVideo model
class NewsVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    url = db.Column(db.String(200))  # YouTube link

# Article model
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))

@app.route('/')
def home():
    videos = NewsVideo.query.all()
    return render_template('index.html', videos=videos)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/news')
def news():
    videos = NewsVideo.query.all()
    return render_template('news.html', videos=videos)

@app.route('/articles')
def articles():
    articles = Article.query.all()
    return render_template('articles.html', articles=articles)

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/privacy policy')
def privacy():
    return render_template('privacy.html')


@app.route('/disclaimer')
def disclaimer():
        return render_template('disclaimer.html')



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
    videos = NewsVideo.query.all()
    articles = Article.query.all()
    return render_template('admin_dashboard.html', videos=videos, articles=articles)

@app.route('/admin/add_video', methods=['POST'])
def add_video():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    title = request.form['title']
    url = request.form['url']
    new_video = NewsVideo(title=title, url=url)
    db.session.add(new_video)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    video = NewsVideo.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_article', methods=['POST'])
def add_article():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    title = request.form['title']
    description = request.form['description']
    image_url = request.form['image_url']
    new_article = Article(title=title, description=description, image_url=image_url)
    db.session.add(new_article)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_article/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
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