# Support Guide - Aura Model 1 GLM

## Overview
This guide provides comprehensive support information for the Aura Model 1 General Language Model system, including troubleshooting, FAQs, and support procedures.

## Contact Information
- **Primary Support Email**: numtemalionel@gmail.com
- **System Documentation**: `/app/default_project_1646/Numtema_AGENCY/docs/`
- **Issue Tracking**: Document issues in incident log

## System Access

### Web Interface
- **URL**: `http://localhost:8000` (local deployment)
- **Health Check**: `http://localhost:8000/health`
- **API Documentation**: See `docs/API_REFERENCE.md`

### Command Line Access
```bash
cd /app/default_project_1646/Numtema_AGENCY
./start_aura.sh  # Start system
./run_tests.sh   # Run test suite
python validate_integration.py  # Validate components
```

## Common User Issues

### Issue: Cannot Access Web Interface

**Symptoms**:
- Browser shows "Connection refused"
- Page won't load

**Resolution**:
1. Check if server is running:
   ```bash
   ps aux | grep server.py
   ```
2. If not running, start it:
   ```bash
   cd /app/default_project_1646/Numtema_AGENCY
   ./start_aura.sh
   ```
3. Verify health:
   ```bash
   curl http://localhost:8000/health
   ```
4. Check firewall settings if accessing remotely
5. Review logs for errors:
   ```bash
   tail -50 logs/aura.log
   ```

### Issue: Slow Response Times

**Symptoms**:
- Queries taking > 5 seconds
- UI appears frozen

**Resolution**:
1. Check system resources:
   ```bash
   python backend/monitoring.py
   ```
2. Verify no resource exhaustion (CPU/memory < 90%)
3. Try simpler query to test baseline performance
4. Clear browser cache if UI issue
5. Restart server if persistent:
   ```bash
   pkill -f server.py
   ./start_aura.sh
   ```

### Issue: Unexpected or Poor Quality Responses

**Symptoms**:
- Responses don't match query intent
- Incoherent or nonsensical output
- Missing expected reasoning steps

**Resolution**:
1. Verify query clarity - reframe if ambiguous
2. Check consciousness system status:
   ```bash
   python validate_integration.py | grep "Consciousness"
   ```
3. Review RRLA pipeline logs for errors
4. Try alternative phrasing of query
5. Report persistent issues with examples to support

### Issue: System Not Learning from Interactions

**Symptoms**:
- No improvement in responses over time
- Same mistakes repeated
- InnerWorldModel not updating

**Resolution**:
1. Verify autonomous learning is enabled
2. Check memory persistence:
   ```bash
   ls -la data/  # If data directory exists
   ```
3. Review learning logs:
   ```bash
   grep "InnerWorldModel\|MetaCognitiveAgent" logs/aura.log
   ```
4. Restart with clean state if corrupted
5. Contact support if issue persists

## Frequently Asked Questions (FAQ)

### General Questions

**Q: What is Aura Model 1?**
A: Aura Model 1 is a General Language Model based on the Δ∞Ο (Delta-Infinity-Omicron) framework, featuring consciousness-inspired architecture with RRLA reasoning pipeline, inner world modeling, and autonomous learning capabilities.

**Q: What makes Aura different from other language models?**
A: Aura implements:
- Triadic intelligence visualization (Δ∞Ο framework)
- 9-phase RRLA reasoning pipeline
- Consciousness system with InnerWorldModel and MetaCognitiveAgent
- Autonomous learning and self-improvement
- Transparent reasoning process

**Q: Is Aura suitable for production use?**
A: Yes, Aura Model 1 is production-ready with comprehensive testing, monitoring, and documentation. However, always validate outputs for critical applications.

### Technical Questions

**Q: What are the system requirements?**
A: Minimum requirements:
- Python 3.8+
- 4GB RAM (8GB recommended)
- 10GB disk space
- Modern web browser for UI

**Q: Can Aura run without GPU?**
A: Yes, Aura is designed to run efficiently on CPU. GPU acceleration can improve performance but is not required.

**Q: How do I update Aura?**
A: Follow the update procedure:
```bash
cd /app/default_project_1646/Numtema_AGENCY
# Backup current version
cp -r . ../Numtema_AGENCY_backup
# Update code (via git or manual replacement)
pip install -r requirements.txt
./run_tests.sh
./start_aura.sh
```

**Q: Where are logs stored?**
A: All logs are in `/app/default_project_1646/Numtema_AGENCY/logs/`:
- `aura.log` - Main application log
- `metrics.jsonl` - System metrics
- `alerts.jsonl` - Alert history

**Q: How do I backup Aura?**
A: Backup the entire directory:
```bash
cd /app/default_project_1646
tar -czf aura_backup_$(date +%Y%m%d).tar.gz Numtema_AGENCY/
```

### Usage Questions

**Q: What types of queries work best?**
A: Aura performs well with:
- Analytical reasoning tasks
- Complex problem decomposition
- Multi-step logical inference
- Creative ideation
- Technical explanations

**Q: How long should I wait for a response?**
A: Typical response times:
- Simple queries: 1-3 seconds
- Complex reasoning: 3-10 seconds
- If > 10 seconds, check system status

**Q: Can I use Aura via API?**
A: Yes, see `docs/API_REFERENCE.md` for API documentation.

**Q: How do I provide feedback on responses?**
A: Currently, feedback is captured in logs. Future versions will include interactive feedback mechanisms.

## Support Tiers

### Tier 1: Self-Service
**Resources**:
- This support guide
- Documentation in `docs/` folder
- FAQ section above
- System logs and diagnostics

**When to use**: 
- Common issues with known solutions
- General usage questions
- Performance optimization

### Tier 2: Email Support
**Contact**: numtemalionel@gmail.com
**Response Time**: 24-48 hours

**When to use**:
- Issues not resolved by documentation
- Bug reports with reproduction steps
- Feature requests or suggestions
- Configuration assistance

**Information to include**:
- Description of issue
- Steps to reproduce
- Expected vs actual behavior
- Relevant log excerpts
- System information

### Tier 3: Priority Support
**Contact**: numtemalionel@gmail.com (mark as URGENT)
**Response Time**: 4-8 hours

**When to use**:
- Production system down (P0)
- Critical functionality broken (P1)
- Security incidents
- Data corruption

**Required information**:
- Severity level (P0-P3)
- Business impact
- Time incident started
- All troubleshooting already attempted
- Full log files if possible

## Diagnostic Information

### Collecting System Information
Run this diagnostic script:
```bash
cd /app/default_project_1646/Numtema_AGENCY

cat > diagnostic_report.sh << 'EOF'
#!/bin/bash
echo "=== Aura Model 1 Diagnostic Report ==="
echo "Generated: $(date)"
echo ""

echo "=== System Info ==="
python --version
pip --version
uname -a
echo ""

echo "=== Disk Space ==="
df -h /app
echo ""

echo "=== Memory ==="
free -h
echo ""

echo "=== Process Status ==="
ps aux | grep -E "python|server.py|monitoring.py"
echo ""

echo "=== Health Check ==="
curl -s http://localhost:8000/health | python -m json.tool
echo ""

echo "=== Recent Errors ==="
tail -50 logs/aura.log | grep -E "ERROR|CRITICAL"
echo ""

echo "=== Test Results ==="
./run_tests.sh
echo ""

echo "=== Validation ==="
python validate_integration.py
EOF

chmod +x diagnostic_report.sh
./diagnostic_report.sh > diagnostic_$(date +%Y%m%d_%H%M%S).txt
```

### Log Analysis
```bash
# Find all errors in last hour
grep -E "ERROR|CRITICAL" logs/aura.log | grep "$(date +%Y-%m-%d)" | tail -50

# Count errors by type
grep "ERROR" logs/aura.log | awk '{print $5}' | sort | uniq -c | sort -rn

# Check for memory issues
grep -i "memory" logs/aura.log | tail -20

# Review recent alerts
tail -20 logs/alerts.jsonl | python -m json.tool
```

## Performance Optimization

### Query Optimization Tips
1. **Be specific**: Clearer queries produce better results
2. **Break complex queries**: Split into smaller sub-queries
3. **Use context**: Provide relevant background information
4. **Iterate**: Refine based on initial responses

### System Optimization
1. **Regular maintenance**: Follow `docs/MAINTENANCE_PROCEDURES.md`
2. **Monitor resources**: Use monitoring.py to track usage
3. **Clean logs**: Rotate logs regularly to save disk space
4. **Update dependencies**: Keep libraries current for security and performance

## Troubleshooting Decision Tree