"""
Prometheus metrics service for Smart Dev Dashboard
"""
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
from typing import Dict, Any
from app.core.logger import logger

class MetricsService:
    """Service for collecting and exposing Prometheus metrics"""
    
    def __init__(self):
        # Create a custom registry
        self.registry = CollectorRegistry()
        
        # API Metrics
        self.request_count = Counter(
            'smart_dashboard_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'smart_dashboard_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Log Analysis Metrics
        self.log_uploads_total = Counter(
            'smart_dashboard_log_uploads_total',
            'Total number of log file uploads',
            ['filename', 'status'],
            registry=self.registry
        )
        
        self.log_analysis_duration = Histogram(
            'smart_dashboard_log_analysis_duration_seconds',
            'Log analysis duration in seconds',
            ['filename'],
            registry=self.registry
        )
        
        # Vector Search Metrics
        self.vector_search_total = Counter(
            'smart_dashboard_vector_searches_total',
            'Total number of vector searches',
            ['query_type', 'results_found'],
            registry=self.registry
        )
        
        self.vector_search_duration = Histogram(
            'smart_dashboard_vector_search_duration_seconds',
            'Vector search duration in seconds',
            registry=self.registry
        )
        
        # Incident Metrics
        self.incidents_total = Gauge(
            'smart_dashboard_incidents_total',
            'Total number of incidents in vector database',
            ['severity', 'category'],
            registry=self.registry
        )
        
        self.incident_similarity_scores = Histogram(
            'smart_dashboard_incident_similarity_scores',
            'Distribution of similarity scores',
            ['category'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        # System Metrics
        self.embedding_model_load_duration = Histogram(
            'smart_dashboard_embedding_model_load_duration_seconds',
            'Time to load embedding model',
            registry=self.registry
        )
        
        self.faiss_index_size = Gauge(
            'smart_dashboard_faiss_index_size',
            'Number of vectors in FAISS index',
            registry=self.registry
        )
        
        # Error Metrics
        self.errors_total = Counter(
            'smart_dashboard_errors_total',
            'Total number of errors',
            ['error_type', 'service'],
            registry=self.registry
        )
        
        logger.info("Metrics service initialized")
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record API request metrics"""
        try:
            self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
            self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        except Exception as e:
            logger.error(f"Error recording request metrics: {str(e)}")
    
    def record_log_upload(self, filename: str, status: str, duration: float = None):
        """Record log upload metrics"""
        try:
            self.log_uploads_total.labels(filename=filename, status=status).inc()
            if duration:
                self.log_analysis_duration.labels(filename=filename).observe(duration)
        except Exception as e:
            logger.error(f"Error recording log upload metrics: {str(e)}")
    
    def record_vector_search(self, query_type: str, results_found: int, duration: float, similarity_scores: list = None):
        """Record vector search metrics"""
        try:
            self.vector_search_total.labels(
                query_type=query_type, 
                results_found=str(results_found)
            ).inc()
            self.vector_search_duration.observe(duration)
            
            # Record similarity score distribution
            if similarity_scores:
                for score in similarity_scores:
                    self.incident_similarity_scores.labels(category='all').observe(score)
        except Exception as e:
            logger.error(f"Error recording vector search metrics: {str(e)}")
    
    def update_incident_metrics(self, incidents_data: Dict[str, Any]):
        """Update incident count metrics"""
        try:
            # Reset all incident gauges
            for severity in ['low', 'medium', 'high', 'critical']:
                for category in ['database', 'memory', 'network', 'storage', 'security', 'general']:
                    self.incidents_total.labels(severity=severity, category=category).set(0)
            
            # Set current values
            severities = incidents_data.get('severities', {})
            categories = incidents_data.get('categories', {})
            
            # This is a simplified approach - in real implementation you'd need more detailed tracking
            total_incidents = incidents_data.get('total_incidents', 0)
            if total_incidents > 0:
                self.incidents_total.labels(severity='general', category='general').set(total_incidents)
                
        except Exception as e:
            logger.error(f"Error updating incident metrics: {str(e)}")
    
    def record_embedding_model_load(self, duration: float):
        """Record embedding model load time"""
        try:
            self.embedding_model_load_duration.observe(duration)
        except Exception as e:
            logger.error(f"Error recording embedding model load metrics: {str(e)}")
    
    def update_faiss_index_size(self, size: int):
        """Update FAISS index size metric"""
        try:
            self.faiss_index_size.set(size)
        except Exception as e:
            logger.error(f"Error updating FAISS index size metric: {str(e)}")
    
    def record_error(self, error_type: str, service: str):
        """Record error metrics"""
        try:
            self.errors_total.labels(error_type=error_type, service=service).inc()
        except Exception as e:
            logger.error(f"Error recording error metrics: {str(e)}")
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics as string"""
        try:
            return generate_latest(self.registry)
        except Exception as e:
            logger.error(f"Error generating metrics: {str(e)}")
            return ""

# Global metrics service instance
metrics_service = MetricsService() 