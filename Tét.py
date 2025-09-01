import uiautomator2 as u2
import time, subprocess, os

# Kết nối thiết bị
devices = os.popen("adb devices").read().strip().split("\n")[1:]
serial = devices[0].split()[0]
d = u2.connect(serial)

def open_golike():
    subprocess.run(["adb", "-s", serial, "shell", "monkey", "-p", "com.golike", 
                    "-c", "android.intent.category.LAUNCHER", "1"])
    time.sleep(8)

def do_job_like():
    # B1: Ấn Kiếm thưởng
    d(text="Kiếm thưởng").click_exists(timeout=10)
    time.sleep(2)

    # B2: Ấn Facebook
    d(text="Facebook").click_exists(timeout=10)
    time.sleep(3)
    print("Gửi yêu cầu lấy job")
    time.sleep(10)
    # B3: Tìm job LIKE
    d(textContains="LIKE cho bài viết").click_exists(timeout=10)
    time.sleep(2)

    # B4: Ấn nút Facebook để mở app
    if d(text="Facebook").exists:
        d(text="Facebook").click()
        print("📲 Đang mở Facebook...")
        time.sleep(5)

        # B5: Ấn nút LIKE trong FB
        if d(text="Thích").exists:
            d(text="Thích").click()
            print("👍 Đã LIKE bài viết")
        else:
            print("❌ Không thấy nút LIKE trong FB")
            return False

        # Quay lại Golike
        open_golike()
        time.sleep(3)

        # B6: Ấn Hoàn thành
        d(text="Hoàn thành").click_exists(timeout=10)
        print("✅ Đã hoàn thành job LIKE")

        # B7: Chờ nhận xu
        time.sleep(3)
        return True
    else:
        print("❌ Không thấy nút FACEBOOK trong job")
        return False

if __name__ == "__main__":
    open_golike()
    while True:
        ok = do_job_like()
        if not ok:
            print("⏭️ Lướt tiếp hoặc thử lại")
            d.swipe(500, 1500, 500, 500)  # scroll xuống tìm job khác
            time.sleep(2)
d(text="LIKE").click_exists(timeout=10)
# 6. Lấy thông tin job
job = d.xpath('//android.widget.TextView[contains(@text,"Fb Id")]').get(timeout=10)
if job:
    print("Job info:", job.text)

# 7. Click chọn job
d(textContains="TĂNG LIKE CHO BÀI VIẾT").click_exists(timeout=10)
