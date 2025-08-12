import os, uuid
from flask import Flask, request, render_template_string, abort, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}

# >>> PERSISTENTER SPEICHER (Azure App Service) <<<
# Linux-App Service: /home   |  Windows-App Service: D:\home
PERSISTENT_ROOT = "/home" if os.name != "nt" else os.environ.get("HOME", r"D:\home")
UPLOAD_DIR = os.path.join(PERSISTENT_ROOT, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

HTML = """
<!doctype html>
<title>Temp Uploads (App Service HOME)</title>
<h1>Bild hochladen (temporär)</h1>
<form method="post" action="{{ url_for('upload') }}" enctype="multipart/form-data">
  <input type="file" name="file" accept="image/*" required>
  <button type="submit">Upload</button>
</form>
{% if url %}
  <p>Gespeichert unter:</p>
  <a href="{{ url }}" target="_blank">{{ url }}</a><br>
  <img src="{{ url }}" style="max-width:420px;margin-top:1rem;">
{% endif %}
"""

def allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED

@app.get("/")
def index():
    return render_template_string(HTML, url=None)

@app.post("/upload")
def upload():
    f = request.files.get("file")
    if not f or f.filename == "":
        abort(400, "Keine Datei.")
    if not allowed(f.filename):
        abort(400, "Nur png/jpg/jpeg/gif/webp.")
    name = f"{uuid.uuid4()}_{secure_filename(f.filename)}"
    path = os.path.join(UPLOAD_DIR, name)
    f.save(path)
    return render_template_string(HTML, url=url_for("file", filename=name, _external=True))

@app.get("/files/<path:filename>")
def file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)

# Kleine Debug-Route zur Kontrolle
@app.get("/debug")
def debug():
    return {
        "os.name": os.name,
        "PERSISTENT_ROOT": PERSISTENT_ROOT,
        "UPLOAD_DIR": UPLOAD_DIR,
        "exists": os.path.isdir(UPLOAD_DIR),
        "files": os.listdir(UPLOAD_DIR)
    }

if __name__ == "__main__":
    app.run(debug=True)
