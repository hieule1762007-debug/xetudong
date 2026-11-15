
import numpy as np

# 1. CHUẨN BỊ DỮ LIỆU DẠY HỌC (Dataset)
# 5 cột tương ứng 5 mắt cảm biến IR: [Trái_Ngoài, Trái_Trong, Giữa, Phải_Trong, Phải_Ngoài]
X = np.array([
    [1, 0, 0, 0, 0],  # Lệch hẳn sang trái
    [0, 1, 0, 0, 0],  # Lệch nhẹ sang trái
    [0, 0, 1, 0, 0],  # Giữa tâm line
    [0, 0, 0, 1, 0],  # Lệch nhẹ sang phải
    [0, 0, 0, 0, 1],  # Lệch hẳn sang phải
    [1, 1, 0, 0, 0],  # Đè 2 mắt trái
    [0, 0, 0, 1, 1],  # Đè 2 mắt phải
], dtype=np.float32)

# Góc lái mục tiêu (Ground Truth Labels) tương ứng với 7 trường hợp trên
# -1.0: Bẻ lái gắt sang trái | 0.0: Đi thẳng | +1.0: Bẻ lái gắt sang phải
Y_true = np.array([
    [-1.0],
    [-0.5],
    [ 0.0],
    [ 0.5],
    [ 1.0],
    [-0.75],
    [ 0.75]
], dtype=np.float32)

# 2. KHỞI TẠO MODEL (5 trọng số W ngẫu nhiên và 1 độ lệch b)
np.random.seed(42)
W = np.random.randn(5, 1)  # Ma trận trọng số (5x1) - ban đầu toàn số vô nghĩa
b = np.zeros((1,))         # Bias ban đầu = 0

learning_rate = 0.1        # Tốc độ học (giống hệ số bước nhảy)
epochs = 500               # Số lần học đi học lại

print("Trọng số W ban đầu (ngẫu nhiên):", W.flatten().round(2))

# 3. QUÁ TRÌNH HUẤN LUYỆN (TRAINING LOOP)
for epoch in range(epochs):
    # --- BƯỚC A: LAN TRUYỀN TIẾN (Forward Pass) ---
    # Máy đoán thử góc lái dựa trên W hiện tại: Y_pred = X * W + b
    Y_pred = np.dot(X, W) + b

    # --- BƯỚC B: TÍNH SAI SỐ (Loss Function - Mean Squared Error) ---
    # Sai số e = (Giá trị đoán - Giá trị thật)
    error = Y_pred - Y_true
    loss = np.mean(error ** 2)  # Bình phương sai số trung bình

    # --- BƯỚC C: LAN TRUYỀN NGƯỢC (Backpropagation - Tính đạo hàm) ---
    # Đạo hàm của hàm Loss theo W và b để biết cần tăng hay giảm W bao nhiêu
    N = X.shape[0]
    dW = (2 / N) * np.dot(X.T, error)  # Đạo hàm theo W: dL/dW
    db = (2 / N) * np.sum(error)       # Đạo hàm theo b: dL/db

    # --- BƯỚC D: CẬP NHẬT TRỌNG SỐ (Gradient Descent) ---
    # Đi ngược hướng đạo hàm để ép sai số tiến về 0
    W = W - learning_rate * dW
    b = b - learning_rate * db

    if epoch % 100 == 0:
        print(f"Epoch {epoch:3d} | Sai số (Loss): {loss:.6f}")

# 4. KẾT QUẢ SAU KHI HỌC XONG
print("\n--- KẾT QUẢ SAU KHI AI HỌC XONG ---")
print("Trọng số W máy tự tìm ra:", W.flatten().round(3))
print("Độ lệch b máy tự tìm ra :", b.round(3))