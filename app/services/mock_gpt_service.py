"""
Mock GPT service for testing without OpenAI API key
"""
import time
from app.core.logger import logger

def analyze_logs(log_text: str) -> str:
    start_time = time.time()
    
    try:
        logger.debug("Using mock GPT service for analysis")
        
        # Simulate API delay
        time.sleep(0.5)
        
        # Mock analysis based on log content
        if "database" in log_text.lower() or "connection" in log_text.lower():
            analysis = """
🔍 **Database Error Analysis:**

**Problem:** Database connection error
**Cause:** Connection timeout after 30 seconds
**Host:** db.example.com:5432

**Solutions:**
1. Check if the database server is running
2. Verify firewall settings
3. Check network configuration
4. Increase connection timeout in configuration

**Recommended steps:**
- Check server status: `systemctl status postgresql`
- Test connection: `telnet db.example.com 5432`
- Check PostgreSQL logs: `/var/log/postgresql/`
"""
        elif "memory" in log_text.lower() or "out of memory" in log_text.lower():
            analysis = """
🔍 **Memory Error Analysis:**

**Problem:** Out of Memory error
**Cause:** Application exceeded available memory

**Solutions:**
1. Increase memory limit for the application
2. Optimize code for memory usage
3. Add garbage collection
4. Check for memory leaks

**Recommended steps:**
- Monitor memory usage: `htop` or `free -h`
- Check JVM configuration (if Java)
- Add memory monitoring
"""
        else:
            analysis = """
🔍 **General Log Analysis:**

**Issues found:** Application error
**Level:** ERROR

**Recommendations:**
1. Check error details in logs
2. Verify application configuration
3. Check dependencies and libraries
4. Add more detailed logging

**Next steps:**
- Analyze complete application logs
- Check system metrics
- Verify environment configuration
"""
        
        duration = time.time() - start_time
        logger.info(f"Mock analysis completed in {duration:.3f}s")
        
        return analysis.strip()
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Mock analysis error after {duration:.3f}s: {str(e)}")
        raise 