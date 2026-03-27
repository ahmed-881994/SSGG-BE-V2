from app.core.metrics_middleware import metrics


class MetricsService:
    
    def get_application_metrics(self):
        return metrics()
    
    