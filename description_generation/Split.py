import re
import os

def split_video_descriptions(input_text, output_directory="video_descriptions"):
    """
    Split video descriptions into separate files.
    
    Args:
        input_text (str): The full text containing all video descriptions
        output_directory (str): Directory to save the individual video files
    """
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Regular expression to match video sections
    # Matches "Video" followed by numbers, then captures everything until the next "Video" or end of string
    video_pattern = r'(Video\s+(\d+).*?)(?=Video\s+\d+|$)'
    
    # Find all video sections
    matches = re.findall(video_pattern, input_text, re.DOTALL)
    
    if not matches:
        print("No video sections found. Please check the input format.")
        return
    
    # Process each video section
    for match in matches:
        full_content = match[0].strip()  # Full content of the video section
        video_number = match[1]          # Video number
        
        # Create filename
        filename = f"Video{video_number}.txt"
        filepath = os.path.join(output_directory, filename)
        
        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(full_content)
            print(f"Successfully created: {filename}")
        except Exception as e:
            print(f"Error creating {filename}: {e}")
    
    print(f"\nProcessing complete! {len(matches)} files created in '{output_directory}' directory.")

def main():
    # Read from the video.txt file (use full path if needed)
    input_filename = r"E:\fifth_semester\Pipeline_Crash_Scene\diffusion-pipe\datasets\videos\video.txt"
    
    try:
        print(f"Reading from '{input_filename}'...")
        with open(input_filename, 'r', encoding='utf-8') as file:
            input_text = file.read()
        
        print(f"File read successfully. Processing video descriptions...")
        split_video_descriptions(input_text)
        
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found in the current directory.")
        print("Please make sure 'video.txt' exists in the same folder as this script.")
    except Exception as e:
        print(f"Error reading file: {e}")

def read_from_file(filename):
    """
    Alternative function to read input from a file instead of hardcoded text.
    
    Args:
        filename (str): Path to the input file containing all video descriptions
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            input_text = file.read()
        split_video_descriptions(input_text)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    # Read from video-description.txt file
    main()