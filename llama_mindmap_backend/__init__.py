"""Flask application factory with device detection and responsive templates."""

import os
import logging
import re
from flask import Flask, render_template, request, jsonify
from llama_mindmap_backend.config import get_config
from llama_mindmap_backend.extensions import db, jwt, migrate
from flasgger import Swagger


def create_app(config_name: str = None) -> Flask:
    """
    Create and configure Flask application with device detection.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    setup_logging()
    
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    app.config.from_object(get_config()())
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register main routes with device detection
    register_main_routes(app)
    
    # Setup Swagger
    setup_swagger(app)
    
    return app


def detect_device(user_agent: str) -> str:
    """
    Detect device type from User-Agent string.
    
    Args:
        user_agent: HTTP User-Agent header
        
    Returns:
        Device type: 'mobile', 'tablet', or 'desktop'
    """
    user_agent = user_agent.lower()
    
    # Mobile device patterns
    mobile_patterns = [
        r'mobile', r'android', r'iphone', r'ipod',
        r'blackberry', r'windows phone', r'opera mini',
        r'palm', r'symbian', r'nokia', r'samsung'
    ]
    
    # Tablet patterns
    tablet_patterns = [
        r'ipad', r'tablet', r'kindle', r'silk',
        r'playbook', r'nexus (?:7|10)',
        r'galaxy tab', r'xoom', r'sch-i800'
    ]
    
    # Check for tablet first (more specific)
    for pattern in tablet_patterns:
        if re.search(pattern, user_agent):
            return 'tablet'
    
    # Then check for mobile
    for pattern in mobile_patterns:
        if re.search(pattern, user_agent):
            return 'mobile'
    
    # Default to desktop
    return 'desktop'


def get_template_for_device(device_type: str) -> str:
    """
    Get appropriate template based on device type.
    
    Args:
        device_type: Device type from detect_device()
        
    Returns:
        Template filename
    """
    template_map = {
        'mobile': 'index_mobile.html',
        'tablet': 'index_tablet.html',  # Optional: separate tablet template
        'desktop': 'index.html'
    }
    
    return template_map.get(device_type, 'index.html')


def setup_logging() -> None:
    """Configure application logging."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""
    from .routes.auth import auth_bp
    from .routes.mindmap import mindmap_bp
    from .routes.admin import admin_bp
    from .routes.web_api import web_api_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(mindmap_bp, url_prefix='/api/mindmap')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(web_api_bp, url_prefix='/api/web')


def register_main_routes(app: Flask) -> None:
    """Register main application routes with device detection."""
    
    @app.route("/")
    def index():
        """Serve device-appropriate HTML page."""
        try:
            # Get User-Agent header
            user_agent = request.headers.get('User-Agent', '')
            
            # Detect device type
            device_type = detect_device(user_agent)
            
            # Get appropriate template
            template_name = get_template_for_device(device_type)
            
            # Log device detection
            app.logger.info(f"Device detected: {device_type} -> {template_name}")
            
            # Try to render the device-specific template
            try:
                return render_template(template_name, device_type=device_type)
            except Exception as template_error:
                app.logger.warning(f"Template {template_name} not found: {template_error}")
                
                # Fallback to default template
                if template_name != 'index.html':
                    app.logger.info("Falling back to index.html")
                    return render_template('index.html', device_type=device_type)
                else:
                    raise template_error
                    
        except Exception as e:
            app.logger.error(f"Error serving template: {e}")
            return create_fallback_response(device_type if 'device_type' in locals() else 'unknown'), 200
    
    @app.route("/force/<device_type>")
    def force_device(device_type: str):
        """Force specific device template for testing."""
        if device_type not in ['mobile', 'tablet', 'desktop']:
            return jsonify({'error': 'Invalid device type'}), 400
        
        try:
            template_name = get_template_for_device(device_type)
            app.logger.info(f"Forced device: {device_type} -> {template_name}")
            return render_template(template_name, device_type=device_type)
        except Exception as e:
            app.logger.error(f"Error forcing device template: {e}")
            return render_template('index.html', device_type=device_type)
    
    @app.route('/device-info')
    def device_info():
        """Get device detection information (for debugging)."""
        user_agent = request.headers.get('User-Agent', '')
        device_type = detect_device(user_agent)
        template_name = get_template_for_device(device_type)
        
        return jsonify({
            'user_agent': user_agent,
            'device_type': device_type,
            'template': template_name,
            'available_templates': get_available_templates()
        })
    
    @app.route('/static/<path:filename>')
    def serve_static(filename: str):
        """Serve static files (CSS, JS, images)."""
        try:
            return app.send_static_file(filename)
        except Exception as e:
            app.logger.error(f"Static file not found: {filename} - {e}")
            return jsonify({'error': 'File not found'}), 404
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Page not found'}), 404


def get_available_templates() -> list:
    """Get list of available template files."""
    try:
        import os
        template_dir = 'templates'
        if os.path.exists(template_dir):
            return [f for f in os.listdir(template_dir) if f.endswith('.html')]
        return []
    except Exception:
        return []


def create_fallback_response(device_type: str) -> str:
    """Create minimal HTML response when template fails."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LLaMA MindMap - {device_type.title()}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            .status {{ padding: 15px; margin: 15px 0; border-radius: 5px; }}
            .success {{ background: #d4edda; color: #155724; }}
            .error {{ background: #f8d7da; color: #721c24; }}
            .info {{ background: #e7f3ff; color: #0066cc; }}
            .btn {{ padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }}
            @media (max-width: 768px) {{
                .container {{ margin: 10px; padding: 15px; }}
                .btn {{ width: 100%; margin: 5px 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LLaMA MindMap</h1>
            <div class="status success">Flask Server Running Successfully</div>
            <div class="status info">Device Detected: {device_type.title()}</div>
            <div class="status error">Template Error: Using fallback HTML</div>
            
            <p>API endpoints are working:</p>
            <button class="btn" onclick="fetch('/api/web/test').then(r=>r.json()).then(d=>alert(JSON.stringify(d)))">Test API</button>
            <button class="btn" onclick="window.open('/docs/', '_blank')">API Docs</button>
            <button class="btn" onclick="window.location.href='/device-info'">Device Info</button>
            
            <h3>Expected Templates:</h3>
            <ul>
                <li>templates/index.html (desktop)</li>
                <li>templates/index_mobile.html (mobile)</li>
                <li>templates/index_tablet.html (tablet - optional)</li>
            </ul>
            
            <h3>Force Device Type (for testing):</h3>
            <button class="btn" onclick="window.location.href='/force/desktop'">Desktop View</button>
            <button class="btn" onclick="window.location.href='/force/mobile'">Mobile View</button>
            <button class="btn" onclick="window.location.href='/force/tablet'">Tablet View</button>
        </div>
    </body>
    </html>
    """


def setup_swagger(app: Flask) -> None:
    """Configure Swagger API documentation."""
    swagger_config = {
        "headers": [],
        "specs": [{
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "MindMap API",
            "description": "AI-powered mindmap creation using LLaMA",
            "version": "1.0.0"
        }
    }

    Swagger(app, config=swagger_config, template=swagger_template)