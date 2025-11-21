# Aura Model 1 GLM - Operational Guide

**Property of Nümtema AGENCY**  
**Contact:** numtemalionel@gmail.com  
**Version:** 1.0  
**Date:** 2025-11-21

## Overview

This operational guide provides comprehensive instructions for deploying, running, monitoring, and maintaining the Aura Model 1 GLM system in production environments.

## System Requirements

### Hardware Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 2 GB free space
- Network: Stable internet connection

**Recommended:**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 10+ GB free space
- Network: High-speed connection

### Software Requirements

- Python 3.8+
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Operating System: Linux, macOS, or Windows

## Installation

### 1. Clone or Extract Project

```bash
cd /path/to/installation/directory
# If from repository:
git clone <repository-url>
# If from archive:
unzip Numtema_AGENCY.zip
cd Numtema_AGENCY
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python validate_integration.py
```

Expected output: All checks should pass with "✓" indicators.

## Starting the System

### Quick Start

```bash
chmod +x start_aura.sh
./start_aura.sh
```

The script will:
1. Check Python environment
2. Install/verify dependencies
3. Start the backend server
4. Provide access URL

### Manual Start

```bash
cd backend
python server.py
```

Access the system at: `http://localhost:5000`

### Startup Options

The system supports environment variables for configuration:

```bash
# Custom port
export AURA_PORT=8080

# Debug mode
export AURA_DEBUG=true

# Log level
export AURA_LOG_LEVEL=INFO

./start_aura.sh
```

## System Monitoring

### Health Checks

**Check 1: Server Status**
```bash
curl http://localhost:5000/health
```
Expected: `{"status": "healthy", "timestamp": "..."}`

**Check 2: System Logs**
```bash
tail -f logs/aura_system.log
```

**Check 3: Resource Usage**
```bash
ps aux | grep "python.*server.py"
```

### Performance Metrics

Monitor these key metrics:

1. **Response Time**: Should be < 10 seconds
2. **Memory Usage**: Should remain stable (not continuously growing)
3. **CPU Usage**: Should return to baseline between requests
4. **Error Rate**: Should be < 1% of total requests

### Log Files

Logs are stored in:
- `logs/aura_system.log` - Main system log
- `logs/error.log` - Error-specific log
- `logs/access.log` - HTTP access log

## Common Operations

### Stopping the System

```bash
# Find process ID
ps aux | grep "python.*server.py"

# Kill process
kill <PID>

# Or force kill if necessary
kill -9 <PID>
```

### Restarting the System

```bash
# Stop
pkill -f "python.*server.py"

# Start
./start_aura.sh
```

### Updating the System

```bash
# Backup current version
cp -r Numtema_AGENCY Numtema_AGENCY_backup

# Pull/extract new version
# ... update files ...

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Restart system
./start_aura.sh
```

## Troubleshooting

### Issue: System Won't Start

**Symptoms:** Server fails to start or immediately exits

**Solutions:**
1. Check Python version: `python --version` (must be 3.8+)
2. Verify dependencies: `pip install -r requirements.txt`
3. Check port availability: `lsof -i :5000`
4. Review error logs: `cat logs/error.log`

### Issue: Slow Response Times

**Symptoms:** Requests take > 15 seconds to complete

**Solutions:**
1. Check system resources: `top` or `htop`
2. Restart the system to clear memory
3. Reduce concurrent requests
4. Check network connectivity

### Issue: Memory Leaks

**Symptoms:** Memory usage continuously increases

**Solutions:**
1. Restart the system
2. Check for infinite loops in logs
3. Limit conversation history depth
4. Contact support if persistent

### Issue: Frontend Not Loading

**Symptoms:** Blank page or connection errors

**Solutions:**
1. Verify server is running: `curl http://localhost:5000/health`
2. Check browser console for errors (F12)
3. Clear browser cache
4. Try different browser
5. Check firewall settings

## Maintenance Tasks

### Daily Tasks
- [ ] Check system logs for errors
- [ ] Verify service is running
- [ ] Monitor response times

### Weekly Tasks
- [ ] Review error logs
- [ ] Check disk space usage
- [ ] Verify backup integrity
- [ ] Update dependencies if needed

### Monthly Tasks
- [ ] Performance review and optimization
- [ ] Security updates
- [ ] Documentation updates
- [ ] User feedback analysis

## Backup and Recovery

### Backup Procedure

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup configuration and data
cp -r backend backups/$(date +%Y%m%d)/
cp -r frontend backups/$(date +%Y%m%d)/
cp -r docs backups/$(date +%Y%m%d)/

# Create archive
tar -czf backups/aura_backup_$(date +%Y%m%d).tar.gz \
  backups/$(date +%Y%m%d)/
```

### Recovery Procedure

```bash
# Stop running system
pkill -f "python.*server.py"

# Extract backup
tar -xzf backups/aura_backup_YYYYMMDD.tar.gz -C ./

# Restart system
./start_aura.sh
```

## Security Considerations

### Best Practices

1. **Network Security**
   - Use HTTPS in production
   - Configure firewall rules
   - Restrict access to known IP addresses

2. **Access Control**
   - Implement authentication if needed
   - Use strong passwords
   - Regular security audits

3. **Data Protection**
   - Regular backups
   - Encrypted storage for sensitive data
   - Secure log file handling

### Production Deployment

For production environments:

1. Use reverse proxy (nginx, Apache)
2. Enable SSL/TLS certificates
3. Set up monitoring and alerting
4. Configure automatic restarts
5. Implement rate limiting
6. Use environment-based configuration

## Performance Optimization

### Configuration Tuning

```python
# In backend/server.py, adjust:
MAX_WORKERS = 4  # Number of concurrent handlers
TIMEOUT = 30  # Request timeout in seconds
CACHE_SIZE = 100  # Response cache size
```

### Resource Limits

```bash
# Set resource limits (Linux)
ulimit -n 4096  # Max open files
ulimit -u 2048  # Max processes
```

## Support and Contact

### Getting Help

**Documentation:**
- README.md - Quick start guide
- ARCHITECTURE.md - System design details
- API_REFERENCE.md - API documentation

**Contact:**
- Email: numtemalionel@gmail.com
- System Owner: Nümtema AGENCY

### Reporting Issues

When reporting issues, include:
1. System version
2. Operating system and version
3. Error messages or logs
4. Steps to reproduce
5. Expected vs actual behavior

## Appendix

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| AURA_PORT | 5000 | Server port |
| AURA_DEBUG | false | Debug mode |
| AURA_LOG_LEVEL | INFO | Logging level |
| AURA_MAX_HISTORY | 10 | Conversation history |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| / | GET | Web interface |
| /health | GET | Health check |
| /api/chat | POST | Chat interaction |
| /api/status | GET | System status |

### File Structure