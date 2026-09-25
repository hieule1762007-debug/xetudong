import yt_dlp
import requests
import heapq
import os
from ip_adress import ip


def play_music(song_name):
    # --- LỚP BẢO VỆ: Chống AI truyền nhầm định dạng hoặc dict/None ---
    if not song_name or not isinstance(song_name, (str, bytes)):
        song_name = "nhạc trẻ lofi"  # Giá trị phòng hờ nếu AI truyền linh tinh
    elif isinstance(song_name, dict):
        # Nếu AI lỡ truyền dạng từ điển, cố gắng lấy giá trị bên trong hoặc ép kiểu
        song_name = "nhạc trẻ lofi"

    print(f"\n[Nhạc] Đang tải bài hát: {song_name}...")

    ydl_opts = {
        "format": "bestaudio/best",
        "ffmpeg_location": "./",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
        "outtmpl": "music",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "extractor_args": {
            "youtube": {"player_client": ["android", "web"]}
        },  # Dùng client Android/Web để né hoàn toàn lỗi JS của YouTube
    }

    # Xóa file nhạc cũ đi để tránh lỗi kẹt file
    if os.path.exists("music.mp3"):
        try:
            os.remove("music.mp3")
        except:
            pass

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_name, download=True)
            title = info["entries"][0].get("title", song_name)

            # Link trạm phát nội bộ cổng 8000 mạng LAN
            link_noi_bo = f"http://{ip}:8000/music.mp3"
            return f"Đang phát bài hát {title}||{link_noi_bo}"

    except Exception as e:
        return f"Xin lỗi, tôi gặp trục trặc khi tải bài hát này: {e}"


def get_weather(location: str = "Đà Nẵng") -> str:
    """
    Hàm này dùng để tra cứu thời tiết hiện tại của một khu vực.
    Nếu không có địa điểm, mặc định sẽ lấy thời tiết tại Đà Nẵng.
    """

    location = "Đà Nẵng"
    try:
        # Gọi API thời tiết miễn phí
        url = f"https://vi.wttr.in/{location}?format=3"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            # Kết quả trả về sẽ có dạng: "Đà Nẵng: ⛅️  +34°C"
            return f"Thông tin thời tiết thực tế: {response.text.strip()}"
        else:
            return "Hiện tại không thể kết nối với máy chủ thời tiết."
    except Exception as e:
        return f"Lỗi kết nối mạng khi tra thời tiết: {e}"


def find_shortest_path(graph, start, goal):
    # 1. BỘ PHIÊN DỊCH: Khai báo các từ lóng tương đương với key trong code
    # 1. BỘ PHIÊN DỊCH: Chuyển các từ lóng/không dấu/chữ thường thành Key chuẩn xác của đồ thị
    alias_map = {
        # --- Cổng ---
        "cổng chính": "Cổng chính",
        "cong chinh": "Cổng chính",
        "cổng": "Cổng chính",
        "cổng phụ 1": "Cổng phụ 1",
        "cong phu 1": "Cổng phụ 1",
        "cổng phụ": "Cổng phụ 1",
        "cổng phụ 2": "Cổng phụ 2",
        "cong phu 2": "Cổng phụ 2",
        # --- Dịch vụ chung ---
        "căn tin 1": "Căn tin 1",
        "can tin 1": "Căn tin 1",
        "căng tin 1": "Căn tin 1",
        "căn tin 2": "Căn tin 2",
        "can tin 2": "Căn tin 2",
        "căng tin 2": "Căn tin 2",
        "thư viện": "Thư viện",
        "thu vien": "Thư viện",
        "trung tâm học liệu": "Thư viện",
        "hội trường f": "Hội trường F",
        "hoi truong f": "Hội trường F",
        "hội trường": "Hội trường F",
        # --- Các khu ---
        "khu a": "Khu A",
        "tòa a": "Khu A",
        "a": "Khu A",
        "khu b": "Khu B",
        "tòa b": "Khu B",
        "b": "Khu B",
        "khu c": "Khu C",
        "tòa c": "Khu C",
        "c": "Khu C",
        "khu d": "Khu D",
        "tòa d": "Khu D",
        "d": "Khu D",
        "khu e": "Khu E",
        "tòa e": "Khu E",
        "e": "Khu E",
        "khu f": "Khu F",
        "tòa f": "Khu F",
        "f": "Khu F",
        "khu h": "Khu H",
        "tòa h": "Khu H",
        "h": "Khu H",
        "khu s": "Khu S",
        "tòa s": "Khu S",
        "s": "Khu S",
        # --- Nhà xe ---
        "nhà xe khu b": "Nhà xe khu B",
        "nha xe khu b": "Nhà xe khu B",
        "bãi xe b": "Nhà xe khu B",
        "nhà xe khu e": "Nhà xe khu E",
        "nha xe khu e": "Nhà xe khu E",
        "bãi xe e": "Nhà xe khu E",
        # --- Ngã tư / Ngã rẽ ---
        "ngã tư 1": "Ngã tư 1",
        "nga tu 1": "Ngã tư 1",
        "ngã tư 2": "Ngã tư 2",
        "nga tu 2": "Ngã tư 2",
        "ngã tư 3": "Ngã tư 3",
        "nga tu 3": "Ngã tư 3",
        "ngã tư 4": "Ngã tư 4",
        "nga tu 4": "Ngã tư 4",
        "ngã rẽ 1": "Ngã rẽ 1",
        "nga re 1": "Ngã rẽ 1",
        "ngã rẽ 2": "Ngã rẽ 2",
        "nga re 2": "Ngã rẽ 2",
    }

    # Đưa chữ của AI về in thường và dịch sang chuẩn code (nếu không có trong từ điển thì giữ nguyên)
    # Thêm .strip() để tự động xóa sạch khoảng trắng thừa do AI sinh ra
    start_clean = alias_map.get(str(start).strip().lower(), str(start).strip())
    goal_clean = alias_map.get(str(goal).strip().lower(), str(goal).strip())
    # 2. BỨC TƯỜNG THÉP (RETURN NGAY TỪ ĐẦU): Kiểm tra bằng biến đã được dịch
    if start_clean not in graph:
        return f"Xin lỗi, tôi không có dữ liệu về điểm xuất phát '{start}' trên bản đồ."
    if goal_clean not in graph:
        return f"Xin lỗi, tôi không có dữ liệu về đích đến '{goal}' trên bản đồ."

    queue = [(0, start_clean, [])]
    seen = set()

    while queue:
        cost, current_node, path = heapq.heappop(queue)

        if current_node in seen:
            continue

        path = path + [current_node]
        seen.add(current_node)

        if current_node == goal_clean:
            # --- HÀM TỔNG QUÁT XỬ LÝ ĐƯỜNG ĐI DÀI NGẮN TÙY Ý ---
            if len(path) == 2:
                # Nếu chỉ đi thẳng từ điểm này sang điểm kia không qua ngã rẽ trung gian
                sentence = f"Đi thẳng từ {path[0]} đến {path[-1]}"
            else:
                # Nếu đi qua nhiều ngã rẽ: Lấy các điểm ở giữa ghép lại bằng dấu phẩy
                intermediates = ", qua ".join(path[1:-1])
                sentence = f"Đi từ {path[0]}, qua {intermediates}, để đến {path[-1]}"

            return f"{sentence}, tổng chiều dài khoảng {round(cost)} mét."

        for neighbor, weight in graph.get(current_node, {}).items():
            if neighbor not in seen:
                heapq.heappush(queue, (cost + weight, neighbor, path))

    return "Xin lỗi, không có đường đi nào kết nối hai khu vực này."
