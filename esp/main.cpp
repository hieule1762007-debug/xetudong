#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <Wire.h>
#include <U8g2lib.h>
#include <driver/i2s.h>
#include "Audio.h"

// --- CẤU HÌNH MẠNG ---
const char* ssid = "MSI 3047";
const char* password = "hieulehaha";
char* ws_host = "192.168.137.1";
const uint16_t ws_port = 8765;

// --- CẤU HÌNH CHÂN PHẦN CỨNG ---
#define OLED_SDA 8  
#define OLED_SCL 46
#define I2S_MIC_SCK 4
#define I2S_MIC_WS  5
#define I2S_MIC_SD  6
#define I2S_SPK_BCLK 15
#define I2S_SPK_LRC  16
#define I2S_SPK_DOUT 7

// --- KHỞI TẠO ĐỐI TƯỢNG ---
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
WebSocketsClient webSocket;
Audio audio;

// --- CỖ MÁY TRẠNG THÁI GIAO DIỆN (UI) ---
enum AppState { IDLE, LISTENING, PROCESSING, SPEAKING };
AppState currentState = IDLE;

String userQuestion = "Đang dịch giọng nói..."; 
String aiAnswer = "";
int scrollX = 128; 
unsigned long lastDrawTime = 0;
bool uiNeedsUpdate = true; // CỜ CHỐNG LAG: Chỉ vẽ lại màn hình khi cần thiết



// --- TRẠNG THÁI MIC VÀ BỘ ĐẾM ---
bool isRecording = false;
#define SILENCE_THRESHOLD 10000 
#define SILENCE_TIMEOUT 3000  
unsigned long lastSoundTime = 0; 

TaskHandle_t AudioTask;

void audioTaskCode(void * pvParameters) {
    for(;;) {
        audio.loop(); 
        vTaskDelay(1); 
    }
}

void initMicrophone() {
    i2s_config_t i2s_mic_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 512,
        .use_apll = false
    };
    i2s_pin_config_t mic_pin_config = {
        .bck_io_num = I2S_MIC_SCK,   
        .ws_io_num = I2S_MIC_WS,    
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_MIC_SD   
    };
    i2s_driver_install(I2S_NUM_1, &i2s_mic_config, 0, NULL);
    i2s_set_pin(I2S_NUM_1, &mic_pin_config);
}

// HÀM ĐỔI TRẠNG THÁI CHUẨN
void changeState(AppState newState) {
    currentState = newState;
    scrollX = 128; 
    uiNeedsUpdate = true; // Mở khóa cho vẽ lại giao diện mới
}

// --- HÀM VẼ GIAO DIỆN TỐI ƯU ---
void drawUI() {
    // 1. Chốt chặn chống lag: Nếu đang thu âm hoặc nghỉ mà đã vẽ xong rồi -> Cấm vẽ tiếp để nhường CPU cho Mic
    if ((currentState == IDLE || currentState == LISTENING) && !uiNeedsUpdate) {
        return; 
    }

    if (millis() - lastDrawTime < 30) return; 
    lastDrawTime = millis();
    u8g2.clearBuffer(); 

    if (currentState == IDLE) {
        u8g2.setFont(u8g2_font_unifont_t_vietnamese1); 
        u8g2.drawUTF8(35, 40, "( ^ _ ^ )");
    } 
    else if (currentState == LISTENING) {
        u8g2.setFont(u8g2_font_unifont_t_vietnamese1); 
        u8g2.drawUTF8(10, 40, "🎤 Đang nghe...");
    } 
    else if (currentState == PROCESSING) {
        u8g2.setFont(u8g2_font_5x8_tf);
        u8g2.drawStr(70, 10, "Processing...");
        u8g2.setFont(u8g2_font_unifont_t_vietnamese1);
        u8g2.drawUTF8(0, 30, "Bạn hỏi:");
        int textWidth = u8g2.getUTF8Width(userQuestion.c_str());
        scrollX -= 3; 
        if (scrollX < -textWidth) scrollX = 128; 
        u8g2.drawUTF8(scrollX, 55, userQuestion.c_str());
    } 
    else if (currentState == SPEAKING) {
        u8g2.setFont(u8g2_font_5x8_tf);
        u8g2.drawStr(0, 10, "Xiaozhi AI:");
        u8g2.setFont(u8g2_font_unifont_t_vietnamese1);
        int textWidth = u8g2.getUTF8Width(aiAnswer.c_str());
        scrollX -= 3; 
        if (scrollX < -textWidth) scrollX = 128; 
        u8g2.drawUTF8(scrollX, 40, aiAnswer.c_str());
    }
    
    u8g2.sendBuffer();
    uiNeedsUpdate = false; // Đóng cửa, vẽ xong rồi

    // Nếu đang có chữ chạy, tự động mở khóa để loop sau vẽ tiếp
    if (currentState == PROCESSING || currentState == SPEAKING) {
        uiNeedsUpdate = true; 
    }
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("❌ Mất kết nối Server!");
            break;
            
        case WStype_CONNECTED:
            Serial.println("✅ Đã kết nối Server!");
            changeState(IDLE);
            break;
            
        case WStype_TEXT:
            String msg = String((char*)payload);
            if (msg.startsWith("http")) {

                bool isConnected = audio.connecttohost(msg.c_str());
                changeState(SPEAKING);
            }
            else if (msg.startsWith("Q:")) {
                userQuestion = msg.substring(2); 
            }
            else if (msg.startsWith("A:")) {
                aiAnswer = msg.substring(2);
             
                changeState(SPEAKING);
            }
            else {
                aiAnswer = msg;
                changeState(SPEAKING);
            }
            break;
    }
}

void setup() {
    Serial.begin(115200);

    Wire.begin(OLED_SDA, OLED_SCL);
    Wire.setClock(400000); // TĂNG TỐC I2C LÊN 400kHz ĐỂ CHỐNG LAG MICRO
    u8g2.begin();
    u8g2.enableUTF8Print();

   
    // 2. KHỞI TẠO WIFIMANAGER
   
    WiFi.setSleep(false); 
    WiFi.mode(WIFI_STA); // Khóa chế độ thu sóng
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) { delay(500); }
    
    webSocket.begin(ws_host, ws_port, "/");
    initMicrophone();
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000); 

    audio.setPinout(I2S_SPK_BCLK, I2S_SPK_LRC, I2S_SPK_DOUT);
    audio.setVolume(5); 

    xTaskCreatePinnedToCore(audioTaskCode, "AudioTask", 10000, NULL, 1, &AudioTask, 1);
}

void loop() {
    webSocket.loop();
    drawUI(); 
    
    size_t bytes_read;
    int16_t i2s_data[256]; 
    i2s_read(I2S_NUM_1, &i2s_data, sizeof(i2s_data), &bytes_read, portMAX_DELAY);
    
    if (bytes_read > 0) {
        int max_amplitude = 0;
        int samples = bytes_read / 2; 
        for (int i = 0; i < samples; i++) {
            int val = abs(i2s_data[i]); 
            if (val > max_amplitude) max_amplitude = val;
        }

        if (!isRecording) {
            if (max_amplitude > SILENCE_THRESHOLD ) {
                isRecording = true;
                lastSoundTime = millis(); 
                audio.stopSong(); 
                changeState(LISTENING); 
                userQuestion = "Đang dịch giọng nói..."; 
                webSocket.sendBIN((uint8_t*)i2s_data, bytes_read); 
            }
        } 
        else {
            webSocket.sendBIN((uint8_t*)i2s_data, bytes_read);
            if (max_amplitude > SILENCE_THRESHOLD) {
                lastSoundTime = millis();
            }

            if (millis() - lastSoundTime > SILENCE_TIMEOUT) {
                isRecording = false;
                changeState(PROCESSING); 
                webSocket.sendTXT("0"); 
            }
        }
    }
}