class QualityCheckModel:
    @staticmethod
    def to_dict(quality_check_id, order_id, inspector_id, inspector_name,
                inspection_date, defect_type="None", defect_quantity=0,
                result="Pass", remarks=""):
        return {
            "qualityCheckId": quality_check_id,
            "orderId": order_id,
            "inspectorId": inspector_id,
            "inspectorName": inspector_name,
            "inspectionDate": inspection_date,
            "defectType": defect_type,
            "defectQuantity": int(defect_quantity),
            "result": result,
            "remarks": remarks or ""
        }
