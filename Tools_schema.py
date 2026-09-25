tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "BẮT BUỘC gọi hàm này ngay lập tức khi người dùng nhắc đến tên bài hát hoặc yêu cầu mở nhạc. Tuyệt đối không phản hồi bằng văn bản.",
            "parameters": {
                "type": "object",
                "properties": {"song_name": {"type": "string"}},
                "required": ["song_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "kích hoạt ngay hàm này khi nói về thời tiết",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_shortest_path",
            "description": "tìm đường đi,đi tới liên quan đến đường đi là gọi hàm này ngày lập tực ko được tự trả lời",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {
                        "type": "string",
                        "description": "Tên địa điểm xuất phát được nhắc đến trong câu.",
                    },
                    "end": {
                        "type": "string",
                        "description": "Tên địa điểm đích đến được nhắc đến trong câu.",
                    },
                },
                "required": ["start", "end"],
            },
        },
    },
]
