import schedule
import time
import threading
from datetime import datetime
from flask import current_app
from app import db
from app.models import Post
from app.utils import publish_to_platform
import atexit


class Scheduler:
    def __init__(self):
        self.running = False
        self.thread = None

    def check_and_publish(self):
        """Check for posts that need to be published"""
        with current_app.app_context():
            now = datetime.utcnow()

            # Find scheduled posts that are due
            due_posts = Post.query.filter(
                Post.status == 'scheduled',
                Post.scheduled_time <= now
            ).all()

            for post in due_posts:
                try:
                    # Publish to platform
                    success = publish_to_platform(post)

                    if success:
                        post.status = 'published'
                        post.published_at = now
                    else:
                        post.status = 'failed'

                    db.session.commit()
                    print(f"Post {post.id} published successfully.")

                except Exception as e:
                    print(f"Error publishing post {post.id}: {str(e)}")
                    post.status = 'failed'
                    db.session.rollback()

    def run_continuously(self, interval=60):
        """Run scheduler continuously in background"""
        schedule.every(interval).seconds.do(self.check_and_publish)

        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def start(self, app):
        """Start the scheduler in a separate thread"""
        if not self.running:
            # Create app context
            with app.app_context():
                self.thread = threading.Thread(target=self.run_continuously)
                self.thread.daemon = True
                self.thread.start()
                print("Scheduler started successfully.")

    def stop(self):
        """Stop the scheduler"""
        self.running = False


def init_scheduler(app):
    """Initialize scheduler with app context"""
    scheduler = Scheduler()

    # Start scheduler when app starts
    scheduler.start(app)

    # Cleanup on exit
    atexit.register(scheduler.stop)

    return scheduler