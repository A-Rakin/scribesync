import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
from app import db
from app.models import Post


class AnalyticsEngine:
    def calculate_engagement_rate(self, post):
        """Calculate engagement rate for a post"""
        if not post:
            return 0
        engagement = (post.likes or 0) + (post.comments or 0) * 2 + (post.shares or 0) * 3
        return engagement

    def generate_daily_report(self, user_id, date=None):
        """Generate daily analytics report"""
        if not date:
            date = datetime.utcnow().date()

        start_date = datetime.combine(date, datetime.min.time())
        end_date = start_date + timedelta(days=1)

        # Get posts for the day
        posts = Post.query.filter(
            Post.user_id == user_id,
            Post.published_at >= start_date,
            Post.published_at < end_date
        ).all()

        report = {
            'date': date.isoformat(),
            'total_posts': len(posts),
            'platform_breakdown': {},
            'top_posts': [],
            'engagement_over_time': [],
            'avg_engagement_per_post': 0
        }

        total_engagement = 0
        platform_data = defaultdict(lambda: {'count': 0, 'engagement': 0})

        for post in posts:
            engagement = self.calculate_engagement_rate(post)
            total_engagement += engagement

            # Platform breakdown
            platform_data[post.platform]['count'] += 1
            platform_data[post.platform]['engagement'] += engagement

            # Collect top posts
            report['top_posts'].append({
                'id': post.id,
                'title': post.title or f"Post #{post.id}",
                'platform': post.platform,
                'engagement': engagement,
                'content_preview': (post.content[:100] + '...') if post.content else ''
            })

        # Convert defaultdict to regular dict
        report['platform_breakdown'] = dict(platform_data)

        # Sort top posts by engagement
        report['top_posts'].sort(key=lambda x: x['engagement'], reverse=True)
        report['top_posts'] = report['top_posts'][:5]

        # Calculate averages
        if posts:
            report['avg_engagement_per_post'] = total_engagement / len(posts)

        # Generate time series data (simulated)
        for hour in range(24):
            report['engagement_over_time'].append({
                'hour': hour,
                'engagement': random.randint(0, 100) if posts else 0
            })

        return report

    def get_comparison_data(self, user_id, days=30):
        """Get comparison data for the last N days"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        analytics_data = []
        current_date = start_date

        while current_date <= end_date:
            report = self.generate_daily_report(user_id, current_date)
            analytics_data.append(report)
            current_date += timedelta(days=1)

        return analytics_data


# Initialize analytics engine
analytics_engine = AnalyticsEngine()