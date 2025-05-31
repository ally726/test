from app import create_app
import os
import argparse

app = create_app()

if __name__ == "__main__":
    # 也可以從環境變數讀取
    port = 5002
    host = '127.0.0.1'  # 移除多餘的反引號
    debug = True

    print(f"🚀 Starting AI Image Generator API")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🛠️  Debug mode: {'ON' if debug else 'OFF'}")
    print(f"📚 API endpoint: http://{host}:{port}/api/dalle/generate")
    print("\n" + "="*50)
    
    app.run(host=host, port=port, debug=debug)