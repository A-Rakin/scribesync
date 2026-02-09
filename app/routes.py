from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Post, SocialAccount
from app.ai_suggestions import ai_helper
from app.analytics import analytics_engine
import json
from datetime import datetime

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
api = Blueprint('api', __name__)


# Simple form data extraction
def get_login_form():
    return {
        'email': request.form.get('email'),
        'password': request.form.get('password'),
        'remember': request.form.get('remember') == 'on'
    }


def get_registration_form():
    return {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'password': request.form.get('password'),
        'confirm_password': request.form.get('confirm_password')
    }


def get_post_form():
    scheduled_time_str = request.form.get('scheduled_time')
    try:
        scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%d %H:%M')
    except:
        scheduled_time = datetime.utcnow()

    return {
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'platform': request.form.get('platform', 'twitter'),
        'scheduled_time': scheduled_time,
        'hashtags': request.form.get('hashtags', ''),
        'media_url': request.form.get('media_url', '')
    }


@main.route('/')
@login_required
def dashboard():
    """Main dashboard"""
    # Get recent posts
    recent_posts = Post.query.filter_by(user_id=current_user.id) \
        .order_by(Post.created_at.desc()) \
        .limit(5).all()

    # Get scheduled posts count
    scheduled_count = Post.query.filter_by(
        user_id=current_user.id,
        status='scheduled'
    ).count()

    # Get total posts count
    total_posts = Post.query.filter_by(user_id=current_user.id).count()

    return render_template('dashboard.html',
                           recent_posts=recent_posts,
                           scheduled_count=scheduled_count,
                           total_posts=total_posts)


@main.route('/calendar')
@login_required
def calendar():
    """Content calendar view"""
    posts = Post.query.filter_by(user_id=current_user.id).all()

    calendar_data = []
    for post in posts:
        if post.scheduled_time:
            calendar_data.append({
                'id': post.id,
                'title': post.title,
                'start': post.scheduled_time.isoformat(),
                'platform': post.platform,
                'status': post.status
            })

    return render_template('calendar.html', calendar_data=json.dumps(calendar_data))


@main.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule_post():
    """Schedule new post"""
    if request.method == 'POST':
        form_data = get_post_form()

        post = Post(
            user_id=current_user.id,
            title=form_data['title'],
            content=form_data['content'],
            platform=form_data['platform'],
            scheduled_time=form_data['scheduled_time'],
            status='scheduled',
            hashtags=form_data['hashtags'],
            media_url=form_data['media_url']
        )

        db.session.add(post)
        db.session.commit()

        flash('Post scheduled successfully!', 'success')
        return redirect(url_for('main.calendar'))

    return render_template('schedule.html')


@main.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard"""
    return render_template('analytics.html')


@api.route('/suggestions', methods=['GET'])
@login_required
def get_suggestions():
    """Get AI content suggestions"""
    category = request.args.get('category', 'educational')
    count = int(request.args.get('count', 5))

    suggestions = ai_helper.generate_content_ideas(current_user.id, category, count)
    return jsonify(suggestions)


@api.route('/hashtags', methods=['GET'])
@login_required
def get_hashtags():
    """Get hashtag suggestions"""
    platform = request.args.get('platform', 'all')
    content = request.args.get('content', '')

    if content:
        hashtags = ai_helper.generate_hashtags(content, platform)
    else:
        hashtags = ai_helper.get_hashtag_suggestions(platform)

    return jsonify(hashtags)


@api.route('/analytics/data', methods=['GET'])
@login_required
def get_analytics_data():
    """Get analytics data"""
    try:
        days = int(request.args.get('days', 30))
        data = analytics_engine.get_comparison_data(current_user.id, days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@api.route('/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """Delete a scheduled post"""
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({'success': True})


# Authentication routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        form_data = get_login_form()
        user = User.query.filter_by(email=form_data['email']).first()

        if user and user.check_password(form_data['password']):
            login_user(user, remember=form_data['remember'])
            return redirect(url_for('main.dashboard'))

        flash('Invalid email or password', 'error')

    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        form_data = get_registration_form()

        if form_data['password'] != form_data['confirm_password']:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        # Check if user exists
        if User.query.filter_by(email=form_data['email']).first():
            flash('Email already registered', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=form_data['username']).first():
            flash('Username already exists', 'error')
            return render_template('register.html')

        user = User(
            username=form_data['username'],
            email=form_data['email']
        )
        user.set_password(form_data['password'])

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))