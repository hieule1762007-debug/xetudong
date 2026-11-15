import asyncio
import websockets
import wave
import io
from gtts import gTTS
import speech_recognition as sr
from handle_ai import handle_data
from ip_adress import ip
import numpy as np
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2
CHUNK_BYTES = 64000
ai_response = None

active_tasks = {
    "music": None,  # Luồng chuyên tải nhạc
    "nav": None,  # Luồng chuyên chỉ đường
    "chat": None,  # Luồng hỏi đáp thông thường
}


# Đổi device="cpu" và compute_type="int8" -> Chạy ngay lập tức không cần CUDA!
stt_model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)


def dich_giong_noi_ram(pcm_bytes: bytearray) -> str:
    """Hàm chuyển trực tiếp mảng bytes âm thanh trên RAM thành chữ tiếng Việt"""
    # Đảm bảo số lượng byte luôn chẵn cho chuẩn 16-bit (2 bytes/sample)
    if len(pcm_bytes) % 2 != 0:
        pcm_bytes = pcm_bytes[:-1]

    audio_np = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0

    # --- BƯỚC QUAN TRỌNG NHẤT: LOẠI BỎ RÒ ĐIỆN DC & KÍCH ÂM LƯỢNG MIC ESP32 ---
    # 1. Khử độ lệch DC (DC Offset) thường gặp trên mic I2S INMP441
    audio_np = audio_np - np.mean(audio_np)

    # 2. Tự động kích âm lượng (Normalize) lên 90% nếu mic thu nhỏ
    max_val = np.max(np.abs(audio_np))
    if max_val > 0.005:  # Nếu có tiếng nói thì kích to lên mức 0.9
        audio_np = (audio_np / max_val) * 0.9
    else:
        return ""  # Nếu toàn bộ chỉ là im lặng thì trả về rỗng luôn

    segments, _ = stt_model.transcribe(
        audio_np,
        language="vi",
        beam_size=5,  # Đổi từ 1 lên 5 để AI rà soát ngữ pháp tiếng Việt chuẩn xác
        vad_filter=True,
        condition_on_previous_text=False,
        initial_prompt="Mở nhạc, bài hát, chỉ đường, thời tiết, xin chào.",  # Gợi ý ngữ cảnh tiếng Việt
    )
    return " ".join(seg.text for seg in segments).strip()


async def handle_text(text, websocket):
    try:
        response_text = await asyncio.to_thread(handle_data, text)

        youtube_url = None

        if response_text and "||" in response_text:
            parts = response_text.split("||")
            response_text = parts[0]
            youtube_url = parts[1]

        # --- LỚP BẢO VỆ CHỐNG LỖI NO TEXT TO SPEAK ---
        if not response_text or not response_text.strip():
            response_text = "Đang xử lý yêu cầu của bạn"

        print(f"🎯 KẾT QUẢ AI : {response_text}")
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
    except Exception as e:
        print(f"❌ Lỗi trong quá trình xử lý AI: {e}")
    except asyncio.CancelledError:
        # Khi có câu lệnh mới gọi ai_response.cancel(), nó sẽ nhảy vào đây và dừng ngay!
        print("🛑 Đã hủy tác vụ AI/Tải nhạc cũ để nhường chỗ cho câu lệnh mới!")


async def handle_audio_stream(websocket):
    print(f"\n🔗 Đã kết nối với ESP32 tại {websocket.remote_address}")
    audio_data = bytearray()
    char_translated = []
    transcribe_task = None
    try:
        async for message in websocket:
            if isinstance(message, bytes):
                audio_data.extend(message)

                # if transcribe_task is not None and transcribe_task.done():
                #     chu_moi = transcribe_task.result()
                #     if chu_moi:
                #         char_translated.append(chu_moi)

                #     transcribe_task = None
                # if len(audio_data) >= CHUNK_BYTES and transcribe_task is None:
                #     # Cắt lấy 2 giây đầu
                #     khuc_am_thanh = bytearray(audio_data[:CHUNK_BYTES])
                #     # XÓA LUÔN 2 giây này khỏi audio_data để cuối câu KHÔNG dịch lại nữa
                #     del audio_data[:CHUNK_BYTES]

                #     transcribe_task = asyncio.create_task(
                #         asyncio.to_thread(dich_giong_noi_ram, khuc_am_thanh)
                #     )

            elif isinstance(message, str):
                if message == "0":

                    # if transcribe_task is not None:
                    #     chu_dang_dich = await transcribe_task
                    #     if chu_dang_dich:
                    #         char_translated.append(chu_dang_dich)
                    # transcribe_task = None

                    # if len(audio_data) > 3200:
                    #     duoi_audio = bytearray(audio_data)
                    #     audio_data.clear()
                    #     duoi_audio = await asyncio.to_thread(
                    #         dich_giong_noi_ram, duoi_audio
                    #     )
                    #     if duoi_audio:
                    #         char_translated.append(duoi_audio)
                    # audio_data.clear()
                    # text = "".join(char_translated)
                    text = await asyncio.to_thread(dich_giong_noi_ram, audio_data)
                    audio_data.clear()
                    if text == "":
                        await websocket.send("Tôi không nghe rõ từ gì cả")
                        tts = gTTS(text="Tôi không nghe rõ từ gì cả", lang="vi")
                        tts.save("ai_voice.mp3")
                        link_giong_noi = f"http://{ip}:8000/ai_voice.mp3"
                        await websocket.send(link_giong_noi)
                    else:
                        print(f"🎯 KẾT QUẢ: {text}")
                        await websocket.send(f"Q:{text}")
                        if any(
                            k in text.lower()
                            for k in [
                                "mở nhạc",
                                "bài hát",
                                "phát bài",
                                "nghe nhạc",
                                "bật nhạc",
                                "nhạc",
                            ]
                        ):
                            type_task = "music"
                        elif any(
                            k in text.lower()
                            for k in ["chỉ đường", "đường đi", "tới", "bản đồ", "rẽ"]
                        ):
                            type_task = "map"
                        else:
                            type_task = "chat"
                        old_task = active_tasks.get(type_task)
                        if old_task is not None and not old_task.done():
                            old_task.cancel()
                        active_tasks[type_task] = asyncio.create_task(
                            handle_text(text, websocket)
                        )

                        char_translated.clear()

    except websockets.exceptions.ConnectionClosed:
        print("\n❌ ESP32 đã ngắt luồng thu âm.")


# (XÓA BỎ TOÀN BỘ KHỐI finally BÊN DƯỚI)


# Cách gọi hàm (Vì là hàm async nên phải dùng asyncio.run)
# asyncio.run(send_data_to_esp_ws("Hello ESP32, AI dang hoat dong!"))
