from flask import Blueprint, render_template

student_bp = Blueprint('student', __name__)


@student_bp.route('/')
def index():
    """Class picker page - student selects their class."""
    return render_template('student/index.html', page_h1="Choose Your Class")
