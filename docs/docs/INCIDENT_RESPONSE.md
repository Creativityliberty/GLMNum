# Incident Response Guide - Aura Model 1 GLM

## Contact Information
- **Primary Support**: numtemalionel@gmail.com
- **Emergency Escalation**: numtemalionel@gmail.com
- **System Status**: Check `/app/default_project_1646/Numtema_AGENCY/logs/`

## Severity Levels

### CRITICAL (P0)
**Definition**: Complete system outage, no user access
**Response Time**: 5 minutes
**Actions**:
1. Immediately check server status: `ps aux | grep server.py`
2. Check logs: `tail -100 /app/default_project_1646/Numtema_AGENCY/logs/aura.log`
3. Restart server: `cd /app/default_project_1646/Numtema_AGENCY && ./start_aura.sh`
4. If restart fails, check dependencies: `pip list | grep -E "torch|transformers"`
5. Notify all stakeholders
6. Document root cause in incident log

### HIGH (P1)
**Definition**: Major functionality broken, significant user impact
**Response Time**: 15 minutes
**Actions**:
1. Identify affected component (backend/frontend/consciousness system)
2. Check resource utilization: `python backend/monitoring.py` (one-time run)
3. Review recent changes in git history
4. Apply hotfix or rollback if available
5. Monitor for resolution
6. Update status and notify users

### MEDIUM (P2)
**Definition**: Degraded performance, partial functionality affected
**Response Time**: 30 minutes
**Actions**:
1. Investigate performance metrics
2. Check for memory/CPU spikes
3. Review error logs for patterns
4. Prepare fix for next maintenance window
5. Document issue and workaround

### LOW (P3)
**Definition**: Minor issues, minimal user impact
**Response Time**: 60 minutes
**Actions**:
1. Log issue in tracking system
2. Schedule fix for next sprint
3. Monitor for escalation

## Common Issues and Solutions

### Issue: Server Won't Start
**Symptoms**: 
- `start_aura.sh` fails
- Port 8000 not responding

**Diagnosis**:
```bash
cd /app/default_project_1646/Numtema_AGENCY
cat logs/aura.log | tail -50
netstat -tulpn | grep 8000
```

**Solutions**:
1. Kill existing process: `pkill -f server.py`
2. Check port availability: `lsof -i :8000`
3. Verify Python environment: `python --version` (should be 3.8+)
4. Reinstall dependencies: `pip install -r requirements.txt`
5. Restart: `./start_aura.sh`

### Issue: High Memory Usage
**Symptoms**:
- System slow/unresponsive
- Memory usage > 90%

**Diagnosis**:
```bash
python backend/monitoring.py  # Check metrics
ps aux --sort=-%mem | head -10
```

**Solutions**:
1. Restart server to clear memory
2. Check for memory leaks in recent code changes
3. Review model loading strategy in aura_glm.py
4. Consider increasing system RAM if persistent
5. Implement model quantization if needed

### Issue: Slow Response Times
**Symptoms**:
- API calls taking > 5 seconds
- UI freezing

**Diagnosis**:
```bash
# Check CPU usage
top -b -n 1 | head -20

# Check active connections
netstat -an | grep :8000 | wc -l

# Review logs for bottlenecks
grep "WARNING\|ERROR" logs/aura.log | tail -50
```

**Solutions**:
1. Check RRLA pipeline complexity
2. Optimize consciousness system loops
3. Implement caching for repeated queries
4. Scale horizontally if needed
5. Review and optimize ∆∞Ο transformations

### Issue: Consciousness System Not Learning
**Symptoms**:
- No improvement in responses over time
- InnerWorldModel not updating

**Diagnosis**:
```bash
# Check learning logs
cat logs/aura.log | grep "InnerWorldModel\|MetaCognitiveAgent"

# Verify RRLA execution
python validate_integration.py
```

**Solutions**:
1. Verify autonomous learning is enabled in config
2. Check memory storage mechanism
3. Review feedback loop implementation
4. Ensure proper state persistence
5. Restart with clean state if corrupted

### Issue: Frontend Not Loading
**Symptoms**:
- Blank page or connection refused
- UI elements missing

**Diagnosis**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify frontend files
ls -la frontend/
```

**Solutions**:
1. Verify backend is running: `ps aux | grep server.py`
2. Check browser console for errors (F12)
3. Clear browser cache
4. Verify static file serving in server.py
5. Check CORS settings

## Emergency Procedures

### Complete System Failure
1. **STOP**: Don't make changes without assessment
2. **ASSESS**: Check all logs and metrics
3. **BACKUP**: Preserve current state and logs
4. **RESTORE**: Use last known good configuration
5. **VERIFY**: Run full test suite
6. **DOCUMENT**: Record all actions taken

### Data Corruption
1. Immediately stop the system
2. Backup corrupted data to separate location
3. Restore from last verified backup
4. Investigate root cause
5. Implement preventive measures
6. Resume operations with monitoring

### Security Incident
1. Isolate affected systems immediately
2. Preserve evidence (logs, memory dumps)
3. Notify security team and stakeholders
4. Assess scope of breach
5. Apply security patches
6. Conduct post-incident review

## Escalation Path

1. **L1 Support** (First Response)
   - Initial triage
   - Common issue resolution
   - Escalate if unresolved in 30 minutes

2. **L2 Support** (Technical Lead)
   - Complex troubleshooting
   - Code-level investigation
   - Escalate if requires architecture changes

3. **L3 Support** (System Architect)
   - Architecture decisions
   - Major system changes
   - Direct contact: numtemalionel@gmail.com

## Post-Incident Review Template

```markdown
## Incident Report: [YYYY-MM-DD] - [Brief Title]

**Severity**: [P0/P1/P2/P3]
**Duration**: [Start Time] to [End Time]
**Impact**: [Description of user impact]

### Timeline
- [HH:MM] - Incident detected
- [HH:MM] - Response initiated
- [HH:MM] - Root cause identified
- [HH:MM] - Fix applied
- [HH:MM] - Service restored
- [HH:MM] - Monitoring confirmed stable

### Root Cause
[Detailed explanation of what caused the incident]

### Resolution
[Steps taken to resolve the incident]

### Preventive Measures
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

### Lessons Learned
[Key takeaways and improvements for future]
```

## Monitoring and Alerts

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-21T20:50:00Z",
  "checks": {
    "cpu_healthy": true,
    "memory_healthy": true,
    "disk_healthy": true,
    "server_responsive": true
  },
  "metrics": {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "disk_usage_percent": 7.0,
    "active_connections": 3
  },
  "alerts": []
}
```

### Continuous Monitoring
Run monitoring in background:
```bash
cd /app/default_project_1646/Numtema_AGENCY/backend
nohup python monitoring.py > /dev/null 2>&1 &
```

Check monitoring status:
```bash
ps aux | grep monitoring.py
tail -f logs/metrics.jsonl
tail -f logs/alerts.jsonl
```

## Maintenance Windows

### Scheduled Maintenance
- **Frequency**: Monthly, first Sunday 02:00-04:00 UTC
- **Notification**: 72 hours advance notice
- **Activities**: 
  - System updates
  - Security patches
  - Performance optimization
  - Backup verification

### Emergency Maintenance
- **Trigger**: Critical security vulnerability or P0 incident
- **Notification**: As soon as possible
- **Duration**: Until resolved

## Recovery Time Objectives (RTO)

| Severity | Target RTO | Maximum RTO |
|----------|-----------|-------------|
| P0 (Critical) | 15 minutes | 1 hour |
| P1 (High) | 1 hour | 4 hours |
| P2 (Medium) | 4 hours | 24 hours |
| P3 (Low) | 24 hours | 1 week |

## Recovery Point Objectives (RPO)

- **System Configuration**: 0 (version controlled)
- **User Data**: 1 hour (if implemented)
- **Logs**: 24 hours (acceptable loss)
- **Model State**: 1 hour (if implemented)

---

**Last Updated**: 2025-11-21
**Review Frequency**: Quarterly
**Document Owner**: Nümtema Agency Operations Team