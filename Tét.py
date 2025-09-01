# go fb beta
import uiautomator2 as u2
import subprocess
import time
import os

# 1. Lấy danh sách thiết bị
devices = os.popen("adb devices").read().strip().split("\n")[1:]
devices = [d.split()[0] for d in devices if "device" in d]

if not devices:
    raise Exception("Không tìm thấy thiết bị!")
elif len(devices) == 1:
    serial = devices[0]
else:
    print("Phát hiện nhiều thiết bị:")
    for i, dev in enumerate(devices):
        print(f"{i+1}. {dev}")
    choice = int(input("Chọn thiết bị: ")) - 1
    serial = devices[choice]

print(f"Kết nối đến thiết bị: {serial}")
d = u2.connect(serial)

# 2. Mở app Golike bằng monkey
subprocess.run(["adb", "-s", serial, "shell", "monkey", "-p", "com.golike", "-c", "android.intent.category.LAUNCHER", "1"])

# 3. Chờ app load
time.sleep(10)

# 4. Click "Kiếm thưởng"
d(text="Kiếm thưởng").click_exists(timeout=10)

# 5. Vào mục Facebook job
d(text="Facebook").click_exists(timeout=10)

d(text="LIKE").click_exists(timeout=10)
# 6. Lấy thông tin job
job = d.xpath('//android.widget.TextView[contains(@text,"Fb Id")]').get(timeout=10)
if job:
    print("Job info:", job.text)

# 7. Click chọn job
d(textContains="TĂNG LIKE CHO BÀI VIẾT").click_exists(timeout=10)
