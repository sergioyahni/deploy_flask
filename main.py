from flask import Flask, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import var
import mysql.connector
import flup

# ------------------------ INITIALIZE ------------------------
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

Bootstrap(app)

app.config['SECRET_KEY'] = var.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = var.connect
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ------------------------ DATABASE --------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))


db.create_all()


# ------------------------ FORMS -----------------------------
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField("Password",
                             validators=[EqualTo('confirm', message='Passwords must match')],
                             render_kw={"placeholder": "Password..."})
    confirm = PasswordField('Confirm Password', render_kw={"placeholder": "Confirm password..."})
    name = StringField("User Name", validators=[DataRequired()], render_kw={"placeholder": "User Name"})
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# ------------------------ ROUTES -----------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print("LOGIN VALIDATED")
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Wrong credentials, cannot connect')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Wrong credentials, cannot connect')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html', form=form)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print("V A L I D A T E D")
        if User.query.filter_by(email=form.email.data).first():
            flash("Account already exists.")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()

        flash("You can login now.")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/home')
@login_required
def home():
    return render_template('home.html', user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
