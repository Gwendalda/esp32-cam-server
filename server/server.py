from flask import Flask, request

app = Flask(__name__)

# Global variable to store the data
received_data = ""

@app.route('/', methods=['GET', 'POST'])
def home():
    global received_data
    if request.method == 'POST':
        received_data = request.get_data(as_text=True)
        print(received_data)
        return "Data received", 200
    return f"ESP32-CAM Server is running!<br>Data: {received_data}"

if __name__ == '__main__':
    app.run(host='10.0.0.195', port=5010)
