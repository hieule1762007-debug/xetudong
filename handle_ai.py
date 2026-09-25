import serial
import json
import time
from openai import OpenAI


from Tools_schema import tools_schema
from Tools import play_music, get_weather, find_shortest_path
from map import BACHKHOA_GRAPH, WAYPOINTS

client = OpenAI(base_url="http://localhost:11434/v1", api_key="local-run")
MODEL_NAME = "qwen2.5:7b"  # Đảm bảo bạn đã chạy lệnh 'ollama run qwen2.5:1.5b'

chat_history = [
    {
        "role": "system",
        "content": (
            "Không thêm ký hiệu và không thêm nội dung vào câu nói của tôi để nguyên nó như vậy"
            "Người dùng hỏi bằng ngôn ngữ nào bạn phải trả lời bằng ngôn ngữ đó,Không được trả lời bằng ngôn ngữ khác"
            "Bạn là trợ lý điều khiển hệ thống thông minh. BẠN PHẢI SỬ DỤNG CÁC CÔNG CỤ (TOOLS) ĐƯỢC CUNG CẤP để thực hiện yêu cầu của người dùng (chỉ đường, mở nhạc, thời tiết). "
            "Tuyệt đối không giải thích, không xin lỗi, không trả lời bằng văn bản khi có thể dùng công cụ. "
            "Nếu người dùng hỏi thời tiết mà không nói rõ ở đâu, mặc định là Đà Nẵng."
            "Bạn có thể giao tiếp bình thường nếu người dùng chỉ muốn giao tiếp bình thường"
        ),
    }
]


def handle_data(user_input):
    global chat_history
    chat_history.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=chat_history,
        tools=tools_schema,
        tool_choice="required",
    )

    response_message = response.choices[0].message

    final_answer = response_message.content or ""

    # 2. Kiểm tra xem AI có yêu cầu gọi hàm không
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"⚙️ AI đang tự động gọi hàm: {func_name}({args})")

            # Thực thi hàm tương ứng trên máy tính
            if func_name == "play_music":
                final_answer += play_music(args.get("song_name"))
            elif func_name == "get_weather":
                final_answer += get_weather(args.get("location"))
            elif func_name == "find_shortest_path":
                final_answer += find_shortest_path(
                    BACHKHOA_GRAPH, args.get("start"), args.get("end")
                )
    chat_history.append({"role": "assistant", "content": final_answer})
    if len(chat_history) > 7:
        chat_history = [chat_history[0]] + chat_history[-6:]
    return final_answer
