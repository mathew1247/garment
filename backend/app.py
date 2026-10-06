import os
import sys
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Ensure backend directory is in python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Resolve frontend directory location
candidate_frontend_dirs = [
    os.path.abspath(os.path.join(current_dir, "..", "frontend")),
    os.path.abspath(os.path.join(current_dir, "frontend")),
    os.path.abspath(os.path.join(os.getcwd(), "frontend")),
    os.path.abspath(os.path.join(os.getcwd(), "..", "frontend")),
]
frontend_dir = next((d for d in candidate_frontend_dirs if os.path.isdir(d)), None)

from backend.config import Config, config_by_name
from backend.routes import ALL_BLUEPRINTS
from backend.utils.responses import error_response, success_response


def create_app(config_name=None):
    """Application factory for Flask REST API."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app_config = config_by_name.get(config_name, Config)
    app.config.from_object(app_config)

    # Configure logging
    log_level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    logger = logging.getLogger("garment_api")

    # Configure CORS
    allowed_origins = app.config.get("CORS_ORIGINS", ["*"])
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # Request logger hook (Sanitizing sensitive data)
    @app.before_request
    def log_request_info():
        # Do not log auth tokens or passwords
        safe_path = request.path
        if not safe_path.startswith("/api/health"):
            logger.info(f"Incoming Request: {request.method} {safe_path} from {request.remote_addr}")

    # Health Check Endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "success": True,
            "message": "Flask server is running",
            "version": "1.0.0"
        }), 200

    # Firestore Connection Test Endpoint
    @app.route("/api/firestore-test", methods=["GET"])
    def firestore_test():
        try:
            from firebase_admin import firestore
            from backend.firebase.firebase_config import db
            doc_ref = db.collection("system").document("firestore_test")
            doc_ref.set({
                "status": "connected",
                "message": "Flask connected to Cloud Firestore",
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            snapshot = doc_ref.get()
            data = snapshot.to_dict() or {}
            # Format timestamp for JSON serialization
            if "timestamp" in data and hasattr(data["timestamp"], "isoformat"):
                data["timestamp"] = data["timestamp"].isoformat()

            return jsonify({
                "success": True,
                "message": "Flask successfully connected and verified with Cloud Firestore",
                "data": data
            }), 200
        except Exception as e:
            logger.error(f"Firestore test connection failed: {e}")
            return error_response(
                message=f"Cloud Firestore connection failed: {str(e)}",
                error_code="FIRESTORE_CONNECTION_ERROR",
                status_code=500
            )

    # API Root overview
    @app.route("/api", methods=["GET"])
    def api_root():
        return success_response(
            data={
                "name": "Garment Production Tracking REST API",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/api/health",
                    "auth": "/api/auth",
                    "users": "/api/users",
                    "dashboard": "/api/dashboard",
                    "orders": "/api/orders",
                    "production": "/api/production",
                    "employees": "/api/employees",
                    "assignments": "/api/assignments",
                    "inventory": "/api/inventory",
                    "qualityChecks": "/api/quality-checks",
                    "packaging": "/api/packaging",
                    "dispatch": "/api/dispatch",
                    "notifications": "/api/notifications",
                    "reports": "/api/reports"
                }
            },
            message="Garment Production Tracking API service active"
        )

    # Root URL Route - Serves frontend login / dashboard if available, or API status
    @app.route("/", methods=["GET"])
    def root():
        if frontend_dir:
            login_file = os.path.join(frontend_dir, "login.html")
            index_file = os.path.join(frontend_dir, "index.html")
            if os.path.isfile(login_file):
                return send_from_directory(frontend_dir, "login.html")
            if os.path.isfile(index_file):
                return send_from_directory(frontend_dir, "index.html")

        return jsonify({
            "success": True,
            "message": "Garment Production Tracking API is running!",
            "status": "online",
            "health_check": "/api/health",
            "api_overview": "/api"
        }), 200

    # Serve frontend assets and pages (CSS, JS, images, HTML)
    @app.route("/<path:path>", methods=["GET"])
    def serve_frontend(path):
        # Allow API routes to be handled by Flask/blueprints or fall through
        if path.startswith("api/") or path == "api":
            return error_response(
                message=f"The requested API endpoint '/{path}' was not found.",
                error_code="NOT_FOUND",
                status_code=404
            )

        if frontend_dir:
            file_path = os.path.join(frontend_dir, path)
            if os.path.isfile(file_path):
                return send_from_directory(frontend_dir, path)

            # Check if matching HTML file exists (e.g., /dashboard -> dashboard.html)
            html_path = os.path.join(frontend_dir, f"{path}.html")
            if os.path.isfile(html_path):
                return send_from_directory(frontend_dir, f"{path}.html")

        return error_response(
            message=f"The requested resource '/{path}' was not found on the server.",
            error_code="NOT_FOUND",
            status_code=404
        )

    # Register all blueprints
    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)

    # Global Error Handlers
    @app.errorhandler(400)
    def handle_bad_request(e):
        return error_response(
            message=str(e.description) if hasattr(e, "description") else "Bad request syntax or invalid parameters",
            error_code="BAD_REQUEST",
            status_code=400
        )

    @app.errorhandler(401)
    def handle_unauthorized(e):
        return error_response(
            message=str(e.description) if hasattr(e, "description") else "Authentication required",
            error_code="UNAUTHORIZED",
            status_code=401
        )

    @app.errorhandler(403)
    def handle_forbidden(e):
        return error_response(
            message=str(e.description) if hasattr(e, "description") else "Access forbidden. Insufficient permissions",
            error_code="FORBIDDEN",
            status_code=403
        )

    @app.errorhandler(404)
    def handle_not_found(e):
        return error_response(
            message=str(e.description) if hasattr(e, "description") else "Resource not found",
            error_code="NOT_FOUND",
            status_code=404
        )

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return error_response(
            message="HTTP method not allowed for this route",
            error_code="METHOD_NOT_ALLOWED",
            status_code=405
        )

    @app.errorhandler(500)
    def handle_internal_server_error(e):
        logger.error(f"Internal Server Error: {str(e)}")
        return error_response(
            message="An unexpected internal server error occurred",
            error_code="INTERNAL_SERVER_ERROR",
            status_code=500
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        if isinstance(e, HTTPException):
            return error_response(
                message=e.description,
                error_code=e.name.upper().replace(" ", "_"),
                status_code=e.code
            )
        logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        return error_response(
            message="An unexpected error occurred while processing the request",
            error_code="SERVER_ERROR",
            status_code=500
        )

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print(f"Starting Garment Production Tracking API on http://localhost:{port}")
    print(f"Health check available at http://localhost:{port}/api/health")
    app.run(host="0.0.0.0", port=port, debug=debug)
