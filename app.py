from flask import Flask, render_template, request, jsonify, send_file, Response, url_for
from flask_socketio import SocketIO, emit
import os
from tools.generate_pose import PoseGenerator
from werkzeug.utils import secure_filename
from datetime import datetime
import json
from threading import Thread
from flask_cors import CORS
from tools.video_to_audio import convert_videos_to_audio
from tools.stock_query import StockQuery
from tools.steam_query import SteamQuery
from tools.etf_query import ETFQuery
from tools.fund_query import FundQuery

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app, supports_credentials=True, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:8000",  # Fresh 开发服务器
            "http://localhost:5000"   # Flask 服务器
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 设置文件上传目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, 'files', 'input')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'files', 'output')

# 创建 PoseGenerator 实例
pose_generator = PoseGenerator()

# 创建股票查询实例
stock_query = StockQuery()

# 创建 SteamQuery 实例
steam_query = SteamQuery()

# 创建 ETFQuery 实例
etf_query = ETFQuery()

# 创建 FundQuery 实例
fund_query = FundQuery()

# 示例数据
todos = []

# 添加一个全局变量来存储处理进度
processing_progress = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate')
def translate():
    return "翻译字幕功能开发中..."

@app.route('/lyrics')
def lyrics():
    return "分离歌词功能开发中..."

@app.route('/skeleton')
def skeleton():
    return render_template('skeleton.html')

@app.route('/extract')
def extract():
    return render_template('extract.html')

@app.route('/convert')
def convert():
    return "格式转换功能开发中..."

@app.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify(todos)

@app.route('/api/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    if 'text' in data:
        todo = {
            'id': len(todos) + 1,
            'text': data['text'],
            'completed': False
        }
        todos.append(todo)
        return jsonify(todo), 201
    return jsonify({'error': '无效的数据'}), 400

@app.route('/upload-video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov')):
        return jsonify({'error': '不支持的文件格式'}), 400

    try:
        # 处理文件名
        original_name, original_ext = os.path.splitext(file.filename)
        if not original_ext:  # 如果没有扩展名，使用默认扩展名
            original_ext = '.mp4'
            
        safe_name = secure_filename(original_name)
        if not safe_name:  # 如果文件名为空，使用默认名称
            safe_name = 'video'
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        input_filename = f"{timestamp}_{safe_name}{original_ext}"
        
        # 确保输入目录存在
        os.makedirs(INPUT_FOLDER, exist_ok=True)
        
        # 保存上传的文件
        input_path = os.path.join(INPUT_FOLDER, input_filename)
        
        print(f"原始文件名: {file.filename}")  # 调试日志
        print(f"处理后文件名: {input_filename}")  # 调试日志
        print(f"保存路径: {input_path}")  # 调试日志
        
        file.save(input_path)
        
        if not os.path.exists(input_path):
            raise Exception("文件保存失败")
            
        return jsonify({
            'message': '上传成功',
            'input_filename': input_filename
        })
        
    except Exception as e:
        print(f"上传失败: {str(e)}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

def process_video_task(input_path, output_path, input_filename):
    try:
        def progress_callback(current_frame, total_frames):
            # 每处理 1% 的帧数就发送一次进度
            progress_step = max(1, total_frames // 100)
            if current_frame % progress_step == 0 or current_frame == total_frames:
                progress = min(100, int((current_frame / total_frames) * 100))
                socketio.emit('progress_update', {
                    'filename': input_filename,
                    'current': current_frame,
                    'total': total_frames,
                    'progress': progress,
                    'status': 'processing'
                })

        # 处理视频
        pose_generator.process_video(input_path, output_path, progress_callback)
        
        # 发送完成消息
        socketio.emit('progress_update', {
            'filename': input_filename,
            'current': 100,
            'total': 100,
            'progress': 100,
            'status': 'completed',
            'should_disconnect': True  # 告诉客户端断开连接
        })
        
    except Exception as e:
        print(f"处理失败: {str(e)}")
        socketio.emit('progress_update', {
            'filename': input_filename,
            'error': str(e),
            'status': 'error',
            'should_disconnect': True  # 错误时也断开连接
        })

@app.route('/convert-video', methods=['POST'])
def convert_video():
    try:
        data = request.get_json()
        input_filename = data.get('input_filename')
        if not input_filename:
            return jsonify({'error': '未指定输入文件'}), 400

        input_path = os.path.join(INPUT_FOLDER, input_filename)
        if not os.path.exists(input_path):
            return jsonify({'error': '输入文件不存在'}), 404

        # 生成输出文件名
        output_filename = f"skeleton_{input_filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        # 初始化进度
        processing_progress[input_filename] = {
            'current': 0,
            'total': 0,
            'status': 'processing'
        }

        # 在新线程中处理视频
        thread = Thread(target=process_video_task, 
                       args=(input_path, output_path, input_filename))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': '开始处理',
            'output_filename': output_filename
        })
        
    except Exception as e:
        print(f"处理失败: {str(e)}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

@app.route('/progress/<filename>')
def get_progress(filename):
    if filename not in processing_progress:
        return jsonify({'error': '未找到进度信息'}), 404
    return jsonify(processing_progress[filename])

@app.route('/download-video/<filename>')
def download_video(filename):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/upload-audio-video', methods=['POST'])
def upload_audio_video():
    if 'video' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not file.filename.lower().endswith('.mp4'):
        return jsonify({'error': '请上传MP4格式的视频'}), 400

    try:
        # 处理文件名
        original_name, _ = os.path.splitext(file.filename)
        safe_name = secure_filename(original_name)
        if not safe_name:
            safe_name = 'video'
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        input_filename = f"{timestamp}_{safe_name}.mp4"
        output_filename = f"{timestamp}_{safe_name}.mp3"
        
        # 保存上传的文件
        input_path = os.path.join(INPUT_FOLDER, input_filename)
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        file.save(input_path)

        def progress_callback(progress):
            socketio.emit('audio_progress', {
                'filename': input_filename,
                'progress': progress,
                'status': 'processing'
            })

        # 在新线程中处理音频转换
        def process_task():
            try:
                convert_videos_to_audio(input_path, output_path, progress_callback)
                socketio.emit('audio_progress', {
                    'filename': input_filename,
                    'progress': 100,
                    'status': 'completed',
                    'output_filename': output_filename
                })
            except Exception as e:
                socketio.emit('audio_progress', {
                    'filename': input_filename,
                    'error': str(e),
                    'status': 'error'
                })

        thread = Thread(target=process_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': '开始处理',
            'input_filename': input_filename
        })
        
    except Exception as e:
        print(f"转换失败: {str(e)}")
        return jsonify({'error': f'转换失败: {str(e)}'}), 500

@app.route('/download-audio/<filename>')
def download_audio(filename):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

# 添加清理文件的路由（可选）
@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        # 清理输入文件夹
        for file in os.listdir(INPUT_FOLDER):
            file_path = os.path.join(INPUT_FOLDER, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # 清理输出文件夹
        for file in os.listdir(OUTPUT_FOLDER):
            file_path = os.path.join(OUTPUT_FOLDER, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                
        return jsonify({'message': '清理完成'})
    except Exception as e:
        return jsonify({'error': f'清理失败: {str(e)}'}), 500

# 在应用启动时确保目录存在
def ensure_directories():
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"输入目录: {INPUT_FOLDER}")  # 调试日志
    print(f"输出目录: {OUTPUT_FOLDER}")  # 调试日志

# 在应用初始化时调用
ensure_directories()

@app.route('/stock')
def stock():
    return render_template('stock.html')

@app.route('/api/stock/query', methods=['POST'])
def query_stock():
    try:
        data = request.get_json()
        stock_codes = data.get('stock_codes', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not stock_codes:
            return jsonify({'error': '请输入股票代码'}), 400
            
        result = stock_query.get_stocks_data(stock_codes, start_date, end_date)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@app.route('/steam')
def steam():
    return render_template('steam.html')

@app.route('/api/steam/query', methods=['POST'])
def query_steam():
    try:
        data = request.get_json()
        item_names = data.get('item_names', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not item_names:
            return jsonify({'error': '请输入饰品名称'}), 400
            
        result = steam_query.get_items_data(item_names, start_date, end_date)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@app.route('/etf')
def etf():
    return render_template('etf.html')

@app.route('/api/etf/query', methods=['POST'])
def query_etf():
    try:
        data = request.get_json()
        etf_codes = data.get('etf_codes', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not etf_codes:
            return jsonify({'error': '请输入ETF代码'}), 400
            
        result = etf_query.get_etfs_data(etf_codes, start_date, end_date)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@app.route('/fund')
def fund():
    return render_template('fund.html')

@app.route('/api/fund/query', methods=['POST'])
def query_fund():
    try:
        data = request.get_json()
        fund_codes = data.get('fund_codes', [])
        
        if not fund_codes:
            return jsonify({'error': '请输入基金代码'}), 400
            
        results = {}
        for fund_code in fund_codes:
            fund_info = fund_query.get_fund_info(fund_code)
            if fund_info:
                results[fund_code] = fund_info
                
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@app.route('/api/fund/list', methods=['GET'])
def get_fund_list():
    try:
        # 从你的数据源获取基金列表
        # 这里是一个示例，你需要根据实际情况修改
        from tools.fund_query import get_available_funds
        
        funds = get_available_funds()
        return jsonify({"funds": funds})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True) 