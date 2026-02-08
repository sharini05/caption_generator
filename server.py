from flask import Flask, render_template, request, send_from_directory
import requests, os, base64
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Upload configuration
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    caption = ""
    image_url = ""

    if request.method == "POST":
        image = request.files.get("image")

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)

            image_url = f"/uploads/{filename}"

            # Convert image to base64
            with open(image_path, "rb") as img:
                b64_image = base64.b64encode(img.read()).decode("utf-8")

            prompt = (
                "Generate ONE short classy Instagram caption (max 12 words) "
                "and 5 relevant hashtags based on the image."
            )

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
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
                "max_tokens": 100,
                "temperature": 0.7
            }

            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                data = response.json()
                print("OpenRouter Response:", data)

                if response.status_code == 200 and "choices" in data:
                    caption = data["choices"][0]["message"]["content"]
                else:
                    error_msg = data.get("error", {}).get("message", "Unknown API error")
                    caption = f"⚠️ Caption generation failed: {error_msg}"

            except Exception as e:
                caption = f"⚠️ Server error: {str(e)}"

    return render_template("index.html", caption=caption, image_url=image_url)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
