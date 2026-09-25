import math

# 1. Khai báo tọa độ
# 1. Khai báo tọa độ (WAYPOINTS)
# Tọa độ (0.0, 0.0) đang để trống, bạn có thể điền số liệu thực tế sau
# 1. Khai báo tọa độ
WAYPOINTS = {
    "Cổng chính": (16.073680, 108.149922),
    "Cổng phụ 1": (16.074488, 108.152058),
    "Cổng phụ 2": (0.0, 0.0),
    "Căn tin 1": (16.075385, 108.154476),
    "Căn tin 2": (16.074316, 108.150405),
    "Thư viện": (16.074231, 108.150635),
    "Ngã tư 1": (16.074287, 108.151557),
    "Ngã tư 2": (16.074954, 108.153262),
    "Ngã tư 3": (16.075784, 108.152820),
    "Ngã tư 4": (16.075409, 108.153303),
    "Ngã rẽ 1": (16.073907, 108.150542),
    "Ngã rẽ 2": (16.074108, 108.150472),
    "Khu A": (16.075409, 108.153303),
    "Khu B": (16.074488, 108.152058),
    "Khu C": (16.074427, 108.152978),
    "Khu D": (16.076342, 108.152915),
    "Khu E": (16.074630, 108.153399),
    "Khu F": (16.075571, 108.152330),
    "Khu H": (16.076181, 108.152574),
    "Khu S": (16.075177, 108.154003),
    "Nhà xe khu B": (16.075625, 108.151391),
    "Nhà xe khu E": (16.075385, 108.154476),
    "Hội trường F": (0.0, 0.0),  # Đã bổ sung vì ở dưới có gọi đến
}

# 2. Khai báo đường đi (Danh sách các đoạn thẳng nối liền nhau)
connections = [
    # Tuyến cổng chính và khu vực lân cận
    ("Cổng chính", "Ngã rẽ 1"),
    ("Ngã rẽ 1", "Ngã tư 1"),
    ("Ngã rẽ 2", "Thư viện"),
    ("Ngã rẽ 2", "Căn tin 2"),
    ("Ngã tư 1", "Thư viện"),
    ("Ngã tư 1", "Cổng phụ 1"),
    ("Ngã tư 1", "Khu B"),
    ("Cổng phụ 1", "Khu B"),
    # Tuyến cổng phụ và nhánh lên Khu B, Khu C
    ("Khu B", "Ngã tư 2"),
    ("Cổng phụ 1", "Ngã tư 2"),
    ("Ngã tư 4", "Hội trường F"),
    ("Ngã tư 4", "Khu B"),
    ("Ngã tư 4", "Cổng phụ 1"),
    ("Ngã tư 2", "Khu A"),
    ("Ngã tư 2", "Ngã tư 3"),
    ("Ngã tư 2", "Khu E"),
    ("Khu S", "Căn tin 1"),
    ("Khu S", "Nhà xe khu E"),
    ("Căn tin 1", "Nhà xe khu E"),
    ("Ngã tư 2", "Khu S"),
    ("Khu E", "Khu C"),
    ("Khu C", "Cổng phụ 2"),
    ("Ngã tư 3", "Khu F"),
    ("Ngã tư 3", "Khu H"),
    ("Khu H", "Khu D"),
    ("Khu H", "Nhà xe khu B"),
    ("Khu F", "Hội trường F"),
]


# 3. Tính toán Haversine
def get_distance(node1, node2):
    lat1, lon1 = WAYPOINTS[node1]
    lat2, lon2 = WAYPOINTS[node2]
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# 4. Hàm sinh tự động ra cấu trúc dữ liệu JSON (Dictionary)
def build_graph():
    graph = {node: {} for node in WAYPOINTS}
    for u, v in connections:
        dist = get_distance(u, v)
        graph[u][v] = dist
        graph[v][u] = dist
    return graph


# Biến này sẽ chứa toàn bộ đồ thị đã được tính toán xong
BACHKHOA_GRAPH = build_graph()
