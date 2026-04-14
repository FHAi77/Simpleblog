import os
from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
import markdown2
import frontmatter
from models import db, BlogPost
import math
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'markdown_posts')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

db.init_app(app)

OPERATION_PASSWORD = os.getenv('OPERATION_PASSWORD', 'fhAI77')

def get_all_tags():
    posts = BlogPost.query.with_entities(BlogPost.tags).all()
    tags_set = set()
    for post in posts:
        if post.tags:
            for tag in post.tags.split(','):
                tag = tag.strip()
                if tag:
                    tags_set.add(tag)
    return sorted(list(tags_set))

@app.context_processor
def inject_globals():
    return dict(
        recent_posts=BlogPost.query.order_by(BlogPost.created_at.desc()).limit(20).all(),
        all_tags=get_all_tags()
    )

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total_posts = BlogPost.query.count()
    total_pages = math.ceil(total_posts / per_page)
    
    offset = (page - 1) * per_page
    recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc()) \
        .offset(offset).limit(per_page).all()
    
    return render_template('index.html', 
                           posts=recent_posts, 
                           page=page, 
                           total_pages=total_pages)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    html_content = markdown2.markdown(
        post.content, 
        extras={
            'code-friendly': {},
            'fenced-code-blocks': {},
            'tables': {},
            'header-ids': {},
            'task_lists': {},
            'metadata': {},
            'footnotes': {},
            'strike': {},
            'toc': {
                'depth': 6
            }
        }
    )
    return render_template('post.html', 
                           post=post, 
                           content=html_content)

@app.route('/post/<slug>')
def show_post_by_slug(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    return redirect(url_for('show_post', post_id=post.id), code=301)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if not query:
        return redirect(url_for('index'))
    
    search_filter = BlogPost.query.filter(
        db.or_(
            BlogPost.title.contains(query),
            BlogPost.content.contains(query),
            BlogPost.tags.contains(query)
        )
    )
    
    total = search_filter.count()
    total_pages = math.ceil(total / per_page)
    
    posts = search_filter.order_by(BlogPost.created_at.desc()) \
        .offset((page - 1) * per_page).limit(per_page).all()
    
    return render_template('search.html',
                           posts=posts,
                           query=query,
                           total=total,
                           page=page,
                           total_pages=total_pages)

@app.route('/tag/<tag>')
def posts_by_tag(tag):
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    tag_filter = BlogPost.query.filter(BlogPost.tags.contains(tag))
    
    total = tag_filter.count()
    total_pages = math.ceil(total / per_page)
    
    posts = tag_filter.order_by(BlogPost.created_at.desc()) \
        .offset((page - 1) * per_page).limit(per_page).all()
    
    return render_template('tag.html',
                           posts=posts,
                           tag=tag,
                           total=total,
                           page=page,
                           total_pages=total_pages)

@app.route('/upload', methods=['GET', 'POST'])
def upload_markdown():
    if request.method == 'POST':
        upload_password = request.form.get('upload_password')
        if upload_password != OPERATION_PASSWORD:
            flash('操作密码错误，请重试', 'danger')
            return redirect(url_for('upload_markdown'))

        file = request.files['markdown_file']
        if file:
            filename = file.filename
            if not (filename.endswith('.md') or filename.endswith('.markdown')):
                flash('Invalid file type. Only Markdown files (.md, .markdown) are allowed.', 'danger')
                return redirect(url_for('upload_markdown'))

            file_content = file.read().decode('utf-8')
            post = frontmatter.loads(file_content)
            
            new_post = BlogPost(
                title=post.get('title', 'Untitled'),
                content=post.content,
                markdown_file=file.filename,
                tags=post.get('tags', '')
            )
            
            db.session.add(new_post)
            db.session.commit()
            
            flash('文章上传成功！', 'success')
            return redirect(url_for('index'))
    
    return render_template('upload.html')

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        edit_password = request.form.get('edit_password')
        if edit_password != OPERATION_PASSWORD:
            flash('操作密码错误，请重试', 'danger')
            return redirect(url_for('edit_post', post_id=post_id))
        
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.tags = request.form.get('tags')
        
        try:
            db.session.commit()
            flash('文章更新成功！', 'success')
            return redirect(url_for('show_post', post_id=post.id))
        except Exception as e:
            db.session.rollback()
            flash(f'更新文章时发生错误：{str(e)}', 'danger')
            return redirect(url_for('edit_post', post_id=post_id))
    
    return render_template('edit.html', post=post)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    delete_password = request.form.get('delete_password')
    
    if delete_password != OPERATION_PASSWORD:
        flash('操作密码错误，请重试', 'danger')
        return redirect(url_for('show_post', post_id=post_id))
    
    post = BlogPost.query.get_or_404(post_id)
    
    try:
        if post.markdown_file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], post.markdown_file)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(post)
        db.session.commit()
        
        flash('文章删除成功！', 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'删除文章时发生错误：{str(e)}', 'danger')
        return redirect(url_for('show_post', post_id=post_id))

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
