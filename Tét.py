import uiautomator2 as u2
import time, subprocess, os

# ====== Kết nối thiết bị ======
devices = os.popen("adb devices").read().strip().split("\n")[1:]
if not devices:
    raise Exception("Không tìm thấy thiết bị nào!")
serial = devices[0].split()[0]
d = u2.connect(serial)
print(f"✅ Đã kết nối thiết bị: {serial}")

job_counter = 0  # đếm số job đã làm

# ====== Hàm hỗ trợ ======
def open_golike():
    subprocess.run([
        "adb", "-s", serial, "shell", "monkey",
        "-p", "com.golike",
        "-c", "android.intent.category.LAUNCHER", "1"
    ])
    time.sleep(6)

def tap_ok_adb():
    try:
        subprocess.run(["adb", "-s", serial, "shell", "input", "tap", "378", "975"])
        print("✅ Đã nhấn OK bằng ADB")
        return True
    except Exception as e:
        print(f"[WARN] Lỗi nhấn OK bằng ADB: {e}")
        return False

def click_retry(text=None, desc=None, retries=5):
    for _ in range(retries):
        try:
            if text and d(text=text).exists(timeout=3):
                d(text=text).click()
                return True
            if desc and d(description=desc).exists(timeout=3):
                d(description=desc).click()
                return True
        except Exception:
            time.sleep(1)
    return False

def wait_for_text(text, timeout=15):
    for _ in range(timeout):
        if d(textContains=text).exists:
            return True
        time.sleep(1)
    return False

def handle_ok_popup():
    for _ in range(5):
        tap_ok_adb()
        time.sleep(1)

# ====== Hàm xử lý job ======
def do_job():
    global job_counter

    # Chỉ mở GoLike một lần trước khi lấy job
    if job_counter == 0:
        open_golike()
        click_retry("Kiếm Thưởng")
        d(textContains="Facebook").click_exists(timeout=12)
        time.sleep(8)

    # Job buttons
    job_buttons = ["cho bài viết", "Tăng LIKE cho Fanpage", "Tăng Theo dõi", "Tham gia nhóm", "Comment"]
    job_found = False
    job_type = None

    # Lấy job
    for _ in range(3):
        for jb in job_buttons:
            obj = d(textContains=jb)
            if obj.exists(timeout=5):
                obj.click()
                job_found = True
                job_type = jb
                time.sleep(3)
                break
        if job_found:
            break
        print("⏭️ Không có job → kéo xuống")
        d.swipe(500, 1500, 500, 500)
        time.sleep(2)

    if not job_found:
        print("❌ Không tìm thấy job")
        return

    print(f"📌 Job type: {job_type}")

    try:
        if job_type == "Tăng Theo dõi":
            for _ in range(8):
                if click_retry("Theo dõi") or click_retry(desc="Follow"):
                    print("👤 Đã Theo dõi xong")
                    break
                time.sleep(1)

        else:
            # Các job khác
            if click_retry("Trình duyệt"):
                print("🌐 Mở trình duyệt")
                time.sleep(6)

            liked = False
            if click_retry("Thích") or click_retry(desc="Like") or click_retry(desc="Love"):
                liked = True
                print("👍 Thích/Love xong")
                d.long_click(500,500)
                click_retry(desc="Love")
                open_golike()

            if not liked:
                print("⚠️ Không có nút Thích/Love → Báo lỗi")
                d.swipe(500,1200,500,800)
                click_retry("Báo lỗi")
                time.sleep(2)
                click_retry("Gửi báo cáo")
                return

      
        time.sleep(5)
        if wait_for_text("Hoàn thành", timeout=12):
            click_retry("Hoàn thành")
            time.sleep(5)
            handle_ok_popup()
            print("✅ Hoàn thành, nhận xu")
        else:
            click_retry("Báo lỗi")
            print("❌ Job lỗi, đã báo lỗi")

        job_counter += 1
        if job_counter >= 3:
            job_counter = 0  # reset sau 3 job

    except Exception as e:
        print(f"[WARN] Lỗi xử lý job: {e}")

# ====== Chạy loop ======
while True:
    try:
        do_job()
        time.sleep(2)
    except Exception as e:
        print(f"[ERROR] Lỗi trong quá trình chạy: {e}")
        time.sleep(5)
