from flask import Blueprint
from flask import render_template

from flask_login import login_required

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.route("/")
@login_required
def dashboard():

    return render_template(
        "dashboard.html"
    )