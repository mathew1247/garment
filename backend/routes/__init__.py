from backend.routes.auth_routes import auth_bp
from backend.routes.user_routes import user_bp
from backend.routes.product_routes import product_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.order_routes import order_bp
from backend.routes.production_routes import production_bp
from backend.routes.employee_routes import employee_bp
from backend.routes.assignment_routes import assignment_bp
from backend.routes.inventory_routes import inventory_bp
from backend.routes.quality_routes import quality_bp
from backend.routes.packaging_routes import packaging_bp
from backend.routes.dispatch_routes import dispatch_bp
from backend.routes.notification_routes import notification_bp
from backend.routes.report_routes import report_bp

ALL_BLUEPRINTS = [
    auth_bp,
    user_bp,
    product_bp,
    dashboard_bp,
    order_bp,
    production_bp,
    employee_bp,
    assignment_bp,
    inventory_bp,
    quality_bp,
    packaging_bp,
    dispatch_bp,
    notification_bp,
    report_bp
]
