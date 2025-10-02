import os
import subprocess
import tempfile
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)

def download_video(url, browser="chrome"):
    """下载视频到临时文件，并返回文件路径"""
    try:
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "--cookies-from-browser", browser,  # 从浏览器获取cookies
            "-f", "bestvideo+bestaudio/best",
            "-o", output_path,
            url
        ]
        subprocess.run(cmd, check=True)
        
        # 获取下载好的文件名
        files = os.listdir(temp_dir)
        if not files:
            return None
        return os.path.join(temp_dir, files[0])
    except subprocess.CalledProcessError as e:
        print("下载失败:", e)
        return None

@app.route("/")
def index():
    return """
    <h1>YouTube 视频下载器</h1>
    <form action="/download" method="post">
        <input type="text" name="url" placeholder="输入YouTube链接" style="width:400px;">
        <button type="submit">下载</button>
    </form>
    """

@app.route("/download", methods=["POST"])
def api_download():
    url = request.form.get("url") or (request.json.get("url") if request.is_json else None)
    if not url:
        return jsonify({"error": "请提供 YouTube 链接"}), 400

    file_path = download_video(url)
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"status": "下载失败"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
