import os
import random
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
import requests


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS',
                                                                     {'png', 'jpg', 'jpeg', 'gif', 'mp4'})


def save_uploaded_file(file):
    """Save uploaded file and return path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None


def publish_to_platform(post):
    """Publish post to respective platform"""
    # Note: You'll need to implement actual API calls here
    # These are placeholder functions that simulate publishing

    try:
        # Simulate publishing with 90% success rate
        success_rate = 0.9

        if random.random() < success_rate:
            print(f"Simulating publishing to {post.platform}: {post.title[:50]}...")

            # Simulate some engagement metrics
            post.likes = random.randint(5, 100)
            post.shares = random.randint(0, 50)
            post.comments = random.randint(0, 30)
            post.clicks = random.randint(0, 200)

            return True
        else:
            print(f"Simulating failed publish to {post.platform}")
            return False

    except Exception as e:
        print(f"Error publishing to {post.platform}: {str(e)}")
        return False


def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """Format datetime for display"""
    if value is None:
        return ""
    return value.strftime(format)