class DispatchModel:
    @staticmethod
    def to_dict(dispatch_id, order_id, dispatch_date, delivery_information, status="Dispatched", remarks=""):
        return {
            "dispatchId": dispatch_id,
            "orderId": order_id,
            "dispatchDate": dispatch_date,
            "deliveryInformation": delivery_information,
            "status": status,
            "remarks": remarks or ""
        }
