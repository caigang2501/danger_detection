from moviepy.editor import VideoFileClip, concatenate_videoclips

video1_path = 'data/videos/test.mp4'
video2_path = 'data/videos/fall.mp4'
video1 = VideoFileClip(video1_path)
video2 = VideoFileClip(video2_path)

final_video = concatenate_videoclips([video1, video2])

final_video_path = 'data/videos/test1.mp4'
final_video.write_videofile(final_video_path, codec='libx264', audio_codec='aac')
video1.close()
video2.close()
final_video.close()
