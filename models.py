from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from slugify import slugify

db = SQLAlchemy()

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    markdown_file = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_description = db.Column(db.String(300), nullable=True)
    tags = db.Column(db.String(200), nullable=True)

    def __init__(self, title, content, markdown_file=None, tags=None):
        self.title = title
        self.slug = self._generate_unique_slug(title)
        self.content = content
        self.markdown_file = markdown_file
        self.tags = tags
        self.meta_description = content[:150] if content else None

    def _generate_unique_slug(self, title):
        base_slug = slugify(title)
        unique_slug = base_slug
        counter = 1
        while BlogPost.query.filter_by(slug=unique_slug).first() is not None:
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        return unique_slug

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'tags': self.tags
        }