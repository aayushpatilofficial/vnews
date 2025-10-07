from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')

# --- PostgreSQL Database Setup ---
db_url = os.getenv(
    'DATABASE_URL',
    'postgresql://aaaa_wpxk_user:elTL77uYi2hzQADlPEm74H8Z8hYV3ABI@dpg-d0pj4cuuk2gs739n8e60-a.oregon-postgres.render.com/aaaa_wpxk'
)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True, "pool_recycle": 300}

db = SQLAlchemy(app)

# --- YouTube API Configuration ---
YOUTUBE_API_KEY = 'AIzaSyAra7KF8LW9KxpXmxhr3P99GUE22_NxKkk'
CHANNEL_ID = 'UCgeFN61OQTU3GZKL6qLsKkg'

# ---------------- MODELS ----------------
class NewsVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(300), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------- YOUTUBE FETCH FUNCTION ----------------
def get_youtube_videos(max_results=10):
    """Fetch latest videos from YouTube channel"""
    try:
        api_url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?key={YOUTUBE_API_KEY}"
            f"&channelId={CHANNEL_ID}"
            f"&part=snippet,id"
            f"&order=date"
            f"&maxResults={max_results}"
            f"&type=video"  # Only fetch videos
        )

        response = requests.get(api_url)
        data = response.json()
        videos = []

        for item in data.get('items', []):
            videos.append({
                'title': item['snippet']['title'],
                'videoId': item['id']['videoId'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'published_at': item['snippet']['publishedAt']
            })
        return videos
    except Exception as e:
        print("Error fetching YouTube videos:", e)
        return []

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    try:
        db_videos = NewsVideo.query.order_by(NewsVideo.timestamp.desc()).all()
    except OperationalError:
        db.session.rollback()
        db_videos = []

    youtube_videos = get_youtube_videos()
    return render_template('index.html', videos=db_videos, youtube_videos=youtube_videos)

@app.route('/news')
def news():
    try:
        db_videos = NewsVideo.query.order_by(NewsVideo.timestamp.desc()).all()
    except OperationalError:
        db.session.rollback()
        db_videos = []

    youtube_videos = get_youtube_videos()
    return render_template('news.html', videos=db_videos, youtube_videos=youtube_videos)

@app.route('/articles')
def articles():
    try:
        articles_list = Article.query.order_by(Article.timestamp.desc()).all()
    except OperationalError:
        db.session.rollback()
        articles_list = []
    return render_template('articles.html', articles=articles_list)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy policy')
def privacy():
    return render_template('privacy.html')

@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

# ---------------- ADMIN ----------------
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
    try:
        videos = NewsVideo.query.order_by(NewsVideo.timestamp.desc()).all()
        articles_list = Article.query.order_by(Article.timestamp.desc()).all()
    except OperationalError:
        db.session.rollback()
        videos = []
        articles_list = []
    return render_template('admin_dashboard.html', videos=videos, articles=articles_list)

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

# ---------------- SERVICE WORKER ----------------
@app.route('/sw.js')
def sw():
    return send_from_directory('static', 'sw.js')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

# ---------------- MAIN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
