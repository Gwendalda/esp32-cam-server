import threading
import requests
from flask import Flask, Response, stream_with_context

app = Flask(__name__)

ESP32_IP = 'http://10.0.0.47/'  # ESP32's IP address
frame_buffer = []  # Shared buffer to hold MJPEG frames
lock = threading.Lock()  # Lock to synchronize access to the buffer

def fetch_stream():
    """
    Fetch the MJPEG stream from the ESP32 and store it in the frame buffer.
    This runs in a separate thread to continuously fetch the frames.
    """
    global frame_buffer
    while True:
        try:
            # Request MJPEG stream from ESP32
            with requests.get(ESP32_IP, stream=True) as response:
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            with lock:
                                frame_buffer.append(chunk)  # Append each chunk to the buffer
                                if len(frame_buffer) > 10:  # Keep buffer small (adjust as needed)
                                    frame_buffer.pop(0)
                else:
                    print(f"Failed to connect to ESP32: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching stream: {str(e)}")


@app.route('/get_video_feed', methods=['GET'])
def get_video_feed():
    """
    Serve the MJPEG stream to clients.
    This function runs in the Flask thread and serves the buffered frames to the client.
    """
    def generate():
        global frame_buffer
        while True:
            with lock:
                # Serve each frame chunk by chunk from the buffer
                if frame_buffer:
                    yield frame_buffer[-1]  # Send the latest frame from the buffer
            # Small sleep to avoid high CPU usage
            import time
            time.sleep(0.01)

    return Response(stream_with_context(generate()), content_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # Start the thread to fetch the MJPEG stream from ESP32
    fetch_thread = threading.Thread(target=fetch_stream)
    fetch_thread.daemon = True
    fetch_thread.start()

    # Run the Flask server on the desired port
    app.run(host='0.0.0.0', port=5010)
