import cv2

# Replace with your ESP32-CAM IP address
url = 'http://10.0.0.47'

# Open a connection to the video stream
cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Display the resulting frame
    cv2.imshow('ESP32-CAM Video Feed', frame)

    # Press 'q' to exit the video stream
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()