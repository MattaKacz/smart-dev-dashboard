"""
Vector search API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.vector_singleton import vector_service
from app.core.logger import logger

router = APIRouter()

@router.get("/vector/search")
async def search_similar_incidents(
    query: str = Query(..., description="Log content to search for"),
    top_k: int = Query(5, description="Number of similar incidents to return"),
    similarity_threshold: float = Query(0.7, description="Minimum similarity score (0-1)")
):
    """Search for similar incidents"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Searching for similar incidents with query: {query[:100]}...")
        
        results = vector_service.search_similar_incidents(
            query_log=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        return {
            "query": query,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "results": results,
            "total_found": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching similar incidents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/vector/statistics")
async def get_vector_statistics():
    """Get statistics about the vector database"""
    try:
        stats = vector_service.get_incident_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting vector statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.post("/vector/add")
async def add_incident_to_vector_db(
    log_content: str,
    analysis: str,
    source_file: str,
    severity: str = "medium",
    category: str = "general"
):
    """Manually add an incident to the vector database"""
    try:
        if not log_content.strip():
            raise HTTPException(status_code=400, detail="Log content cannot be empty")
        
        logger.info(f"Manually adding incident to vector database from {source_file}")
        
        incident_id = vector_service.add_incident(
            log_content=log_content,
            analysis=analysis,
            source_file=source_file,
            severity=severity,
            category=category
        )
        
        return {
            "incident_id": incident_id,
            "message": "Incident added to vector database successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding incident to vector database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add incident: {str(e)}")

@router.delete("/vector/{incident_id}")
async def delete_incident(incident_id: str):
    """Delete an incident from the vector database"""
    try:
        success = vector_service.delete_incident(incident_id)
        if not success:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        return {"message": "Incident deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting incident {incident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete incident: {str(e)}") 