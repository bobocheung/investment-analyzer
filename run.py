#!/usr/bin/env python3
"""
投資分析系統啟動腳本
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # 獲取項目根目錄
    project_root = Path(__file__).parent.absolute()
    backend_dir = project_root / "backend"
    
    print("🚀 啟動投資分析系統...")
    print(f"📁 項目目錄: {project_root}")
    
    # 檢查依賴
    try:
        import flask
        import yfinance
        import pandas
        import numpy
        print("✅ 依賴檢查通過")
    except ImportError as e:
        print(f"❌ 缺少依賴: {e}")
        print("請運行: pip install Flask Flask-CORS requests pandas numpy yfinance python-dotenv schedule Jinja2")
        return
    
    # 創建必要目錄
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    print(f"📂 數據目錄: {data_dir}")
    
    # 設置環境變量
    os.environ['PYTHONPATH'] = str(project_root)
    
    # 切換到後端目錄
    os.chdir(backend_dir)
    
    # 檢查端口
    import socket
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return True
            except OSError:
                return False
    
    # 尋找可用端口
    ports_to_try = [8080, 8081, 8082, 5001, 5002]
    available_port = None
    
    for port in ports_to_try:
        if is_port_available(port):
            available_port = port
            break
    
    if not available_port:
        print("❌ 無法找到可用端口")
        return
    
    print(f"🌐 使用端口: {available_port}")
    
    # 更新前端API配置
    frontend_script = project_root / "frontend" / "script.js"
    if frontend_script.exists():
        content = frontend_script.read_text(encoding='utf-8')
        # 更新API基礎URL
        new_content = content.replace(
            "const API_BASE = window.location.origin.includes('localhost') ? 'http://localhost:8080' : '';",
            f"const API_BASE = window.location.origin.includes('localhost') ? 'http://localhost:{available_port}' : '';"
        )
        frontend_script.write_text(new_content, encoding='utf-8')
        print("✅ 前端配置已更新")
    
    # 啟動Flask應用
    print(f"🔥 啟動Flask應用在端口 {available_port}...")
    print(f"🌍 訪問地址: http://localhost:{available_port}")
    print("按 Ctrl+C 停止服務")
    print("-" * 50)
    
    try:
        # 直接導入並運行
        sys.path.insert(0, str(backend_dir))
        
        # 修改app.py中的端口
        app_file = backend_dir / "app.py"
        app_content = app_file.read_text(encoding='utf-8')
        new_app_content = app_content.replace(
            "app.run(debug=True, host='0.0.0.0', port=8080)",
            f"app.run(debug=True, host='0.0.0.0', port={available_port})"
        )
        app_file.write_text(new_app_content, encoding='utf-8')
        
        # 啟動應用
        subprocess.run([sys.executable, "app.py"], cwd=backend_dir)
        
    except KeyboardInterrupt:
        print("\n👋 服務已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        print("\n🔧 故障排除:")
        print("1. 檢查Python版本 (需要3.8+)")
        print("2. 安裝依賴: pip install -r requirements.txt")
        print("3. 檢查端口是否被佔用")

if __name__ == "__main__":
    main()