#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <esp_camera.h>

const char* ssid = "SuperWifi";
const char* password = "cacaboudin";

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22


IPAddress local_IP(10, 0, 0, 47);
IPAddress gateway(10, 0, 0, 1);
IPAddress subnet(255, 255, 255, 0);

WebServer server(80);
unsigned long startTime;  // To track time
bool isStreaming = false;

void setup() {
    Serial.begin(115200);
    Serial.setDebugOutput(true);

    if (!WiFi.config(local_IP, gateway, subnet)) {
        Serial.println("STA Failed to configure");
    }

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("WiFi connected");

    if (!startCamera()) {
        Serial.println("Camera init failed");
        return;
    }

    startCameraServer();
}

void loop() {
    if (isStreaming && (millis() - startTime) > 30000) {  // Check if 30 seconds have passed
        stopStreaming();
        isStreaming = false;
    }
    server.handleClient();
    delay(1);
}

bool startCamera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    if (psramFound()) {
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 10;
        config.fb_count = 2;
    } else {
        config.frame_size = FRAMESIZE_QVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
    }

    if (esp_camera_init(&config) != ESP_OK) {
        Serial.println("Camera init failed");
        return false;
    }
    return true;
}

void startCameraServer() {
    server.on("/", HTTP_GET, []() {
        startStreaming();  // Start streaming when a request is made
    });

    server.begin();
    Serial.println("HTTP server started");
}

void startStreaming() {
    if (!isStreaming) {
        Serial.println("Starting camera stream for 30 seconds");
        startTime = millis();  // Record the start time
        isStreaming = true;
    }

    WiFiClient client;
    if (client.connect("10.0.0.195", 5010)) {
        camera_fb_t * fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Camera capture failed");
            return;
        }

        client.write(fb->buf, fb->len);
        esp_camera_fb_return(fb);
    } else {
        Serial.println("Connection to server failed");
    }
}

void stopStreaming() {
    Serial.println("Stopping camera stream");
    // Any other cleanup logic can go here, though the ESP32 will naturally stop capturing if not polled
}
