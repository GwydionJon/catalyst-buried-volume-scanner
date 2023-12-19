from molecule_scanner.dash_app import app
import webbrowser  # For launching web pages
from threading import Timer

app.title = "molecule scanner"
server = app.server
port = 8013


def open_browser():
    """
    Open browser to localhost
    """

    webbrowser.open_new(f"http://127.0.0.1:{port}")


print("Starting app...")
Timer(1, open_browser).start()
app.run_server(debug=True, port=port)
