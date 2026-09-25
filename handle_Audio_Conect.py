import asyncio
import websockets
import wave
import io
import urllib.parse
from gtts import gTTS
import os
import speech_recognition as sr
from handle_ai import handle_data
from ip_adress import ip

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2


async def handle_audio_stream(websocket):
    print(f"\n🔗 Đã kết nối với ESP32 tại {websocket.remote_address}")
    audio_data = bytearray()

    try:
        async for message in websocket:
            if isinstance(message, bytes):
                audio_data.extend(message)
                print(
                    f"📥 Đang nhận sóng âm... Tổng: {len(audio_data)} bytes", end="\r"
                )

            # --- THÊM KHỐI NÀY ĐỂ BẮT LỆNH DỪNG THU ÂM ---
            elif isinstance(message, str):
                if message == "0" and len(audio_data) > 0:
                    print(f"\n⚙️ Đang đóng gói {len(audio_data)} bytes vào RAM...")

                    wav_io = io.BytesIO()
                    with wave.open(wav_io, "wb") as wav_file:
                        wav_file.setnchannels(CHANNELS)
                        wav_file.setsampwidth(SAMPLE_WIDTH)
                        wav_file.setframerate(SAMPLE_RATE)
                        wav_file.writeframes(audio_data)
                    wav_io.seek(0)

                    print("🤖 AI đang phân tích giọng nói...")
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(wav_io) as source:
                        audio_for_ai = recognizer.record(source)

                    try:
                        text = recognizer.recognize_google(
                            audio_for_ai, language="vi-VN"
                        )
                        print(f"🎯 KẾT QUẢ: {text}")
                        await websocket.send(f"Q:{text}")
                        ai_response = await asyncio.to_thread(handle_data, text)
                        response_text = ai_response
                        youtube_url = None

                        if ai_response and "||" in ai_response:
                            parts = ai_response.split("||")
                            response_text = parts[0]
                            youtube_url = parts[1]

                        # --- LỚP BẢO VỆ CHỐNG LỖI NO TEXT TO SPEAK ---
                        if not response_text or not response_text.strip():
                            response_text = "Đang xử lý yêu cầu của bạn"

                        print(f"🎯 KẾT QUẢ AI : {ai_response}")
                        await websocket.send(f"A:{response_text}")

                        # Lúc này gọi gTTS sẽ cực kỳ an toàn vì response_text chắc chắn có chữ
                        tts = gTTS(text=response_text, lang="vi")
                        tts.save("ai_voice.mp3")

                        # 2. Lấy link mạng LAN (bạn nhớ đổi thành IP máy tính của bạn và cổng 8000)
                        # Lưu ý: Cần kết hợp với đoạn code chạy HTTP Server thu nhỏ đã bàn ở phần mở nhạc
                        link_giong_noi = f"http://{ip}:8000/ai_voice.mp3"

                        # 3. Gửi thẳng đường link xuống ESP32
                        await websocket.send(link_giong_noi)

                        if youtube_url:
                            await asyncio.sleep(6)  # Chờ 4s cho AI đọc xong câu chào
                            await websocket.send(youtube_url)
                            print(f"🎯 KẾT QUẢ AI : {youtube_url}")

                    except sr.UnknownValueError:
                        await websocket.send("Tôi không nghe rõ từ gì cả")
                        tts = gTTS(text="Tôi không nghe rõ từ gì cả", lang="vi")
                        tts.save("ai_voice.mp3")
                        link_giong_noi = f"http://{ip}:8000/ai_voice.mp3"
                        await websocket.send(link_giong_noi)
                    except sr.RequestError as e:
                        await websocket.send("Lỗi mạng khi gọi Google API")
                        tts = gTTS(text="Lỗi mạng khi gọi Google API", lang="vi")
                        tts.save("ai_voice.mp3")
                        link_giong_noi = f"http://{ip}:8000/ai_voice.mp3"
                        await websocket.send(link_giong_noi)

                    # Xóa bộ đệm chờ câu tiếp theo
                    audio_data.clear()

    except websockets.exceptions.ConnectionClosed:
        print("\n❌ ESP32 đã ngắt luồng thu âm.")


# (XÓA BỎ TOÀN BỘ KHỐI finally BÊN DƯỚI)


# Cách gọi hàm (Vì là hàm async nên phải dùng asyncio.run)
# asyncio.run(send_data_to_esp_ws("Hello ESP32, AI dang hoat dong!"))
