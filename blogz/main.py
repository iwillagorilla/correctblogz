from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
#from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'as8d7f98!qmc@#7d$*$'
db = SQLAlchemy(app)

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
     
   
    def __init__(self, owner, title, body):
        self.owner = owner
        self.title = title
        self.body = body

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner') 

    def __init__(self, username, password):

        self.username = username  
        self.password = password
           
@app.before_request
def require_login():
    allowed_functions = ['get_login', 'get_signup', 'index']
    if request.endpoint not in allowed_functions and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    
    return render_template('index.html', title= 'List of Blog Users',users=users)

@app.route('/new_post', methods=['GET', 'POST'])
def add_blog():

    blogtitle_error = ""
    blogbody_error = ""
    
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        if (not blog_title) or (blog_title.strip() == ""):
            blogtitle_error = "Please enter a blog title."

        blog_message = request.form['blog-message']    
        if (not blog_message) or (blog_title.strip() == ""):
            blogbody_error = "Please enter a blog message."

        logged_in_username = session['username']
        owner = User.query.filter_by(username=logged_in_username).first()    

        if blogtitle_error !="":
            return render_template("new_post.html", title="Blogz", blogtitle_error=blogtitle_error, blog_message = blog_message)
                
        elif blogbody_error !="":
            return render_template('new_post.html', title="Blogz", blogbody_error=blogbody_error, blog_title = blog_title) 
                
        else:
            new_blog = Blog(owner, blog_title, blog_message) 
            db.session.add(new_blog) 
            db.session.commit() 
            return render_template('ind_blog.html', title="Individual Blog", ind_blog=new_blog) 
    else:
        return render_template('new_post.html', title="Blogz")           
   
@app.route('/blog', methods=['GET', 'POST']) 
def get_blogs(): 
    id = request.args.get('id')
    if id :
        get_blog_entry = Blog.query.get(id)
        return render_template('ind_blog.html', title = "New Blog", ind_blog=get_blog_entry(id))

    authorid = request.args.get('authorid')
    if authorid :
        id = int(authorid)
        get_auth_blogs = Blog.query.filter_by(owner_id=id).all()
        return render_template('blog.html', title="Author Blog List", blogs=get_auth_blogs)
    
    blogs = Blog.query.all()
    return render_template('blog.html', title="Blogz", blogs=blogs)


@app.route('/author_blogs', methods=['GET']) 
def get_author_blog():

    user_id = request.args.get('userid') 
    blogs_by_user = Blog.query.filter_by(owner_id=user_id).all()  

    return render_template('author_blogs.html', title="Blogs by Author", blogs_by_user=blogs_by_user)

@app.route('/ind_blog', methods=['GET'])
def get_ind_blog():
    
    blog_id = request.args.get('id')
    ind_blog = Blog.query.get(blog_id)
    return render_template('ind_blog.html', title="Individual Blog", ind_blog=ind_blog)

@app.route('/signup', methods=['GET', 'POST']) 
def get_signup():

    if request.method == 'GET':
        return render_template('signup.html')

    username_new = request.form['username'] 
    password = request.form['password']
    verify = request.form['verify']

    existing_user = User.query.filter_by(username=username_new).first()

    username_error = ""
    password_error = ""
    verify_error = ""

    if not username_new :
        username_error += "Must enter a Username, Cannot be Blank. "
    else:
        if len(username_new) > 20 or len(username_new) < 3 :
            username_error += "Usernname must be at least 3 characters and no more than 20 characters long. "
        if " " in username_new :
            username_error += "Username must not have any spaces. "
        if existing_user :
            username_error += "User already exists."


    if not password :
        password_error += "Must enter a Password, Cannot be Blank. "
    else:
        if len(password) > 20 or len(password) < 3 :
            password_error += "Password must be at least 3 characters and no more than 20 characters long. "
        if " " in password :
            password_error += "Password must not have any spaces. "

    if not verify :
        verify_error += "Must enter Verify Password, Cannot be Blank. "
    else:
        if len(verify) > 20 or len(verify) < 3 :
            verify_error += "Verify Password must be at least 3 characters and no more than 20 characters long. "
        if " " in verify :
            verify_error += "Verify Password must not have any spaces. "

    if verify not in password :
        password_error += "Password and Verify Password do not match. "

    if any(username_error) or any(password_error) or any(verify_error) :   
        return render_template('signup.html', username = username_new, username_error=username_error, pswd_error=password_error, verify_error=verify_error)
    else:
        new_user = User(username_new, password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username_new
        flash_string = "New user: " + username_new + " was sucessfully created!"
        flash(flash_string)
        return redirect('/')
                

@app.route('/login', methods=['GET', 'POST']) 
def get_login(): 
    username_error = ""  
    password_error = "" 

    if request.method=='GET':
        return render_template('login.html', title = "Login")

    old_user = request.form['username']
    password = request.form['password']

    
    if old_user and password:
        session['username'] = old_user
        return redirect('/')
    if not old_user:
        return render_template('login.html', username_error="Username does not exist.")  
    else:
        return_template('login.html', password_error="Your username or password was incorrect.")  
    
    return render_template('login.html', title="Login Page")

@app.route('/logout')  
def logout():
    
    del session['username']
    return redirect('/')    

if __name__ == '__main__':
    app.run()