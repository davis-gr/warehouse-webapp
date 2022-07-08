from flask import redirect, render_template, request, session
from functools import wraps
from datetime import date


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def flt3(value):
    """Format value with 3 floating points."""
    return f"{value:,.3f}"

def flt2(value):
    """Format value with 2 floating points."""
    return f"{value:,.2f}"

def flt1(value):
    """Format value with 1 floating point."""
    return f"{value:,.1f}"

def flt0(value):
    """Format value with 0 floating points."""
    return f"{value:.0f}"

def today():
    return date.today().strftime("%Y-%m-%d")

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            return redirect("/cut")
        return f(*args, **kwargs)
    return decorated_function