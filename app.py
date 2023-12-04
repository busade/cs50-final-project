from flask import Flask, render_template, request, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin
from datetime import datetime
from helpers import generate_qrcode, generate_short_url, is_valid_url
import os,base64


base_dir = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, "url.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
app.config["SECRET_KEY"] = "253c4da2655bdc82be91658e448831d0"

db = SQLAlchemy(app)
login_manager = LoginManager(app)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(), nullable = False)
    username = db.Column(db.String(20), nullable = False, unique = True)    
    email = db.Column(db.String(50), nullable = False, unique= True)
    password= db.Column(db.Text, nullable = False)
    link = db.relationship("Links", backref= "user", lazy = True)

    def __repr__(self) :
        return f'<User{self.id}>'

class Links (db.Model):
    __tablename__ = "urls"
    id = db.Column(db.Integer, primary_key = True)
    link = db.Column(db.String,unique= True, nullable=False )
    long_link = db.Column(db.String, unique=True, nullable = False)
    qr_code = db.Column(db.LargeBinary, nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    

    def __repr__(self) :
        return f"<Urls{self.id}>"



with app.app_context():
    db.create_all()

@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))

@app.route('/', methods = ["GET", "POST"])
def index():
    current_year= datetime.now().year
    if request.method == "POST":
        if current_user.is_authenticated:
            user_id= current_user.id
            urls = Links.query.filter_by(user_id=user_id)
            link = request.form.get("long-url")
            short = Links.query.filter_by(long_link=link).first()
            if short:
                return render_template('index.html', urls=urls)
            if is_valid_url(link):
                new_short=generate_short_url()
                new_qr_code=generate_qrcode(new_short)
                user_id = current_user.id
                new_data = Links(link=new_short, user_id=user_id,long_link=link, qr_code=new_qr_code)
                db.session.add(new_data)
                db.session.commit()
        
                return redirect('/')
            flash("invalid url")
            return render_template('index.html')
        return redirect('/login', urls=urls)        
    return  render_template('index.html', year = current_year)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name= request.form.get("full_name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_pass = request.form.get("confirm_password")

        user_check = User.query.filter_by(username = username).first()
        email_check = User.query.filter_by(email= email).first()
        if user_check :
            flash("This username already exists.")
            return redirect("/register")
        elif email_check:
            flash("THis email already in use.")
            return redirect("/register")
        else:
            password_hash= generate_password_hash(password)
            new_user = User(name=name, username= username, email=email,password= password_hash)
            db.session.add(new_user)
            db.session.commit()

            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods= ["GET", "POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if request.method == "POST":
        user= User.query.filter_by(username=username).first()
        if not user :
            flash("Incorrect Username or password")
            return redirect ('/login')
        elif not check_password_hash(user.password, password):
            flash ("Incorrect password")
            return redirect("/login")
        login_user(user)
        return redirect("/")
    return render_template('login.html')
        
@app.route('/logout')
def logout():
    logout_user()
    flash("Bye!.")
    return redirect("/")



@app.route('/about')
def about():
    return render_template('about.html')

if __name__ =="__main__":
    app.run(debug=True)
