import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import markdown2
import frontmatter
from models import db, BlogPost
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'markdown_posts'
app.secret_key = os.urandom(24)  # 用于闪存消息
db.init_app(app)

# 固定上传密码
UPLOAD_PASSWORD = 'fhAI77'

@app.route('/upload', methods=['GET', 'POST'])
def upload_markdown():
    if request.method == 'POST':
        # 验证上传密码
        upload_password = request.form.get('upload_password')
        if upload_password != UPLOAD_PASSWORD:
            flash('上传密码错误，请重试', 'danger')
            return redirect(url_for('upload_markdown'))

        file = request.files['markdown_file']
        if file:
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
    
    return render_template('upload.html')

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
@app.route('/post/<slug>')
def show_post(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    html_content = markdown2.markdown(
        post.content, 
        extras={
            'code-friendly': True,
            'fenced-code-blocks': True,
            'highlightjs-class': True,
            'tables': True,
            'header-ids': True,
            'task_lists': True,
            'metadata': True,
            'footnotes': True,
            'strike': True,
            'toc': {
                'depth': 6
            },
            'link-patterns': []  # 设置为空列表
        }
    )
    recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(20).all()
    return render_template('post.html', 
                           post=post, 
                           content=html_content,
                           recent_posts=recent_posts)

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
