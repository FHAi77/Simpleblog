import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import markdown2
import frontmatter
from models import db, BlogPost
import math
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 使用环境变量进行配置
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'markdown_posts')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

db.init_app(app)

# 使用单一操作密码
OPERATION_PASSWORD = os.getenv('OPERATION_PASSWORD', 'fhAI77')


def get_all_tags():
    """获取所有标签"""
    posts_with_tags = BlogPost.query.filter(BlogPost.tags.isnot(None)).all()
    all_tags = set()
    for post in posts_with_tags:
        if post.tags:
            tags = [tag.strip() for tag in post.tags.split(',') if tag.strip()]
            all_tags.update(tags)
    return sorted(list(all_tags))


def get_recent_posts(limit=20):
    """获取最近的文章列表（用于侧边导航）"""
    return BlogPost.query.order_by(BlogPost.created_at.desc()).limit(limit).all()


@app.route('/upload', methods=['GET', 'POST'])
def upload_markdown():
    if request.method == 'POST':
        # 验证操作密码
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

            # 读取文件内容为文本
            file_content = file.read().decode('utf-8')
            
            # 使用 frontmatter 解析文本内容
            post = frontmatter.loads(file_content)
            
            # 创建新的博客文章
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
    
    return render_template('upload.html',
                           all_tags=get_all_tags(),
                           recent_posts=get_recent_posts())


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    # 查找文章
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        # 验证操作密码
        edit_password = request.form.get('edit_password')
        if edit_password != OPERATION_PASSWORD:
            flash('操作密码错误，请重试', 'danger')
            return redirect(url_for('edit_post', post_id=post_id))
        
        # 更新文章内容
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
    
    return render_template('edit.html', post=post,
                           all_tags=get_all_tags(),
                           recent_posts=get_recent_posts())


@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    delete_password = request.form.get('delete_password')
    
    # 验证操作密码
    if delete_password != OPERATION_PASSWORD:
        flash('操作密码错误，请重试', 'danger')
        return redirect(url_for('show_post', post_id=post_id))
    
    # 查找并删除文章
    post = BlogPost.query.get_or_404(post_id)
    
    try:
        # 如果文章关联了Markdown文件，尝试删除文件
        if post.markdown_file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], post.markdown_file)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # 从数据库删除文章
        db.session.delete(post)
        db.session.commit()
        
        flash('文章删除成功！', 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'删除文章时发生错误：{str(e)}', 'danger')
        return redirect(url_for('show_post', post_id=post_id))


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
                           total_pages=total_pages,
                           all_tags=get_all_tags(),
                           recent_posts=get_recent_posts())


@app.route('/post/<int:post_id>')
def show_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    html_content = markdown2.markdown(
        post.content,
        extras={
            'code-friendly': True,
            'tables': True,
            'header-ids': True,
            'task_lists': True,
            'metadata': True,
            'footnotes': True,
            'strike': True,
            'toc': {
                'depth': 6
            }
        }
    )
    return render_template('post.html', 
                           post=post, 
                           content=html_content,
                           all_tags=get_all_tags(),
                           recent_posts=get_recent_posts())


@app.route('/post/<slug>')
def show_post_by_slug(slug):
    """兼容旧slug路由，301重定向到新ID路由"""
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    return redirect(url_for('show_post', post_id=post.id), code=301)


@app.route('/search')
def search():
    """搜索文章"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if not query:
        return redirect(url_for('index'))
    
    # 搜索标题和内容
    search_filter = BlogPost.title.contains(query) | BlogPost.content.contains(query)
    total_posts = BlogPost.query.filter(search_filter).count()
    total_pages = math.ceil(total_posts / per_page) if total_posts > 0 else 1
    
    offset = (page - 1) * per_page
    posts = BlogPost.query.filter(search_filter) \
        .order_by(BlogPost.created_at.desc()) \
        .offset(offset).limit(per_page).all()
    
    return render_template('search.html',
                           posts=posts,
                           query=query,
                           page=page,
                           total_pages=total_pages,
                           total_posts=total_posts,
                           all_tags=get_all_tags(),
                           recent_posts=get_recent_posts())


@app.route('/tag/<tag>')
def posts_by_tag(tag):
    """按标签筛选文章"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 搜索包含该标签的文章
    tag_filter = BlogPost.tags.contains(tag)
    total_posts = BlogPost.query.filter(tag_filter).count()
    total_pages = math.ceil(total_posts / per_page) if total_posts > 0 else 1
    
    offset = (page - 1) * per_page
    posts = BlogPost.query.filter(tag_filter) \
        .order_by(BlogPost.created_at.desc()) \
        .offset(offset).limit(per_page).all()
    
    return render_template('tag.html',
                           posts=posts,
                           tag=tag,
                           page=page,
                           total_pages=total_pages,
                           total_posts=total_posts,
                           all_tags=get_all_tags(),
                           recent_posts=get_recent_posts())


def init_db():
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
