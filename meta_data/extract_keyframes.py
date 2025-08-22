import os
import cv2
import re
import ast

TXT_PATH = "Crash-1500.txt"
VIDEO_DIR = "./test_data/"
OUTPUT_DIR = "./keyframes-crash-pic1"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Counter for sequential image naming
image_counter = 1

# Read all lines from the crash data file
with open(TXT_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Processing {len(lines)} videos for crash sequence extraction (3 frames before to 2 frames after)...")

# Process all videos
for line_num, line in enumerate(lines, 1):
    parts = line.strip().split(",")
    vidname = parts[0]
        
    # Extract binlabels using regex
    match = re.search(r"\[.*?\]", line)
    if not match:
        print(f"Line {line_num}: {vidname} - binlabels extraction failed, skipping")
        continue
            
    binlabels_str = match.group(0)
    try:
        binlabels = ast.literal_eval(binlabels_str)
    except:
        print(f"Line {line_num}: {vidname} - binlabels parsing failed, skipping")
        continue

    video_path = os.path.join(VIDEO_DIR, f"{vidname}.mp4")

    if not os.path.exists(video_path):
        print(f"Line {line_num}: Video {video_path} not found, skipping")
        continue

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
    if total_frames == 0:
        print(f"Line {line_num}: {vidname} - Unable to read video frames, skipping")
        cap.release()
        continue

    # Find the FIRST crash frame (label == 1)
    first_crash_idx = None
    for idx, label in enumerate(binlabels):
        if label == 1:
            first_crash_idx = idx
            break  # Stop at the first occurrence of 1
            
    if first_crash_idx is not None:
        # Calculate frame range: 3 frames before to 2 frames after crash
        frames_before = 10  # 3 frames before
        frames_after = 2   # 2 frames after
        
        start_frame = max(0, first_crash_idx - frames_before)
        end_frame = min(total_frames - 1, first_crash_idx + frames_after)
        
        print(f"Line {line_num}: {vidname} - Extracting frames {start_frame} to {end_frame} (crash at {first_crash_idx})")
        
        # Extract all frames in the range
        frames_extracted = 0
        for frame_idx in range(start_frame, end_frame + 1):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                # 计算相对于碰撞帧的帧偏移
                frame_offset = frame_idx - first_crash_idx
                
                # 生成文件名：包含视频名、帧索引和帧偏移信息
                filename = f"image_{image_counter:06d}_{vidname}_frame{frame_idx}_offset{frame_offset:+d}.jpg"
                out_path = os.path.join(OUTPUT_DIR, filename)
                cv2.imwrite(out_path, frame)
                
                frames_extracted += 1
                image_counter += 1
            else:
                print(f"Line {line_num}: {vidname} - Failed to read frame {frame_idx}")
        
        print(f"Line {line_num}: {vidname} - Successfully extracted {frames_extracted} frames")
        
    else:
        print(f"Line {line_num}: {vidname} - No crash frames found (no label=1)")
            
    cap.release()

print("Crash sequence extraction completed!")
print(f"Results saved in: {OUTPUT_DIR}")

# Print summary statistics
def print_summary():
    all_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.jpg')]
    total_frames = len(all_files)
    
    # 统计每个视频提取的帧数
    video_stats = {}
    for filename in all_files:
        # 从文件名中提取视频名
        parts = filename.split('_')
        if len(parts) >= 3:
            vidname = parts[2]
            video_stats[vidname] = video_stats.get(vidname, 0) + 1
    
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY:")
    print(f"Total frames extracted: {total_frames}")
    print(f"Total videos processed: {len(video_stats)}")
    print(f"Average frames per video: {total_frames/len(video_stats):.1f}" if video_stats else "N/A")
    print(f"Location: {OUTPUT_DIR}")
    print("-"*60)
    print("Per-video statistics:")
    for vidname, count in sorted(video_stats.items()):
        print(f"  {vidname}: {count} frames")
    print("="*60)

print_summary()