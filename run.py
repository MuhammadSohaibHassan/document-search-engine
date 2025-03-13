from app import create_app
import os
import pytz
from datetime import datetime

app = create_app()

def get_pakistan_time_str():
    """Get current Pakistan Standard Time as formatted string"""
    # Get UTC time with timezone info
    utc_now = datetime.now(pytz.UTC)
    # Convert to Pakistan time (PKT is UTC+5)
    pk_time = utc_now.astimezone(pytz.timezone('Asia/Karachi'))
    return pk_time.strftime("%b %d, %Y %I:%M:%S %p") + ' (PKT)'

if __name__ == '__main__':
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║            Document Search Engine - Starting                ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    print(f"\n🕒 Server time: {get_pakistan_time_str()}")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"🔍 Search index: {app.config['WHOOSH_INDEX_DIR']}")
    
    # Show allowed file types in a readable format
    allowed_exts = ', '.join(sorted(list(app.config['ALLOWED_EXTENSIONS'])))
    print(f"📄 Supported file types: {allowed_exts}")
    
    # Show server URL with a more prominent display
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║  Server running at: http://127.0.0.1:5000/                  ║")
    print("║  Press CTRL+C to stop the server                           ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    app.run(debug=True) 