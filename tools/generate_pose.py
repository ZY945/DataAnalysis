import cv2
import mediapipe as mp
import numpy as np
import os
import logging

# 设置日志级别为 ERROR，只显示错误信息
logging.getLogger("mediapipe").setLevel(logging.ERROR)

class PoseGenerator:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose
        
    def process_video(self, video_path, output_path='output_pose.mp4', progress_callback=None):
        print(f"开始处理视频: {video_path}")  # 调试日志
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"输出路径: {output_path}")  # 调试日志
        
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"无法打开视频: {video_path}")
        
        try:
            # 获取视频属性
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"视频信息: {frame_width}x{frame_height}, {fps}fps, 总帧数: {total_frames}")  # 调试日志
            
            # 尝试不同的编码器
            encoders = [
                ('avc1', '.mp4'),  # H.264
                ('mp4v', '.mp4'),  # MPEG-4
                ('XVID', '.avi'),  # XVID
                ('MJPG', '.avi')   # Motion JPEG
            ]
            
            out = None
            for codec, ext in encoders:
                try:
                    if ext != os.path.splitext(output_path)[1]:
                        continue
                        
                    fourcc = cv2.VideoWriter_fourcc(*codec)
                    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
                    
                    if out.isOpened():
                        print(f"使用编码器: {codec}")  # 调试日志
                        break
                except Exception as e:
                    print(f"编码器 {codec} 失败: {str(e)}")  # 调试日志
                    if out:
                        out.release()
                        out = None
            
            if not out or not out.isOpened():
                raise Exception("无法找到可用的视频编码器")
            
            frame_count = 0
            
            # 初始化姿势检测器
            with self.mp_pose.Pose(
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            ) as pose:
                while cap.isOpened():
                    success, image = cap.read()
                    if not success:
                        break

                    # 处理图像
                    image.flags.writeable = False
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    results = pose.process(image)

                    # 创建白色背景
                    white_image = np.ones((frame_height, frame_width, 3), dtype=np.uint8) * 255

                    # 在白色背景上绘制骨架
                    if results.pose_landmarks:
                        self.mp_drawing.draw_landmarks(
                            white_image,
                            results.pose_landmarks,
                            self.mp_pose.POSE_CONNECTIONS,
                            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                        )

                    # 写入帧
                    frame_count += 1
                    out.write(cv2.flip(white_image, 1))
                    
                    # if frame_count % 10 == 0:  # 每10帧打印一次进度
                    #     print(f"处理帧数: {frame_count}/{total_frames}")  # 调试日志

                    # 更新进度
                    if progress_callback:
                        progress_callback(frame_count, total_frames)

        except Exception as e:
            print(f"处理视频时出错: {str(e)}")  # 调试日志
            raise e
        
        finally:
            # 释放资源
            cap.release()
            if out:
                out.release()
                print(f"视频处理完成，已保存到: {output_path}")  # 调试日志
                
            # 验证文件是否生成
            if os.path.exists(output_path):
                print(f"输出文件存在，大小: {os.path.getsize(output_path)} 字节")  # 调试日志
            else:
                print(f"警告：输出文件未生成: {output_path}")  # 调试日志

# def main():
#     generator = PoseGenerator()
    
#     file_name = "1.mp4"
#     # 视频文件路径
#     video_path = f"视频骨架生成/输入文件夹/{file_name}"
#     output_dir = "视频骨架生成/输出文件夹"
    
#     # 如果视频路径为空或文件不存在，让用户输入
#     if not video_path or not os.path.exists(video_path):
#         video_path = input("请输入视频文件路径: ")
#         if not os.path.exists(video_path):
#             print("视频文件不存在！")
#             return
    
#     # 设置输出视频路径
#     if not output_dir:
#         output_dir = os.path.dirname(os.path.abspath(__file__))

#     output_name = f"{file_name.split('.')[0]}_骨架视频.mp4"
#     output_path = os.path.join(output_dir, output_name)
    
#     # 处理视频
#     generator.process_video(video_path, output_path)

# if __name__ == "__main__":
#     main() 