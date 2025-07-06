"""
FAISS vector search service for finding similar incidents
"""
import json
import pickle
import numpy as np
import faiss
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from app.services.embedding_service import EmbeddingService
from app.services.metrics_service import metrics_service
from app.core.logger import logger

@dataclass
class IncidentRecord:
    """Record of an incident for vector search"""
    id: str
    timestamp: datetime
    log_content: str
    analysis: str
    severity: str
    category: str
    source_file: str
    embedding: Optional[np.ndarray] = None

class VectorSearchService:
    """FAISS-based vector search for incident similarity"""
    
    def __init__(self, storage_dir: str = "vector_db"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.embedding_service = EmbeddingService()
        self.incidents: List[IncidentRecord] = []
        self.index = None
        self.is_index_built = False
        
        # Load existing data
        self._load_existing_data()
    
    def add_incident(self, log_content: str, analysis: str, source_file: str, 
                    severity: str = "medium", category: str = "general") -> str:
        """
        Add a new incident to the vector database
        
        Args:
            log_content: The log content that caused the incident
            analysis: AI analysis of the incident
            source_file: Source log file name
            severity: Incident severity (low, medium, high, critical)
            category: Incident category (database, memory, network, etc.)
            
        Returns:
            Incident ID
        """
        try:
            import uuid
            
            # Generate embedding for log content
            embedding = self.embedding_service.generate_single_embedding(log_content)
            
            # Create incident record
            incident = IncidentRecord(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                log_content=log_content,
                analysis=analysis,
                severity=severity,
                category=category,
                source_file=source_file,
                embedding=embedding
            )
            
            # Add to incidents list
            self.incidents.append(incident)
            
            # Rebuild index
            self._build_index()
            
            # Save to disk
            self._save_data()
            
            logger.info(f"Added incident {incident.id} to vector database")
            return incident.id
            
        except Exception as e:
            logger.error(f"Error adding incident: {str(e)}")
            raise
    
    def search_similar_incidents(self, query_log: str, top_k: int = 5, 
                               similarity_threshold: float = 0.7) -> List[Dict]:
        """
        Search for similar incidents
        
        Args:
            query_log: Log content to search for
            top_k: Number of top similar incidents to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar incidents with similarity scores
        """
        try:
            if not self.incidents:
                logger.warning("No incidents in database")
                return []
            
            # Generate embedding for query
            query_embedding = self.embedding_service.generate_single_embedding(query_log)
            
            # Search using FAISS
            if self.index is not None and self.is_index_built:
                # Use FAISS for fast search
                query_embedding_reshaped = query_embedding.reshape(1, -1).astype('float32')
                distances, indices = self.index.search(query_embedding_reshaped, min(top_k, len(self.incidents)))
                
                results = []
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx < len(self.incidents):
                        incident = self.incidents[idx]
                        # Convert distance to similarity (FAISS returns L2 distance)
                        similarity = 1.0 / (1.0 + distance)
                        
                        if similarity >= similarity_threshold:
                            results.append({
                                'incident_id': incident.id,
                                'similarity_score': float(similarity),
                                'timestamp': incident.timestamp.isoformat(),
                                'log_content': incident.log_content[:200] + "..." if len(incident.log_content) > 200 else incident.log_content,
                                'analysis': incident.analysis,
                                'severity': incident.severity,
                                'category': incident.category,
                                'source_file': incident.source_file
                            })
                
                # Sort by similarity score (descending)
                results.sort(key=lambda x: x['similarity_score'], reverse=True)
                return results[:top_k]
            
            else:
                # Fallback to brute force search
                logger.warning("FAISS index not available, using brute force search")
                return self._brute_force_search(query_embedding, top_k, similarity_threshold)
                
        except Exception as e:
            logger.error(f"Error searching similar incidents: {str(e)}")
            metrics_service.record_error("vector_search", "vector_service")
            return []
    
    def get_incident_statistics(self) -> Dict:
        """Get statistics about stored incidents"""
        try:
            if not self.incidents:
                return {
                    'total_incidents': 0,
                    'categories': {},
                    'severities': {},
                    'index_built': False
                }
            
            categories = {}
            severities = {}
            
            for incident in self.incidents:
                categories[incident.category] = categories.get(incident.category, 0) + 1
                severities[incident.severity] = severities.get(incident.severity, 0) + 1
            
            return {
                'total_incidents': len(self.incidents),
                'categories': categories,
                'severities': severities,
                'index_built': self.is_index_built,
                'embedding_dimension': self.embedding_service.get_embedding_dimension()
            }
            
        except Exception as e:
            logger.error(f"Error getting incident statistics: {str(e)}")
            return {}
    
    def delete_incident(self, incident_id: str) -> bool:
        """Delete an incident from the database"""
        try:
            for i, incident in enumerate(self.incidents):
                if incident.id == incident_id:
                    del self.incidents[i]
                    self._build_index()
                    self._save_data()
                    logger.info(f"Deleted incident {incident_id}")
                    return True
            
            logger.warning(f"Incident {incident_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting incident {incident_id}: {str(e)}")
            return False
    
    def _build_index(self):
        """Build FAISS index from incidents"""
        try:
            if not self.incidents:
                self.index = None
                self.is_index_built = False
                return
            
            # Extract embeddings
            embeddings = []
            valid_incidents = []
            
            for incident in self.incidents:
                if incident.embedding is not None:
                    embeddings.append(incident.embedding)
                    valid_incidents.append(incident)
            
            if not embeddings:
                logger.warning("No valid embeddings found")
                self.index = None
                self.is_index_built = False
                return
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype='float32')
            
            # Create FAISS index
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings_array)
            
            # Update incidents list to only include valid ones
            self.incidents = valid_incidents
            
            self.is_index_built = True
            logger.info(f"Built FAISS index with {len(embeddings)} vectors of dimension {dimension}")
            
            # Update metrics
            metrics_service.update_faiss_index_size(len(embeddings))
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {str(e)}")
            self.index = None
            self.is_index_built = False
    
    def _brute_force_search(self, query_embedding: np.ndarray, top_k: int, 
                           similarity_threshold: float) -> List[Dict]:
        """Fallback brute force search"""
        try:
            results = []
            
            for incident in self.incidents:
                if incident.embedding is not None:
                    similarity = self.embedding_service.compute_similarity(
                        query_embedding, incident.embedding
                    )
                    
                    if similarity >= similarity_threshold:
                        results.append({
                            'incident_id': incident.id,
                            'similarity_score': similarity,
                            'timestamp': incident.timestamp.isoformat(),
                            'log_content': incident.log_content[:200] + "..." if len(incident.log_content) > 200 else incident.log_content,
                            'analysis': incident.analysis,
                            'severity': incident.severity,
                            'category': incident.category,
                            'source_file': incident.source_file
                        })
            
            # Sort by similarity score and return top_k
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in brute force search: {str(e)}")
            return []
    
    def _save_data(self):
        """Save incidents data to disk"""
        try:
            # Save incidents (without embeddings to reduce size)
            incidents_data = []
            for incident in self.incidents:
                incident_dict = asdict(incident)
                incident_dict['embedding'] = None  # Don't save embeddings in JSON
                incidents_data.append(incident_dict)
            
            incidents_file = self.storage_dir / "incidents.json"
            with open(incidents_file, 'w') as f:
                json.dump(incidents_data, f, indent=2, default=str)
            
            # Save embeddings separately
            embeddings_file = self.storage_dir / "embeddings.pkl"
            embeddings = [incident.embedding for incident in self.incidents if incident.embedding is not None]
            with open(embeddings_file, 'wb') as f:
                pickle.dump(embeddings, f)
            
            logger.info(f"Saved {len(self.incidents)} incidents to disk")
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
    
    def _load_existing_data(self):
        """Load existing incidents from disk"""
        try:
            incidents_file = self.storage_dir / "incidents.json"
            embeddings_file = self.storage_dir / "embeddings.pkl"
            
            if incidents_file.exists() and embeddings_file.exists():
                # Load incidents
                with open(incidents_file, 'r') as f:
                    incidents_data = json.load(f)
                
                # Load embeddings
                with open(embeddings_file, 'rb') as f:
                    embeddings = pickle.load(f)
                
                # Reconstruct incidents
                self.incidents = []
                for i, incident_dict in enumerate(incidents_data):
                    incident = IncidentRecord(
                        id=incident_dict['id'],
                        timestamp=datetime.fromisoformat(incident_dict['timestamp']),
                        log_content=incident_dict['log_content'],
                        analysis=incident_dict['analysis'],
                        severity=incident_dict['severity'],
                        category=incident_dict['category'],
                        source_file=incident_dict['source_file'],
                        embedding=embeddings[i] if i < len(embeddings) else None
                    )
                    self.incidents.append(incident)
                
                # Build index
                self._build_index()
                
                logger.info(f"Loaded {len(self.incidents)} incidents from disk")
            else:
                logger.info("No existing data found, starting with empty database")
                
        except Exception as e:
            logger.error(f"Error loading existing data: {str(e)}")
            self.incidents = [] 