import uiautomator2 as u2
import time, subprocess, os, re, requests

# --- COOKIE FACEBOOK ---
COOKIE = input("Nhập cookie Facebook: ").strip()
HEADERS = {
    "cookie": COOKIE,
    "user-agent": "Mozilla/5.0 (Linux; Android 10)"
}

# --- Kết nối thiết bị ---
devices = os.popen("adb devices").read().strip().split("\n")[1:]
if not devices or len(devices[0].strip()) == 0:
    print("❌ Không tìm thấy thiết bị ADB")
    exit()

serial = devices[0].split()[0]
print(f"📱 Đang kết nối thiết bị: {serial}")
d = u2.connect(serial)

def open_golike():
    """Mở app GoLike"""
    print("📲 Đang mở app GoLike...")
    subprocess.run(["adb", "-s", serial, "shell", "monkey", "-p", "com.golike",
                    "-c", "android.intent.category.LAUNCHER", "1"])
    time.sleep(8)

def fb_react(fb_id, reaction):
    """Thực hiện reaction bằng Graph API"""
    url = f"https://graph.facebook.com/{fb_id}/reactions"
    res = requests.post(url, headers=HEADERS, data={"type": reaction.lower()})
    print(f"[DEBUG] Reaction {reaction} → {res.status_code}")
    return res.status_code == 200

def fb_likepage(fb_id):
    """Like page bằng Graph API"""
    url = f"https://graph.facebook.com/{fb_id}/likes"
    res = requests.post(url, headers=HEADERS)
    print(f"[DEBUG] Like Page → {res.status_code}")
    return res.status_code == 200

swipe_count = 0  # Đếm số lần kéo xuống

def do_job():
    global swipe_count

    # B1: Vào kiếm thưởng
    if d(text="Kiếm Thưởng").exists(timeout=10):
        d(text="Kiếm Thưởng").click_exists(timeout=10)
    else:
        print("❌ Không tìm thấy nút Kiếm thưởng")
        return
    time.sleep(2)

    # B2: Vào Facebook
    if d(text="Facebook").exists(timeout=10):
        d(text="Facebook").click_exists(timeout=10)
    else:
        print("❌ Không tìm thấy mục Facebook")
        return
    time.sleep(10)

    # B3: Tìm job
    if d(textContains="cho bài viết").exists():
        d(textContains="cho bài viết").click_exists(timeout=10)
        swipe_count = 0
    elif d(textContains="Tăng Like cho Fanpage").exists():
        d(textContains="Tăng Like cho Fanpage").click_exists(timeout=10)
        swipe_count = 0
    else:
        swipe_count += 1
        if swipe_count <= 2:
            print(f"⏭️ Không có job, kéo xuống (lần {swipe_count})")
            d.swipe(500, 1500, 500, 500)  # Kéo xuống
        else:
            print("🔄 Không có job sau 2 lần → Kéo lên để làm mới")
            d.swipe(500, 500, 500, 1500)  # Kéo lên
            swipe_count = 0
        return

    time.sleep(3)

    # B4: Lấy Job ID + Fb ID
    job_id = None
    fb_id = None
    for node in d.xpath("//android.widget.TextView").all():
        txt = (node.text or "").strip()
        job_match = re.search(r"Job\s*Id[:\s]*(\d+)", txt, re.I)
        fb_match = re.search(r"Fb\s*Id[:\s]*(\d+)", txt, re.I)
        if job_match:
            job_id = job_match.group(1)
        if fb_match:
            fb_id = fb_match.group(1)

    if not job_id or not fb_id:
        print("❌ Không lấy được Job ID hoặc Fb ID")
        d(text="Báo lỗi").click_exists(timeout=5)
        return

    print(f"📌 Job: {job_id}, Fb: {fb_id}")

    # B5: Kiểm tra loại job
    job_texts = [n.text for n in d.xpath("//android.widget.TextView").all() if n.text]
    job_type = " ".join(job_texts)
    print(f"[DEBUG] Job text: {job_type}")

    ok = False
    if "LIKE" in job_type and "bài viết" in job_type:
        ok = fb_react(fb_id, "LIKE")
    elif "LOVE" in job_type:
        ok = fb_react(fb_id, "LOVE")
    elif "WOW" in job_type:
        ok = fb_react(fb_id, "WOW")
    elif "ANGRY" in job_type:
        ok = fb_react(fb_id, "ANGRY")
    elif "HAHA" in job_type:
        ok = fb_react(fb_id, "HAHA")
    elif "HUHU" in job_type or "SAD" in job_type:
        ok = fb_react(fb_id, "SAD")
    elif "Fanpage" in job_type or "LIKEPAGE" in job_type:
        ok = fb_likepage(fb_id)

    # B6: Quay lại Golike
    open_golike()
    time.sleep(3)

    if ok:
        if d(text="Hoàn thành").exists(timeout=10):
            d(text="Hoàn thành").click_exists(timeout=10)
            print("✅ Hoàn thành, nhận xu")
            time.sleep(3)
        else:
            print("⚠️ Không tìm thấy nút Hoàn thành")
    else:
        d(text="Báo lỗi").click_exists(timeout=5)
        print("❌ Job lỗi, đã báo lỗi")
        d.swipe(500, 1500, 500, 500)

if __name__ == "__main__":
    open_golike()
    while True:
        do_job()
