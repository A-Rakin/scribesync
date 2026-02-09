import random
from datetime import datetime, timedelta
from app.models import Post, ContentTemplate


class FreeAISuggestions:
    def __init__(self):
        self.topic_templates = {
            'educational': [
                "5 Things You Didn't Know About {topic}",
                "Beginner's Guide to {topic}",
                "The Future of {topic}: Trends to Watch",
                "{topic} Explained in Simple Terms",
                "Common Mistakes in {topic} and How to Avoid Them"
            ],
            'promotional': [
                "How Our {product} Can Help You Achieve {benefit}",
                "Limited Time Offer: {offer_details}",
                "Customer Success Story: {achievement}",
                "New Feature Alert: {feature_name}",
                "Why Choose {product} Over Competitors"
            ],
            'entertainment': [
                "Fun Facts About {topic}",
                "Behind the Scenes: {process}",
                "{number} Memes That Perfectly Describe {situation}",
                "Quiz: How Much Do You Know About {topic}?",
                "Day in the Life of {role}"
            ],
            'engagement': [
                "What's Your Biggest Challenge with {topic}?",
                "Poll: Which Do You Prefer - {option1} or {option2}?",
                "Share Your Experience with {topic}",
                "What Topic Should We Cover Next?",
                "True or False: {statement}"
            ]
        }

        self.hashtag_suggestions = {
            'linkedin': ['#business', '#career', '#leadership', '#innovation', '#technology',
                         '#marketing', '#entrepreneurship', '#networking', '#success', '#motivation'],
            'twitter': ['#trending', '#viral', '#news', '#tech', '#socialmedia',
                        '#digitalmarketing', '#content', '#tips', '#lifehacks', '#community'],
            'instagram': ['#instagood', '#photooftheday', '#love', '#art', '#inspiration',
                          '#design', '#creative', '#motivation', '#lifestyle', '#beautiful']
        }

    def generate_content_ideas(self, user_id, category='educational', count=5):
        """Generate content ideas without external API"""
        user_posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).limit(20).all()

        # Extract common topics from user's previous posts
        topics = self._extract_topics(user_posts)
        if not topics:
            topics = ['your industry', 'your expertise', 'your products', 'your services']

        ideas = []
        for _ in range(count):
            topic = random.choice(topics)
            template = random.choice(self.topic_templates.get(category, self.topic_templates['educational']))
            idea = template.format(topic=topic)
            ideas.append({
                'title': idea,
                'category': category,
                'hashtags': self.get_hashtag_suggestions('all'),
                'suggested_time': self.suggest_best_time()
            })

        return ideas

    def _extract_topics(self, posts):
        """Simple topic extraction from previous posts"""
        common_words = ['the', 'and', 'for', 'with', 'that', 'this', 'have', 'from']
        word_freq = {}

        for post in posts:
            if post.content:
                words = post.content.lower().split()
                for word in words:
                    if word not in common_words and len(word) > 4:
                        word_freq[word] = word_freq.get(word, 0) + 1

        # Return top 10 words as topics
        return sorted(word_freq, key=word_freq.get, reverse=True)[:10]

    def get_hashtag_suggestions(self, platform='all'):
        """Get platform-specific hashtags"""
        if platform == 'all':
            all_hashtags = []
            for platform_hashtags in self.hashtag_suggestions.values():
                all_hashtags.extend(random.sample(platform_hashtags, 3))
            return list(set(all_hashtags))[:5]

        return random.sample(self.hashtag_suggestions.get(platform, []), 5)

    def suggest_best_time(self):
        """Suggest optimal posting times based on industry data"""
        # These are general best times - you can customize based on user's analytics
        times_by_platform = {
            'linkedin': ['08:00', '12:00', '17:00'],
            'twitter': ['07:00', '12:00', '18:00', '22:00'],
            'instagram': ['09:00', '13:00', '19:00', '21:00']
        }

        return {
            platform: random.choice(times) for platform, times in times_by_platform.items()
        }

    def format_content_for_platform(self, content, platform):
        """Format content according to platform guidelines"""
        if platform == 'twitter':
            # Ensure content fits in 280 characters
            if len(content) > 280:
                content = content[:277] + '...'
            # Add thread markers if needed
            if len(content.split('. ')) > 3:
                content += '\n(1/?)'

        elif platform == 'linkedin':
            # Make it more professional
            if not content[0].isupper():
                content = content[0].upper() + content[1:]

        elif platform == 'instagram':
            # Add emojis for visual appeal
            emojis = ['✨', '🌟', '💡', '🔥', '🚀', '🎯', '📈', '💭']
            content = random.choice(emojis) + ' ' + content

        return content

    def generate_hashtags(self, content, platform, count=5):
        """Generate relevant hashtags from content"""
        words = content.lower().split()
        filtered_words = [word.strip('.,!?') for word in words if len(word) > 4]

        # Mix content-based hashtags with platform-specific ones
        content_hashtags = ['#' + word for word in filtered_words[:count]]
        platform_hashtags = self.get_hashtag_suggestions(platform)[:count]

        # Combine and deduplicate
        all_hashtags = list(set(content_hashtags + platform_hashtags))
        return all_hashtags[:count]


# Initialize the AI helper
ai_helper = FreeAISuggestions()