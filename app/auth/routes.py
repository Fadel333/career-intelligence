from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import os

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models import User
from extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user_type = request.form.get("user_type")
        terms = request.form.get("terms")
        
        # Validation
        if not name or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.register"))
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))
        
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for("auth.register"))
        
        if not terms:
            flash("You must agree to the Terms of Service.", "error")
            return redirect(url_for("auth.register"))
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "error")
            return redirect(url_for("auth.login"))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        user = User(
            fullname=name,
            email=email,
            password=hashed_password,
            user_type=user_type or 'student'
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("auth.register"))
    
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember")
        
        if not email or not password:
            flash("Please enter both email and password.", "error")
            return redirect(url_for("auth.login"))
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=bool(remember))
            flash(f"Welcome back, {user.fullname}!", "success")
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))
    
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))