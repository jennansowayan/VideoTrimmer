from moviepy.video.io.VideoFileClip import VideoFileClip
import os

def trim_and_save_clips(video_path, clip_timestamps):
    video = VideoFileClip(video_path)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = 'clips'
    os.makedirs(output_dir, exist_ok=True)

    for i in range(len(clip_timestamps) - 1):
        start_time = clip_timestamps[i]
        end_time = clip_timestamps[i + 1]

        output_path = os.path.join(output_dir, f"{base_name}_clip_{i+1}.mp4")
        clip = video.subclip(start_time, end_time)
        clip.write_videofile(output_path, codec="libx264")

    # Save the last clip
    start_time = clip_timestamps[-1]
    output_path = os.path.join(output_dir, f"{base_name}_clip_{len(clip_timestamps)}.mp4")
    clip = video.subclip(start_time)
    clip.write_videofile(output_path, codec="libx264")
