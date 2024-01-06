from datetime import date, datetime
from calculatetime import calculate_time_difference
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from forms import CreatePostForm, RegistrationForm, LoginForm, UserEdit, CommentForm
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)

# Create login Manager class
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Init Gravatar for comment display pictures
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# Run first: flask db migrate -m "info on change"
# Then run: flask db upgrade
# db.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)
    # return User.query.get(int(user_id))


# Create admin_only function
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


# User comment delete function
def only_commenter(function):
    @wraps(function)
    def check(*args, **kwargs):
        user = db.session.execute(db.select(Comment).where(Comment.author_id == current_user.id)).scalar()
        if not current_user.is_authenticated or current_user.id != user.author_id:
            return abort(403)
        return function(*args, **kwargs)

    return check


# Used to store BlogPosts
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    post_comments = relationship("Comment", back_populates="blog_post")


# Create a User table for all your registered users.
class User(UserMixin, db.Model):
    __tablename__ = "users"
    # Currently used by Comment DB and BlogPosts - Both for author ID
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(1000))
    last_name = db.Column(db.String(1000))
    is_admin = db.Column(db.Integer, default=0)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


# Used to store all comments made by users
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    posted_time = db.Column(db.DateTime)
    # Created relationship for User and Comment
    comment_author = relationship("User", back_populates="comments")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Created relationship for blog post comment is posted to. Create Blog id value
    blog_post = relationship("BlogPost", back_populates="post_comments")
    blog_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))


with app.app_context():
    db.create_all()


# Werkzeug used to hash the user's password, add to DB, login in after if va.
@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('get_all_posts'))
    if request.method == "POST" and form.validate():
        hashed_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=hashed_password
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash("You have registered.", "info")
            return redirect(url_for("get_all_posts"))
        except IntegrityError:
            db.session.rollback()
            flash("That User is already Registered, Please try and login.", "danger")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


# Retrieve a user from the database based on their email.
@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('get_all_posts'))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("You are Now Logged In", "info")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('get_all_posts'))
        elif not user:
            flash("That Email does not exist, Please register", "danger")
            return redirect(url_for("register"))
        else:
            flash('Invalid Username or Password', 'danger')
            return redirect(url_for("login"))
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>", methods=["POST", "GET"])
# In this route we use post.post_comments to access comments assigned to blog post!
def show_post(post_id):
    comment_form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please Log in to Comment", "danger")
            return redirect(url_for('login'))
        new_com = Comment(
            author_id=current_user.id,
            blog_id=post_id,
            text=comment_form.comment.data,
            posted_time=datetime.now()
        )
        db.session.add(new_com)
        db.session.commit()
        # Tracing the days, H, M of each comment
        return redirect(url_for('show_post', post_id=post_id))
    comments = Comment.query.filter_by(blog_id=post_id).all()
    the_time = []
    for comments_time in comments:
        time = calculate_time_difference(comments_time.posted_time)
        the_time.append(time)
    return render_template("post.html", post=requested_post, form=comment_form, posted_time=the_time)


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y"),
            author_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# edit posts by ID, edit restricted to author ID.
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    if current_user.id == post.author_id:
        edit_form = CreatePostForm(
            title=post.title,
            subtitle=post.subtitle,
            img_url=post.img_url,
            author=post.author,
            body=post.body
        )
        if edit_form.validate_on_submit():
            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.img_url = edit_form.img_url.data
            post.author = current_user
            post.body = edit_form.body.data
            db.session.commit()
            return redirect(url_for("show_post", post_id=post.id))
    else:
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    if current_user.id == post_to_delete.id:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return redirect(url_for('get_all_posts'))


@app.route("/delete/comment/<int:comment_id>/<int:post_id>")
@only_commenter
def delete_comment(post_id, comment_id):
    post_to_delete = db.get_or_404(Comment, comment_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('show_post', post_id=post_id))

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/admin-panel", methods=["GET", "POST"])
@admin_only
def admin_panel():
    result = db.session.execute(db.select(User))
    all_users = result.scalars().all()
    return render_template("admin.html", users=all_users)


@app.route("/edit-user/<int:user_id>", methods=["POST", "GET"])
@admin_only
def edit_user(user_id):
    user_to_edit = db.get_or_404(User, user_id)
    if current_user.is_admin:
        edit_user_form = UserEdit(
            email=user_to_edit.email,
            username=user_to_edit.username,
            first_name=user_to_edit.first_name,
            last_name=user_to_edit.last_name,
            is_admin=user_to_edit.is_admin
        )
        if edit_user_form.validate_on_submit():
            user_to_edit.email = edit_user_form.email.data
            user_to_edit.username = edit_user_form.username.data
            user_to_edit.first_name = edit_user_form.first_name.data
            user_to_edit.last_name = edit_user_form.last_name.data
            user_to_edit.is_admin = edit_user_form.is_admin.data
            db.session.commit()
            return redirect(url_for("admin_panel"))
    else:
        return render_template("admin.html")
    return render_template("edit-user.html", form=edit_user_form)


if __name__ == "__main__":
    # app.run(debug=False)
    app.run(debug=True, port=5002)
