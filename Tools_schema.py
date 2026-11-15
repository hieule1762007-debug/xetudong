tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Phát nhạc khi người dùng yêu cầu mở một bài hát.",
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
            "description": "Xem dự báo thời tiết tại một địa điểm.",
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
            "description": "Tìm đường đi ngắn nhất từ điểm xuất phát đến điểm đích.",
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
