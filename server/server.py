from flask import Flask, Response
import requests

app = Flask(__name__)

ESP32_IP = 'http://10.0.0.47/'

@app.route('/get_video_feed', methods=['GET'])
def get_video_feed():
    # Send a request to the ESP32 to start streaming
    response = requests.get(ESP32_IP)
    
    # Handle the response or forward the stream as necessary
    if response.status_code == 200:
        return Response(response.content, content_type='video/jpeg')
    else:
        return "Failed to connect to ESP32", 500

if __name__ == '__main__':
    app.run(host='10.0.0.195', port=5010)
