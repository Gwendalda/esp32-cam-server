from flask import Flask, Response, stream_with_context
import requests

app = Flask(__name__)

ESP32_IP = 'http://10.0.0.47/'  # Replace with your ESP32 IP address

@app.route('/get_video_feed', methods=['GET'])
def get_video_feed():
    try:
        # Send a request to the ESP32 for the MJPEG stream
        with requests.get(ESP32_IP, stream=True) as response:
            if response.status_code == 200:
                # Log headers for debugging
                print(response.headers)

                # Stream the MJPEG video to the client
                def generate():
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            yield chunk  # Yield each chunk as it is received
                    print("Flask server stopped streaming")
                
                return Response(stream_with_context(generate()), content_type=response.headers['Content-Type'])

            else:
                return f"Failed to connect to ESP32, status code: {response.status_code}", 500

    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    app.run(host='10.0.0.195', port=5010)
