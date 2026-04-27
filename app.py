from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import requests
import os
from datetime import datetime
from functools import wraps
import json
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'profiles')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    watchlist = db.relationship('Watchlist', backref='user', lazy=True, cascade='all, delete-orphan')
    readinglist = db.relationship('ReadingList', backref='user', lazy=True, cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', backref='sender_user', lazy=True, foreign_keys='Message.sender_id', cascade='all, delete-orphan')
    received_messages = db.relationship('Message', backref='receiver_user', lazy=True, foreign_keys='Message.receiver_id')

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anime_id = db.Column(db.String(100), nullable=False)
    anime_title = db.Column(db.String(255), nullable=False)
    anime_image = db.Column(db.String(500))
    status = db.Column(db.String(50), default='Planning')  # Planning, Watching, Completed
    episodes_watched = db.Column(db.Integer, default=0)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReadingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    manga_id = db.Column(db.String(100), nullable=False)
    manga_title = db.Column(db.String(255), nullable=False)
    manga_image = db.Column(db.String(500))
    status = db.Column(db.String(50), default='Planning')  # Planning, Reading, Completed
    chapters_read = db.Column(db.Integer, default=0)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    bio = db.Column(db.String(500))
    profile_image = db.Column(db.String(500), default='https://via.placeholder.com/150?text=No+Avatar')
    favorite_anime = db.Column(db.String(255))
    favorite_manga = db.Column(db.String(255))
    location = db.Column(db.String(100))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_online = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # None for public messages
    content = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Boolean, default=False)  # Public = visible to all, Private = one-on-one
    anime_topic = db.Column(db.String(255))  # Optional: which anime they're discussing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

# ==================== API INTEGRATION ====================
JAKEN_API = 'https://api.jikan.moe/v4'
ANILIST_API = 'https://graphql.anilist.co'

def get_anime_details(anime_id):
    """Fetch anime details from Jikan API"""
    try:
        response = requests.get(f'{JAKEN_API}/anime/{anime_id}', timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        print(f"Error fetching anime: {e}")
        return None

def get_manga_details(manga_id):
    """Fetch manga details from Jikan API"""
    try:
        response = requests.get(f'{JAKEN_API}/manga/{manga_id}', timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        print(f"Error fetching manga: {e}")
        return None

def get_anime_search(query, page=1):
    """Search anime"""
    try:
        response = requests.get(f'{JAKEN_API}/anime', params={'query': query, 'page': page}, timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return []
    except Exception as e:
        print(f"Error searching anime: {e}")
        return []

def get_manga_search(query, page=1):
    """Search manga"""
    try:
        response = requests.get(f'{JAKEN_API}/manga', params={'query': query, 'page': page}, timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return []
    except Exception as e:
        print(f"Error searching manga: {e}")
        return []

def get_person(person_id):
    """Fetch author/person details"""
    try:
        response = requests.get(f'{JAKEN_API}/people/{person_id}', timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        print(f"Error fetching person: {e}")
        return None

def get_studio(studio_id):
    """Fetch animation studio details"""
    try:
        response = requests.get(f'{JAKEN_API}/studios/{studio_id}', timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        print(f"Error fetching studio: {e}")
        return None

def get_top_anime():
    """Get top anime"""
    try:
        response = requests.get(f'{JAKEN_API}/top/anime', params={'limit': 12}, timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return []
    except Exception as e:
        print(f"Error fetching top anime: {e}")
        return []

def get_top_manga():
    """Get top manga"""
    try:
        response = requests.get(f'{JAKEN_API}/top/manga', params={'limit': 12}, timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return []
    except Exception as e:
        print(f"Error fetching top manga: {e}")
        return []

# ==================== AUTHENTICATION ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== HELPER FUNCTIONS ====================
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_picture(file):
    """Save uploaded profile picture and return filename"""
    if file and allowed_file(file.filename):
        # Generate unique filename with timestamp
        filename = f"{session['user_id']}_{datetime.utcnow().timestamp()}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"/static/uploads/profiles/{filename}"
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            
            # Update user as online
            profile = UserProfile.query.filter_by(user_id=user.id).first()
            if profile:
                profile.is_online = True
                profile.last_seen = datetime.utcnow()
                db.session.commit()
            
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
        
        if User.query.filter_by(username=username).first():
            return render_template('signup.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already exists')
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.flush()
        
        # Create user profile
        user_profile = UserProfile(user_id=new_user.id, is_online=True)
        db.session.add(user_profile)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
        if profile:
            profile.is_online = False
            profile.last_seen = datetime.utcnow()
            db.session.commit()
    
    session.clear()
    return redirect(url_for('login'))

# ==================== MAIN ROUTES ====================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    top_anime = get_top_anime()
    top_manga = get_top_manga()
    return render_template('home.html', top_anime=top_anime, top_manga=top_manga)

# ==================== ANIME ROUTES ====================
@app.route('/anime/<int:anime_id>')
@login_required
def anime_detail(anime_id):
    anime = get_anime_details(anime_id)
    if not anime:
        return "Anime not found", 404
    
    in_watchlist = Watchlist.query.filter_by(
        user_id=session['user_id'],
        anime_id=str(anime_id)
    ).first()
    
    return render_template('anime.html', anime=anime, in_watchlist=bool(in_watchlist))

@app.route('/anime')
@app.route('/anime/search/<query>')
@login_required
def anime_search(query=None):
    page = request.args.get('page', 1, type=int)
    
    if not query:
        query = request.args.get('q', '')
    
    if query:
        results = get_anime_search(query, page)
    else:
        results = []
    
    return render_template('anime_search.html', results=results, query=query, page=page)

# ==================== MANGA ROUTES ====================
@app.route('/manga/<int:manga_id>')
@login_required
def manga_detail(manga_id):
    manga = get_manga_details(manga_id)
    if not manga:
        return "Manga not found", 404
    
    in_readinglist = ReadingList.query.filter_by(
        user_id=session['user_id'],
        manga_id=str(manga_id)
    ).first()
    
    return render_template('manga.html', manga=manga, in_readinglist=bool(in_readinglist))

@app.route('/manga')
@app.route('/manga/search/<query>')
@login_required
def manga_search(query=None):
    page = request.args.get('page', 1, type=int)
    
    if not query:
        query = request.args.get('q', '')
    
    if query:
        results = get_manga_search(query, page)
    else:
        results = []
    
    return render_template('manga_search.html', results=results, query=query, page=page)

# ==================== AUTHOR ROUTES ====================
@app.route('/author/<int:author_id>')
@login_required
def author_detail(author_id):
    author = get_person(author_id)
    if not author:
        return "Author not found", 404
    
    return render_template('author.html', author=author)

# ==================== ANIMATION STUDIO ROUTES ====================
@app.route('/as/<int:studio_id>')
@login_required
def studio_detail(studio_id):
    studio = get_studio(studio_id)
    if not studio:
        return "Studio not found", 404
    
    return render_template('studio.html', studio=studio)

# ==================== WATCHLIST & READING LIST ROUTES ====================
@app.route('/api/watchlist/add', methods=['POST'])
@login_required
def add_to_watchlist():
    data = request.get_json()
    anime_id = data.get('anime_id')
    anime_title = data.get('anime_title')
    anime_image = data.get('anime_image')
    
    existing = Watchlist.query.filter_by(
        user_id=session['user_id'],
        anime_id=str(anime_id)
    ).first()
    
    if existing:
        return jsonify({'status': 'already_added'}), 400
    
    watchlist_item = Watchlist(
        user_id=session['user_id'],
        anime_id=str(anime_id),
        anime_title=anime_title,
        anime_image=anime_image
    )
    db.session.add(watchlist_item)
    db.session.commit()
    
    return jsonify({'status': 'added', 'id': watchlist_item.id})

@app.route('/api/watchlist/remove/<int:item_id>', methods=['DELETE'])
@login_required
def remove_from_watchlist(item_id):
    item = Watchlist.query.get(item_id)
    if item and item.user_id == session['user_id']:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'status': 'removed'})
    return jsonify({'status': 'error'}), 400

@app.route('/api/readinglist/add', methods=['POST'])
@login_required
def add_to_readinglist():
    data = request.get_json()
    manga_id = data.get('manga_id')
    manga_title = data.get('manga_title')
    manga_image = data.get('manga_image')
    
    existing = ReadingList.query.filter_by(
        user_id=session['user_id'],
        manga_id=str(manga_id)
    ).first()
    
    if existing:
        return jsonify({'status': 'already_added'}), 400
    
    readinglist_item = ReadingList(
        user_id=session['user_id'],
        manga_id=str(manga_id),
        manga_title=manga_title,
        manga_image=manga_image
    )
    db.session.add(readinglist_item)
    db.session.commit()
    
    return jsonify({'status': 'added', 'id': readinglist_item.id})

@app.route('/api/readinglist/remove/<int:item_id>', methods=['DELETE'])
@login_required
def remove_from_readinglist(item_id):
    item = ReadingList.query.get(item_id)
    if item and item.user_id == session['user_id']:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'status': 'removed'})
    return jsonify({'status': 'error'}), 400

@app.route('/watchlist')
@login_required
def watchlist():
    watchlist_items = Watchlist.query.filter_by(user_id=session['user_id']).all()
    return render_template('watchlist.html', items=watchlist_items)

@app.route('/readinglist')
@login_required
def readinglist():
    readinglist_items = ReadingList.query.filter_by(user_id=session['user_id']).all()
    return render_template('readinglist.html', items=readinglist_items)

# ==================== USERS & PROFILES ====================
@app.route('/users')
@login_required
def users_list():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=12)
    user_profiles = {user.id: UserProfile.query.filter_by(user_id=user.id).first() for user in users.items}
    return render_template('users.html', users=users, user_profiles=user_profiles)

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    
    # Get user's watchlist stats
    watchlist_count = Watchlist.query.filter_by(user_id=user_id).count()
    readinglist_count = ReadingList.query.filter_by(user_id=user_id).count()
    
    return render_template('profile.html', user=user, profile=profile, 
                         watchlist_count=watchlist_count, readinglist_count=readinglist_count)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        bio = request.form.get('bio', '')
        favorite_anime = request.form.get('favorite_anime', '')
        favorite_manga = request.form.get('favorite_manga', '')
        location = request.form.get('location', '')
        
        # Handle profile picture upload
        profile_image = profile.profile_image
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                # Delete old profile picture if it's a custom upload (not a URL)
                if profile.profile_image and '/static/uploads/' in profile.profile_image:
                    try:
                        old_path = os.path.join(os.path.dirname(__file__), profile.profile_image.lstrip('/'))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception as e:
                        print(f"Error deleting old profile picture: {e}")
                
                # Save new profile picture
                new_image = save_profile_picture(file)
                if new_image:
                    profile_image = new_image
        elif request.form.get('profile_image_url'):
            # Allow URL input as well
            profile_image = request.form.get('profile_image_url')
        
        profile.bio = bio
        profile.favorite_anime = favorite_anime
        profile.favorite_manga = favorite_manga
        profile.location = location
        profile.profile_image = profile_image
        
        db.session.commit()
        return redirect(url_for('profile', user_id=session['user_id']))
    
    return render_template('edit_profile.html', profile=profile)

# ==================== AUTHORS ==================== 
@app.route('/authors')
@login_required
def authors_list():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')
    
    if query:
        authors = get_authors_search(query, page)
    else:
        authors = get_top_authors(page)
    
    return render_template('authors_list.html', authors=authors, query=query, page=page)

def get_top_authors(page=1):
    """Get top authors from Jikan API"""
    try:
        response = requests.get(f'{JAKEN_API}/people', params={'page': page, 'limit': 12}, timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return []
    except Exception as e:
        print(f"Error fetching top authors: {e}")
        return []

def get_authors_search(query, page=1):
    """Search authors"""
    try:
        response = requests.get(f'{JAKEN_API}/people', params={'query': query, 'page': page, 'limit': 12}, timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return []
    except Exception as e:
        print(f"Error searching authors: {e}")
        return []

# ==================== ANIMATION STUDIOS ====================
@app.route('/studios')
@login_required
def studios_list():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')
    
    if query:
        studios = get_studios_search(query, page)
    else:
        studios = get_top_studios(page)
    
    return render_template('studios_list.html', studios=studios, query=query, page=page)

def get_top_studios(page=1):
    """Get top studios from Jikan API"""
    try:
        response = requests.get(f'{JAKEN_API}/studios', params={'page': page, 'limit': 12}, timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return []
    except Exception as e:
        print(f"Error fetching top studios: {e}")
        return []

def get_studios_search(query, page=1):
    """Search studios"""
    try:
        response = requests.get(f'{JAKEN_API}/studios', params={'query': query, 'page': page, 'limit': 12}, timeout=5)
        if response.status_code == 200:
            return response.json()['data']
        return []
    except Exception as e:
        print(f"Error searching studios: {e}")
        return []

# ==================== CHAT & MESSAGING ====================
@app.route('/chat/<int:user_id>')
@login_required
def private_chat(user_id):
    other_user = User.query.get_or_404(user_id)
    other_profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    messages = Message.query.filter(
        ((Message.sender_id == session['user_id']) & (Message.receiver_id == user_id) & (~Message.is_public)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == session['user_id']) & (~Message.is_public))
    ).order_by(Message.created_at.asc()).all()
    
    return render_template('chat.html', other_user=other_user, other_profile=other_profile, messages=messages)

@app.route('/community-chat')
@login_required
def community_chat():
    page = request.args.get('page', 1, type=int)
    anime_filter = request.args.get('anime', '')
    
    query = Message.query.filter_by(is_public=True)
    if anime_filter:
        query = query.filter_by(anime_topic=anime_filter)
    
    messages_paginated = query.order_by(Message.created_at.desc()).paginate(page=page, per_page=20)
    
    # Pre-fetch sender usernames to avoid N+1 queries
    messages_data = []
    for msg in messages_paginated.items:
        sender = User.query.get(msg.sender_id)
        sender_profile = UserProfile.query.filter_by(user_id=msg.sender_id).first()
        messages_data.append({
            'message': msg,
            'sender_username': sender.username if sender else 'Unknown',
            'sender_avatar': sender_profile.profile_image if sender_profile else 'https://via.placeholder.com/40?text=Avatar'
        })
    
    return render_template('community_chat.html', messages=messages_data, messages_paginated=messages_paginated, anime_filter=anime_filter)

@app.route('/api/send-message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    content = data.get('content')
    receiver_id = data.get('receiver_id')
    is_public = data.get('is_public', False)
    anime_topic = data.get('anime_topic')
    
    if not content or not content.strip():
        return jsonify({'status': 'error', 'message': 'Message cannot be empty'}), 400
    
    message = Message(
        sender_id=session['user_id'],
        receiver_id=receiver_id if not is_public else None,
        content=content,
        is_public=is_public,
        anime_topic=anime_topic
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Update sender's last seen
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    if profile:
        profile.last_seen = datetime.utcnow()
        db.session.commit()
    
    return jsonify({
        'status': 'sent',
        'id': message.id,
        'sender_id': session['user_id'],
        'created_at': message.created_at.isoformat()
    })

@app.route('/api/get-messages/<int:user_id>')
@login_required
def get_messages(user_id):
    messages = Message.query.filter(
        ((Message.sender_id == session['user_id']) & (Message.receiver_id == user_id) & (~Message.is_public)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == session['user_id']) & (~Message.is_public))
    ).order_by(Message.created_at.asc()).all()
    
    # Mark as read
    Message.query.filter(
        (Message.receiver_id == session['user_id']) & 
        (Message.sender_id == user_id) & 
        (~Message.is_read)
    ).update({'is_read': True})
    db.session.commit()
    
    return jsonify([{
        'id': m.id,
        'sender_id': m.sender_id,
        'content': m.content,
        'created_at': m.created_at.isoformat()
    } for m in messages])

@app.route('/api/get-community-messages')
@login_required
def get_community_messages():
    page = request.args.get('page', 1, type=int)
    anime_filter = request.args.get('anime', '')
    
    query = Message.query.filter_by(is_public=True)
    if anime_filter:
        query = query.filter_by(anime_topic=anime_filter)
    
    messages = query.order_by(Message.created_at.desc()).paginate(page=page, per_page=20)
    
    return jsonify([{
        'id': m.id,
        'sender_id': m.sender_id,
        'sender_username': User.query.get(m.sender_id).username,
        'content': m.content,
        'anime_topic': m.anime_topic,
        'created_at': m.created_at.isoformat()
    } for m in messages.items])

@app.route('/api/unread-count')
@login_required
def unread_count():
    unread = Message.query.filter_by(receiver_id=session['user_id'], is_read=False).count()
    return jsonify({'count': unread})

# ==================== ERROR HANDLING ====================
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# ==================== CREATE TABLES ====================
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
