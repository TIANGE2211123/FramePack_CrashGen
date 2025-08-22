import os
import re
import glob

def extract_summary_from_file(filepath):
    """
    Extract the summary sentence from a single video file.
    
    Args:
        filepath (str): Path to the video description file
    
    Returns:
        tuple: (video_number, summary_text) or (None, None) if not found
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract video number from filename or content
        filename = os.path.basename(filepath)
        video_match = re.search(r'Video(\d+)\.txt', filename)
        if video_match:
            video_number = video_match.group(1)
        else:
            # Try to extract from content
            video_match = re.search(r'Video\s+(\d+)', content)
            video_number = video_match.group(1) if video_match else "Unknown"
        
        # Extract summary using regex
        summary_match = re.search(r'Summary:\s*(.+?)(?:\n|$)', content)
        if summary_match:
            summary_text = summary_match.group(1).strip()
            return video_number, summary_text
        else:
            print(f"Warning: No summary found in {filename}")
            return video_number, None
            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None, None

def extract_all_summaries(input_directory="video_descriptions", output_file="video_summaries.txt"):
    """
    Extract summaries from all Video*.txt files in the specified directory.
    
    Args:
        input_directory (str): Directory containing the video files
        output_file (str): Output file to save all summaries
    """
    
    # Find all Video*.txt files
    pattern = os.path.join(input_directory, "Video*.txt")
    video_files = glob.glob(pattern)
    
    if not video_files:
        print(f"No Video*.txt files found in '{input_directory}' directory.")
        print("Please make sure the video description files exist.")
        return
    
    # Sort files by video number
    video_files.sort(key=lambda x: int(re.search(r'Video(\d+)\.txt', x).group(1)) if re.search(r'Video(\d+)\.txt', x) else 0)
    
    summaries = []
    successful_extractions = 0
    
    print(f"Found {len(video_files)} video files. Extracting summaries...")
    
    for filepath in video_files:
        video_number, summary = extract_summary_from_file(filepath)
        if summary:
            summaries.append(f"Video {video_number}: {summary}")
            successful_extractions += 1
            print(f"✓ Extracted from Video{video_number}.txt")
        else:
            print(f"✗ Failed to extract from {os.path.basename(filepath)}")
    
    # Write summaries to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            for summary in summaries:
                file.write(summary + '\n')
        
        print(f"\nSuccess! Extracted {successful_extractions} summaries.")
        print(f"Summaries saved to: {output_file}")
        
    except Exception as e:
        print(f"Error writing to output file: {e}")

def extract_summaries_to_individual_files(input_directory="video_descriptions", output_directory="summaries"):
    """
    Extract summaries and save each to individual files named image_*.txt.
    
    Args:
        input_directory (str): Directory containing the video files
        output_directory (str): Directory to save individual summary files
    """
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Find all Video*.txt files
    pattern = os.path.join(input_directory, "Video*.txt")
    video_files = glob.glob(pattern)
    
    if not video_files:
        print(f"No Video*.txt files found in '{input_directory}' directory.")
        return
    
    successful_extractions = 0
    
    for filepath in video_files:
        video_number, summary = extract_summary_from_file(filepath)
        if summary:
            # Create individual summary file with image_ prefix
            summary_filename = f"image_{video_number}.txt"
            summary_filepath = os.path.join(output_directory, summary_filename)
            
            try:
                with open(summary_filepath, 'w', encoding='utf-8') as file:
                    file.write(summary)
                successful_extractions += 1
                print(f"✓ Created {summary_filename}")
            except Exception as e:
                print(f"✗ Error creating {summary_filename}: {e}")
    
    print(f"\nExtracted {successful_extractions} individual summary files to '{output_directory}' directory.")

def main():
    """
    Main function with options for different extraction methods.
    """
    print("Video Summary Extractor")
    print("=" * 30)
    
    # Check if video_descriptions directory exists
    if not os.path.exists("video_descriptions"):
        print("Error: 'video_descriptions' directory not found.")
        print("Please run the video splitter script first to create the individual video files.")
        return
    
    print("Choose extraction method:")
    print("1. Extract all summaries to one file (video_summaries.txt)")
    print("2. Extract summaries to individual files (image_*.txt)")
    print("3. Both methods")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        extract_all_summaries()
    elif choice == "2":
        extract_summaries_to_individual_files()
    elif choice == "3":
        extract_all_summaries()
        print("\n" + "="*50)
        extract_summaries_to_individual_files()
    else:
        print("Invalid choice. Running default extraction (all summaries to one file)...")
        extract_all_summaries()

if __name__ == "__main__":
    main()