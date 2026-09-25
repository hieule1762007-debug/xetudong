import asyncio
import websockets
from handle_Audio_Conect import handle_audio_stream
import threading
import http.server
import socketserver


def start_file_server():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"📻 Trạm phát file (MP3) đang chạy ngầm ở cổng {PORT}")
        httpd.serve_forever()


# Cho trạm phát chạy ngầm song song, không làm kẹt code WebSocket
threading.Thread(target=start_file_server, daemon=True).start()


# ----------------------------------------------------------------------
async def main():
    # Khởi động server
    server = await websockets.serve(handle_audio_stream, "0.0.0.0", 8765)
    print("🚀 Server AI WebSocket đang chạy ở cổng 8765!")
    print("Đang chờ ESP32 bắn âm thanh lên...")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
