#!/usr/bin/env python3
"""Simplified run script with device template verification."""

import os
import sys
from pathlib import Path


def load_env_file() -> None:
    """Load environment variables from .env file."""
    env_path = Path('.env')
    if env_path.exists():
        print("Loading environment variables from .env")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
    else:
        print(".env file not found! Please create one with your configuration.")


def verify_templates() -> None:
    """Verify template files exist and suggest creation."""
    templates = {
        'templates/index.html': 'Desktop template (required)',
        'templates/index_mobile.html': 'Mobile template (recommended)',
        'templates/index_tablet.html': 'Tablet template (optional)'
    }
    
    print("Checking template files:")
    for template_path, description in templates.items():
        if Path(template_path).exists():
            print(f"  ✓ {template_path} - {description}")
        else:
            print(f"  ✗ {template_path} - {description}")
    
    # Suggest copying desktop template for mobile if missing
    if not Path('templates/index_mobile.html').exists() and Path('templates/index.html').exists():
        print("\nSuggestion: Copy desktop template for mobile:")
        print("  cp templates/index.html templates/index_mobile.html")


def verify_static_files() -> None:
    """Verify static files exist."""
    static_files = [
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    print("\nChecking static files:")
    for file_path in static_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (missing)")


def main() -> None:
    """Main function to run the application."""
    load_env_file()
    verify_templates()
    verify_static_files()
    
    try:
        from llama_mindmap_backend import create_app
        
        app = create_app()
        
        host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_RUN_PORT', '5000'))
        debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        
        print(f"\nStarting LLaMA MindMap Application...")
        print(f"Server: http://{host}:{port}")
        print(f"Templates: {app.template_folder}")
        print(f"Static: {app.static_folder}")
        print("\nDevice Detection Features:")
        print(f"  - Desktop: http://{host}:{port}/")
        print(f"  - Force Mobile: http://{host}:{port}/force/mobile")
        print(f"  - Force Tablet: http://{host}:{port}/force/tablet")
        print(f"  - Device Info: http://{host}:{port}/device-info")
        print("="*60)
        
        app.run(debug=debug, host=host, port=port)
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"Error starting application: {e}")


if __name__ == "__main__":
    main()