import re
import csv

# Configuration
TXT_PATH = "Crash-1500.txt"
OUTPUT_PATH = "video_prompts.csv"
FRAMES_PER_SECOND = 10  # Adjust based on your video frame rate
TOTAL_FRAMES = 50

def frames_to_timestamp(frame_num, fps=FRAMES_PER_SECOND):
    """Convert frame number to timestamp format like 1s, 3s, 5s"""
    seconds = frame_num / fps
    return f"{seconds:.0f}s"

def analyze_crash_sequence(binlabels):
    """Analyze binary labels to find crash timing"""
    labels = [int(x) for x in binlabels]
    
    # Find first and last crash frames
    crash_frames = [i for i, label in enumerate(labels) if label == 1]
    
    if not crash_frames:
        return None, None, None, None
    
    pre_crash_end = crash_frames[0] - 1
    crash_start = crash_frames[0]
    crash_end = crash_frames[-1]
    post_crash_start = crash_frames[-1] + 1
    
    return pre_crash_end, crash_start, crash_end, post_crash_start

def generate_crash_prompt(timing, weather, egoinvolve, binlabels):
    """Generate crash prompt in the format [1s: description] [3s: description]"""
    ego_text = "the dashcam car" if egoinvolve.lower() == "yes" else "other vehicles"
    weather_desc = weather.lower() if weather.lower() != "normal" else ""
    time_desc = f"during {timing.lower()}" if timing.lower() != "normal" else ""
    
    sequence = analyze_crash_sequence(binlabels)
    if sequence == (None, None, None, None):
        # No crash frames - shouldn't happen but handle gracefully
        return f"[0s: Dashcam footage shows normal driving] [2s: Traffic continues normally] [4s: Scene remains stable]"
    
    pre_crash_end, crash_start, crash_end, post_crash_start = sequence
    
    prompt_parts = []
    
    # Pre-crash phase
    if pre_crash_end >= 0:
        pre_time = frames_to_timestamp(0)
        conditions = []
        if weather_desc: conditions.append(f"in {weather_desc} weather")
        if time_desc: conditions.append(time_desc)
        condition_text = " ".join(conditions)
        
        prompt_parts.append(f"[{pre_time}: Dashcam shows normal driving {condition_text}]")
    
    # Crash moment
    crash_time = frames_to_timestamp(crash_start)
    if crash_start == crash_end:
        prompt_parts.append(f"[{crash_time}: Crash occurs involving {ego_text}]")
    else:
        crash_end_time = frames_to_timestamp(crash_end)
        prompt_parts.append(f"[{crash_time}: Crash begins involving {ego_text}]")
        if crash_end - crash_start > 2:  # Only add end timestamp if crash is long
            prompt_parts.append(f"[{crash_end_time}: Crash impact concludes]")
    
    # Post-crash phase
    if post_crash_start < TOTAL_FRAMES:
        post_time = frames_to_timestamp(post_crash_start)
        prompt_parts.append(f"[{post_time}: Aftermath and recovery visible]")
    
    return " ".join(prompt_parts)

def generate_nearcrash_prompt(timing, weather, egoinvolve, binlabels):
    """Generate near-crash prompt"""
    ego_text = "the dashcam car" if egoinvolve.lower() == "yes" else "other vehicles"
    weather_desc = weather.lower() if weather.lower() != "normal" else ""
    time_desc = f"during {timing.lower()}" if timing.lower() != "normal" else ""
    
    sequence = analyze_crash_sequence(binlabels)
    if sequence == (None, None, None, None):
        # No crash frames - assume near-miss happens mid-sequence
        middle_frame = TOTAL_FRAMES // 2
        pre_crash_end = middle_frame - 5
        crash_start = middle_frame
        crash_end = middle_frame + 2
        post_crash_start = middle_frame + 3
    else:
        pre_crash_end, crash_start, crash_end, post_crash_start = sequence
    
    prompt_parts = []
    
    # Pre-incident
    if pre_crash_end >= 0:
        pre_time = frames_to_timestamp(0)
        conditions = []
        if weather_desc: conditions.append(f"in {weather_desc} weather")
        if time_desc: conditions.append(time_desc)
        condition_text = " ".join(conditions)
        
        prompt_parts.append(f"[{pre_time}: Normal driving {condition_text}]")
    
    # Near-crash event
    incident_time = frames_to_timestamp(crash_start)
    prompt_parts.append(f"[{incident_time}: Near-crash event with {ego_text}, danger avoided]")
    
    # Recovery
    if post_crash_start < TOTAL_FRAMES:
        recovery_time = frames_to_timestamp(post_crash_start)
        prompt_parts.append(f"[{recovery_time}: Vehicles return to safe driving]")
    
    return " ".join(prompt_parts)

def generate_safe_prompt(timing, weather, egoinvolve):
    """Generate safe driving prompt"""
    weather_desc = weather.lower() if weather.lower() != "normal" else ""
    time_desc = f"during {timing.lower()}" if timing.lower() != "normal" else ""
    
    conditions = []
    if weather_desc: conditions.append(f"in {weather_desc} weather")
    if time_desc: conditions.append(time_desc)
    condition_text = " ".join(conditions)
    
    start_time = frames_to_timestamp(0)
    mid_time = frames_to_timestamp(TOTAL_FRAMES // 2)
    end_time = frames_to_timestamp(TOTAL_FRAMES - 1)
    
    return f"[{start_time}: Dashcam shows safe driving {condition_text}] [{mid_time}: Traffic flows normally] [{end_time}: Journey continues safely]"

def main():
    # Process Crash-1500.txt
    with open(TXT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["vidname", "crash_prompt", "nearcrash_prompt", "safe_prompt"])
        
        processed = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse the line format: vidname,[binary_array],startframe,youtubeID,timing,weather,egoinvolve
            bracket_start = line.find('[')
            bracket_end = line.find(']')
            
            if bracket_start == -1 or bracket_end == -1:
                print(f"Warning: Invalid format in line: {line[:50]}...")
                continue
            
            # Extract components
            vidname = line[:bracket_start].rstrip(',')
            binlabels_str = line[bracket_start+1:bracket_end]
            remaining = line[bracket_end+1:].lstrip(',')
            
            # Parse remaining fields
            remaining_parts = remaining.split(',')
            if len(remaining_parts) < 5:
                print(f"Warning: Not enough fields in line: {line[:50]}...")
                continue
                
            startframe, youtubeID, timing, weather, egoinvolve = remaining_parts[:5]
            
            # Parse binary labels
            binlabels = [x.strip() for x in binlabels_str.split(",")]
            
            # Generate prompts
            crash_prompt = generate_crash_prompt(timing, weather, egoinvolve, binlabels)
            nearcrash_prompt = generate_nearcrash_prompt(timing, weather, egoinvolve, binlabels)
            safe_prompt = generate_safe_prompt(timing, weather, egoinvolve)
            
            writer.writerow([vidname, crash_prompt, nearcrash_prompt, safe_prompt])
            
            processed += 1
            if processed <= 5:  # Show first 5 examples
                print(f"Video {vidname}:")
                print(f"  Crash: {crash_prompt}")
                print(f"  Near-crash: {nearcrash_prompt}")
                print(f"  Safe: {safe_prompt}")
                print()
            
            if processed % 100 == 0:
                print(f"Processed {processed} videos...")
        
        print(f"✅ Generated prompts for {processed} videos in {OUTPUT_PATH}")

if __name__ == "__main__":
    main()