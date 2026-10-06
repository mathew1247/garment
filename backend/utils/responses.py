from flask import jsonify

def success_response(data=None, message="Operation successful", status_code=200):
    """
    Generate a standardized JSON success response.
    """
    response_payload = {
        "success": True,
        "message": message
    }
    if data is not None:
        response_payload["data"] = data
        
    return jsonify(response_payload), status_code


def list_response(data=None, count=None, message="Data retrieved successfully", status_code=200):
    """
    Generate a standardized JSON response for collections / lists.
    """
    if data is None:
        data = []
    
    response_payload = {
        "success": True,
        "message": message,
        "data": data,
        "count": len(data) if count is None else count
    }
    return jsonify(response_payload), status_code


def error_response(message="An error occurred", error_code="ERROR", status_code=400, details=None):
    """
    Generate a standardized JSON error response.
    """
    response_payload = {
        "success": False,
        "message": message,
        "error": error_code
    }
    if details:
        response_payload["details"] = details
        
    return jsonify(response_payload), status_code
