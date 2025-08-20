import os
import subprocess

videos_subs_dir = input("Videos and Subtitles Directory: ").strip().replace("\\", "/")

while not os.path.exists(videos_subs_dir):
    print("❌ Path not found. Please try again.")
    videos_subs_dir = input("Videos and Subtitles Directory: ").strip().replace("\\", "/")
print("✅ Path found:", videos_subs_dir)

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

for file in os.listdir(videos_subs_dir):
    if file.endswith(".mp4"):
        base_name = os.path.splitext(file)[0]
        video_path = os.path.join(videos_subs_dir, file)
        subtitle_eng_path = os.path.join(videos_subs_dir, base_name + ".srt")
        subtitle_fa_path = os.path.join(videos_subs_dir, base_name + ".fa.srt")

        if not (os.path.exists(subtitle_eng_path) or os.path.exists(subtitle_fa_path)):
            continue

        output_path = os.path.join(Merged_videos_subs_dir, base_name + ".mp4")

        if os.path.exists(output_path):
            print(f"⚠️ Skipping, already exists: {output_path}")
            continue

        cmd = ["ffmpeg", "-i", video_path]

        if os.path.exists(subtitle_fa_path):
            cmd.extend(["-i", subtitle_fa_path])
        if os.path.exists(subtitle_eng_path):
            cmd.extend(["-i", subtitle_eng_path])

        cmd.extend([
            "-c:v", "copy",
            "-c:a", "copy",
            "-c:s", "mov_text",
            "-map", "0:v",
            "-map", "0:a"
        ])

        input_count = 1
        subtitle_stream_index = 0

        if os.path.exists(subtitle_fa_path) and os.path.exists(subtitle_eng_path):
            # Persian exists AND English exists
            cmd.extend([
                "-map", f"{input_count}:0",
                f"-metadata:s:s:{subtitle_stream_index}", "language=fas",
                f"-metadata:s:s:{subtitle_stream_index}", "title=Persian",
                f"-disposition:s:{subtitle_stream_index}", "default"
            ])
            input_count += 1
            subtitle_stream_index += 1

            cmd.extend([
                "-map", f"{input_count}:0",
                f"-metadata:s:s:{subtitle_stream_index}", "language=eng",
                f"-metadata:s:s:{subtitle_stream_index}", "title=English",
                f"-disposition:s:{subtitle_stream_index}", "0"
            ])
            input_count += 1
            subtitle_stream_index += 1

        elif os.path.exists(subtitle_fa_path):
            # Only Persian exists → make default
            cmd.extend([
                "-map", f"{input_count}:0",
                f"-metadata:s:s:{subtitle_stream_index}", "language=fas",
                f"-metadata:s:s:{subtitle_stream_index}", "title=Persian",
                f"-disposition:s:{subtitle_stream_index}", "default"
            ])
            input_count += 1
            subtitle_stream_index += 1

        elif os.path.exists(subtitle_eng_path):
            # Only English exists → make default
            cmd.extend([
                "-map", f"{input_count}:0",
                f"-metadata:s:s:{subtitle_stream_index}", "language=eng",
                f"-metadata:s:s:{subtitle_stream_index}", "title=English",
                f"-disposition:s:{subtitle_stream_index}", "default"
            ])
            input_count += 1
            subtitle_stream_index += 1

        cmd.append(output_path)

        try:
            print("▶️ Running:", " ".join(cmd))
            subprocess.run(cmd, check=True)
            print(f"✅ Merged: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg failed for {file}: {e}")

input("Press Enter key for exit...")
