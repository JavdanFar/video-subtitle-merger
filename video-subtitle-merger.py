import os
import subprocess

# دریافت مسیر پوشه ویدیو و زیرنویس‌ها
videos_subs_dir = input("Videos and Subtitles Directory: ").strip().replace("\\", "/")
while not os.path.exists(videos_subs_dir):
    print("❌ Path not found. Please try again.")
    videos_subs_dir = input("Videos and Subtitles Directory: ").strip().replace("\\", "/")
print("✅ Path found:", videos_subs_dir)

# مسیر مقصد فایل‌های ادغام شده
Merged_videos_subs_dir = input("Merged Files Destination (optional): ").strip().replace("\\", "/")
while not os.path.exists(Merged_videos_subs_dir):
    if Merged_videos_subs_dir == "":
        Merged_videos_subs_dir = f"{videos_subs_dir}/Merged"
        print(f"Your directory for merged files is: \n {Merged_videos_subs_dir}")
        break
    print("❌ Path not found. Please try again.")
    Merged_videos_subs_dir = input("Merged Files Destination (optional): ").strip().replace("\\", "/")
print("✅ Path found:", Merged_videos_subs_dir)

os.makedirs(Merged_videos_subs_dir, exist_ok=True)

# پردازش فایل‌ها
for file in os.listdir(videos_subs_dir):
    if file.endswith(".mp4"):
        base_name = os.path.splitext(file)[0]
        video_path = os.path.join(videos_subs_dir, file)
        subtitle_eng_path = os.path.join(videos_subs_dir, base_name + ".srt")
        subtitle_fa_path = os.path.join(videos_subs_dir, base_name + ".fa.srt")

        # اگر هیچ زیرنویسی وجود ندارد، رد کن
        if not (os.path.exists(subtitle_eng_path) or os.path.exists(subtitle_fa_path)):
            continue

        output_path = os.path.join(Merged_videos_subs_dir, base_name + ".mkv")
        if os.path.exists(output_path):
            print(f"⚠️ Skipping, already exists: {output_path}")
            continue

        cmd = ["ffmpeg", "-i", video_path]

        # اضافه کردن زیرنویس‌ها به عنوان ورودی
        if os.path.exists(subtitle_fa_path):
            cmd.extend(["-i", subtitle_fa_path])
        if os.path.exists(subtitle_eng_path):
            cmd.extend(["-i", subtitle_eng_path])

        # نگه داشتن فقط ویدیو و صدا (حذف تمام زیرنویس‌های قبلی)
        cmd.extend([
            "-map", "0:v",
            "-map", "0:a?",
        ])

        input_count = 1
        subtitle_stream_index = 0

        # اضافه کردن زیرنویس‌ها به صورت SRT واقعی داخل MKV
        if os.path.exists(subtitle_fa_path) and os.path.exists(subtitle_eng_path):
            # Persian → غیر پیش‌فرض
            cmd.extend([
                "-map", f"{input_count}:0",
                "-c:s:s", "srt",
                f"-metadata:s:s:{subtitle_stream_index}", "language=fas",
                f"-metadata:s:s:{subtitle_stream_index}", "title=Persian",
                f"-disposition:s:{subtitle_stream_index}", "0"  # NOT default
            ])
            input_count += 1
            subtitle_stream_index += 1

            # English → پیش‌فرض
            cmd.extend([
                "-map", f"{input_count}:0",
                "-c:s:s", "srt",
                f"-metadata:s:s:{subtitle_stream_index}", "language=eng",
                f"-metadata:s:s:{subtitle_stream_index}", "title=English",
                f"-disposition:s:{subtitle_stream_index}", "default"
            ])
        elif os.path.exists(subtitle_fa_path):
            # فقط فارسی → پیش‌فرض چون گزینه دیگری نیست
            cmd.extend([
                "-map", f"{input_count}:0",
                "-c:s:s", "srt",
                f"-metadata:s:s:{subtitle_stream_index}", "language=fas",
                f"-metadata:s:s:{subtitle_stream_index}", "title=Persian",
                f"-disposition:s:{subtitle_stream_index}", "default"
            ])
        elif os.path.exists(subtitle_eng_path):
            # فقط انگلیسی
            cmd.extend([
                "-map", f"{input_count}:0",
                "-c:s:s", "srt",
                f"-metadata:s:s:{subtitle_stream_index}", "language=eng",
                f"-metadata:s:s:{subtitle_stream_index}", "title=English",
                f"-disposition:s:{subtitle_stream_index}", "default"
            ])

        # کپی ویدیو و صدا بدون تغییر
        cmd.extend(["-c:v", "copy", "-c:a", "copy"])

        cmd.append(output_path)

        try:
            print("▶️ Running:", " ".join(cmd))
            subprocess.run(cmd, check=True)
            print(f"✅ Merged: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg failed for {file}: {e}")

input("Press Enter key for exit...")
