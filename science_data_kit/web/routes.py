"""
Main Routes for the Flask Application

This module defines the main routes for the Flask application.
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from functools import wraps

from science_data_kit.core.pages.dashboard import DashboardPage
from science_data_kit.core.pages.file_browser import FileBrowserPage
from science_data_kit.core.pages.connect import ConnectPage
from science_data_kit.core.pages.explore import ExplorePage
from science_data_kit.web.adapters.flask_adapter import render_page_html

# Create a blueprint for the main routes
main_bp = Blueprint('main', __name__)

def login_required(f):
    """
    Decorator to require login for routes.
    
    If the user is not logged in, they will be redirected to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        # Simple authentication for demonstration purposes
        username = request.form.get('username')
        password = request.form.get('password')
        
        # In a real application, you would validate against a database
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            session['username'] = username
            flash('You have been logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out!', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the dashboard page."""
    page = DashboardPage()
    return render_page_html(page)

@main_bp.route('/files')
@login_required
def files():
    """Render the file browser page."""
    page = FileBrowserPage()
    return render_page_html(page)

@main_bp.route('/connect')
@login_required
def connect():
    """Render the connect page."""
    page = ConnectPage()
    return render_page_html(page)

@main_bp.route('/explore')
@login_required
def explore():
    """Render the explore page."""
    page = ExplorePage()
    return render_page_html(page)