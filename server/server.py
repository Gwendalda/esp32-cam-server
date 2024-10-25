from flask import Flask, Response, stream_with_context
import requests
import aiohttp
import asyncio

app = Flask(__name__)

ESP32_IP = 'http://10.0.0.47/'  # Replace with your ESP32 IP address

@app.route('/get_video_feed', methods=['GET'])
async def get_video_feed():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ESP32_IP) as response:
                if response.status == 200:
                    # Log headers for debugging
                    print(response.headers)

                    # Stream the MJPEG video to the client
                    async def generate():
                        async for chunk in response.content.iter_chunked(1024):
                            if chunk:
                                yield chunk  # Yield each chunk as it is received
                        print("Flask server stopped streaming")
                    
                    return Response(stream_with_context(generate()), content_type=response.headers['Content-Type'])

                else:
                    return f"Failed to connect to ESP32, status code: {response.status}", 500

    except aiohttp.ClientError as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='10.0.0.195', port=5010)
