from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    social_accounts = db.relationship('SocialAccount', backref='user', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    analytics = db.relationship('Analytics', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SocialAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    platform = db.Column(db.String(20))  # 'linkedin', 'twitter', 'instagram'
    account_name = db.Column(db.String(100))
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Platform-specific data
    followers_count = db.Column(db.Integer, default=0)
    last_synced = db.Column(db.DateTime)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    platform = db.Column(db.String(20))  # 'linkedin', 'twitter', 'instagram', 'all'
    scheduled_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, published, failed
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Media
    media_url = db.Column(db.String(500))
    media_type = db.Column(db.String(20))  # image, video, carousel

    # Hashtags
    hashtags = db.Column(db.String(500))

    # Analytics
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)


class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, default=datetime.utcnow().date)
    platform = db.Column(db.String(20))

    # Metrics
    total_posts = db.Column(db.Integer, default=0)
    total_engagement = db.Column(db.Integer, default=0)
    follower_growth = db.Column(db.Integer, default=0)
    avg_engagement_rate = db.Column(db.Float, default=0.0)

    # Top performing post
    best_post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    best_post = db.relationship('Post', foreign_keys=[best_post_id])


class ContentTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    category = db.Column(db.String(50))  # 'educational', 'promotional', 'entertainment'
    content_structure = db.Column(db.Text)  # JSON structure for content
    hashtags = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))