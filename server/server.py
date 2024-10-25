from flask import Flask, Response, stream_with_context
import requests

app = Flask(__name__)

ESP32_IP = 'http://10.0.0.47/'  # Replace with your ESP32 IP address

@app.route('/get_video_feed', methods=['GET'])
def get_video_feed():
    try:
        # Stream the response directly from the ESP32
        with requests.get(ESP32_IP, stream=True) as response:
            # Check if the connection was successful
            if response.status_code == 200:
                # Forward the raw JPEG stream directly
                return Response(stream_with_context(response.iter_content(chunk_size=1024)),
                                content_type='image/jpeg')
            else:
                return f"Failed to connect to ESP32, status code: {response.status_code}", 500
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='10.0.0.195', port=5010)
