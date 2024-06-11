from moviepy.editor import VideoFileClip, concatenate_videoclips

# 视频文件路径
video1_path = 'data/videos/4.mp4'
video2_path = 'data/videos/3.mp4'

# 读取视频文件
video1 = VideoFileClip(video1_path)
video2 = VideoFileClip(video2_path)

# 拼接视频
final_video = concatenate_videoclips([video1, video2])

# 保存拼接后的视频
final_video_path = 'data/videos/test.mp4'
final_video.write_videofile(final_video_path, codec='libx264', audio_codec='aac')

# 关闭视频文件
video1.close()
video2.close()
final_video.close()
