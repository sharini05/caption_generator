from flask import Flask, render_template, request, send_from_directory
import requests, os, base64
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    caption = ""
    image_url = ""

    if request.method == "POST":
        image = request.files["image"]
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

            image_url = f"/uploads/{filename}"

            # Convert image to base64
            with open(image_path, "rb") as img:
                b64_image = base64.b64encode(img.read()).decode("utf-8")

            prompt = """
Generate:
- ONE short classy caption (max 12 words)
- 5 relevant hashtags
- Elegant Instagram style
"""

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 100
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )

            caption = response.json()["choices"][0]["message"]["content"]

    return render_template("index.html", caption=caption, image_url=image_url)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)
