from dash_app import app
from waitress import serve
import webbrowser  # For launching web pages
from threading import Timer


app.title = "molecule scanner"
server = app.server


def open_browser():
    """
    Open browser to localhost
    """

    webbrowser.open_new("http://127.0.0.1:8080/")


Timer(1, open_browser).start()
serve(server)
