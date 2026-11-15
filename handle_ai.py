import json
from openai import OpenAI


from Tools_schema import tools_schema
from Tools import play_music, get_weather, find_shortest_path
from map import BACHKHOA_GRAPH

TU_KHOA_TOOL = [
    "nhạc",
    "bài hát",
    "mở bài",
    "thời tiết",
    "mưa",
    "nắng",
    "đường",
    "đi tới",
    "đi đến",
    "chỉ đường",
]

client = OpenAI(base_url="http://localhost:11434/v1", api_key="local-run")
MODEL_NAME = "qwen2.5:7b"  # Đảm bảo bạn đã chạy lệnh 'ollama run qwen2.5:1.5b'

chat_history = [
    {
        "role": "system",
        "content": (
            "Bạn là trợ lý giọng nói thông minh có nhiệm vụ điều khiển xe tự động chở người nên bạn cần  gọi tool khi người dùng cần "
            "QUY TẮC BẮT BUỘC VỀ CÔNG CỤ (TOOLS):"
            "1. LUÔN LUÔN ưu tiên sử dụng công cụ (tool/function) nếu câu nói của người dùng liên quan đến: phát nhạc, mở bài hát, xem giờ, thời tiết,tìm đường đi,đường đi đến,đường đi."
            "2. KHÔNG BAO GIỜ tự bịa ra thông tin hoặc trả lời rằng Tôi không thể mở nhạc khi đã có công cụ `play_music`."
            "3. Khi cần dùng công cụ, CHỈ trả về định dạng gọi hàm (tool_calls), KHÔNG giải thích dài dòng. "
            "4. Chỉ trò chuyện bình thường khi yêu cầu của người dùng hoàn toàn không khớp với bất kỳ công cụ nào. "
            "5 . Nếu trò chuyện thì chỉ trả về câu nói bình thường không được gửi bất kỳ đường link hay ngôn ngữ lạ trong đoạn hội thoại bình thường "
        ),
    }
]


def handle_data(user_input):
    global chat_history
    can_dung_tool = any(kw in user_input.lower() for kw in TU_KHOA_TOOL)
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
