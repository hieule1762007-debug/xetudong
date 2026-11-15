import numpy as np

# 1. CHUẨN BỊ DỮ LIỆU ĐẦU VÀO (X) VÀ MỤC TIÊU (Y_true)
X = np.array(
    [
        [1.0, 0.0, 0.0, 0.0, 0.0],  # Lệch hẳn trái
        [0.0, 1.0, 0.0, 0.0, 0.0],  # Lệch nhẹ trái
        [0.0, 0.0, 1.0, 0.0, 0.0],  # Giữa tâm line
        [0.0, 0.0, 0.0, 1.0, 0.0],  # Lệch nhẹ phải
        [0.0, 0.0, 0.0, 0.0, 1.0],  # Lệch hẳn phải
        [1.0, 1.0, 0.0, 0.0, 0.0],  # Đè 2 mắt trái
        [0.0, 0.0, 0.0, 1.0, 1.0],  # Đè 2 mắt phải
    ],
    dtype=np.float32,
)

Y_true = np.array(
    [[-1.0], [-0.5], [0.0], [0.5], [1.0], [-0.75], [0.75]], dtype=np.float32
)

# 2. KHỞI TẠO TRỌNG SỐ NGẪU NHIÊN (Tầng 2: Có 1 Tầng ẩn gồm 4 nơ-ron)
np.random.seed(42)

# Tầng 1 (Tầng ẩn): Nhận 5 đầu vào, xuất ra 4 đặc trưng (W1 kích thước 5x4)
W1 = np.random.randn(5, 4) * 0.1
b1 = np.zeros((1, 4))

# Tầng 2 (Tầng đầu ra): Nhận 4 đặc trưng từ tầng ẩn, xuất ra 1 giá trị góc lái (W2 kích thước 4x1)
W2 = np.random.randn(4, 1) * 0.1
b2 = np.zeros((1, 1))


# Hàm kích hoạt ReLU (giúp bẻ cong không gian, xử lý phi tuyến tính)
def relu(z):
    return np.maximum(0, z)


# Đạo hàm của hàm ReLU (dùng khi tính lan truyền ngược)
def relu_derivative(z):
    return np.float32(z > 0)


learning_rate = 0.1

# 3. VÒNG LẶP HUẤN LUYỆN (TRAINING LOOP)
for epoch in range(1000):
    # --- BƯỚC A: LAN TRUYỀN TIẾN (FORWARD PASS) ---
    # Tính toán ở Tầng ẩn
    Z1 = np.dot(X, W1) + b1
    A1 = relu(Z1)  # Cho qua hàm kích hoạt ReLU

    # Tính toán ở Tầng đầu ra
    Z2 = np.dot(A1, W2) + b2
    Y_pred = Z2  # Kết quả xe dự đoán

    # Tính sai số (Loss - Hàm MSE: Mean Squared Error)
    loss = np.mean((Y_pred - Y_true) ** 2)

    # --- BƯỚC B: LAN TRUYỀN NGƯỢC (BACKWARD PASS - TỰ TÍNH ĐẠO HÀM) ---
    N = X.shape[0]

    # Đạo hàm lỗi tại đầu ra (Tầng 2)
    dY_pred = 2 * (Y_pred - Y_true) / N
    dW2 = np.dot(A1.T, dY_pred)
    db2 = np.sum(dY_pred, axis=0, keepdims=True)

    # Lan truyền ngược sai số ngược về Tầng ẩn qua quy tắc chuỗi (Chain Rule)
    dA1 = np.dot(dY_pred, W2.T)
    dZ1 = dA1 * relu_derivative(Z1)  # Nhân với đạo hàm ReLU
    dW1 = np.dot(X.T, dZ1)
    db1 = np.sum(dZ1, axis=0, keepdims=True)

    # --- BƯỚC C: CẬP NHẬT TRỌNG SỐ (GRADIENT DESCENT) ---
    W1 -= learning_rate * dW1
    b1 -= learning_rate * db1
    W2 -= learning_rate * dW2
    b2 -= learning_rate * db2

    # In sai số mỗi 200 vòng lặp để theo dõi quá trình học
    if epoch % 200 == 0:
        print(f"Epoch {epoch} | Sai số (Loss): {loss:.6f}")

# 4. KẾT QUẢ SAU KHI HỌC XONG
print("\n--- KẾT QUẢ DỰ ĐOÁN CUỐI CÙNG SO VỚI THỰC TẾ ---")
print("Y_true (Đáp án chuẩn) | Y_pred (Máy đoán)")
for true, pred in zip(Y_true, Y_pred):
    print(f"[{true[0]:5.2f}]              | [{pred[0]:5.2f}]")
