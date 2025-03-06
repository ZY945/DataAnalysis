import os
from moviepy import VideoFileClip
import time
from proglog import ProgressBarLogger

class MyProgressBarLogger(ProgressBarLogger):
    def __init__(self, progress_callback):
        super().__init__()
        self._progress_callback = progress_callback
        
    def bars_callback(self, bar, attr, value, old_value=None):
        """进度条回调"""
        if bar == 'chunk' and attr == 't':
            if self._progress_callback:
                progress = min(100, int(value * 100))
                self._progress_callback(progress)

def convert_videos_to_audio(input_path, output_path, progress_callback=None):
    """转换单个视频文件到音频"""
    try:
        print(f"正在转换: {input_path}")
        
        # 加载视频文件
        video = VideoFileClip(input_path)
        
        # 创建进度记录器
        logger = MyProgressBarLogger(progress_callback)
        
        # 提取音频并保存
        video.audio.write_audiofile(
            output_path,
            logger=logger
        )
        
        # 关闭视频文件
        video.close()
        
        print(f"转换完成: {output_path}")
        return True
        
    except Exception as e:
        print(f"转换失败: {str(e)}")
        raise e

# if __name__ == "__main__":
#     # 设置输入和输出文件夹路径
#     input_folder = "提取音频_输入文件夹"  # 存放MP4文件的文件夹
#     output_folder = "提取音频_输出文件夹"  # 输出MP3文件的文件夹
    
#     convert_videos_to_audio(input_folder, output_folder) 