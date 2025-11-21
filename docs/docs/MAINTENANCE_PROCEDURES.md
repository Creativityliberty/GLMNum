# Maintenance Procedures - Aura Model 1 GLM

## Daily Maintenance

### Health Checks (5 minutes)
```bash
cd /app/default_project_1646/Numtema_AGENCY

# 1. Check system status
curl -s http://localhost:8000/health | python -m json.tool

# 2. Review logs for errors
tail -100 logs/aura.log | grep -E "ERROR|CRITICAL"

# 3. Check resource usage
python backend/monitoring.py  # Run once, review output

# 4. Verify all tests pass
./run_tests.sh

# 5. Check disk space
df -h /app
```

**Expected Results**:
- Health status: "healthy"
- No critical errors in logs
- CPU < 80%, Memory < 80%, Disk < 80%
- All tests passing (9/9)
- Sufficient disk space (> 20% free)

### Log Rotation (Automated)
Logs automatically rotate at 10MB. Manual rotation if needed:
```bash
cd /app/default_project_1646/Numtema_AGENCY/logs
mv aura.log "aura_$(date +%Y%m%d_%H%M%S).log"
touch aura.log
```

## Weekly Maintenance

### Performance Review (15 minutes)
```bash
# 1. Analyze metrics trends
cd /app/default_project_1646/Numtema_AGENCY
python -c "
import json
from pathlib import Path

metrics_file = Path('logs/metrics.jsonl')
if metrics_file.exists():
    lines = metrics_file.read_text().strip().split('\n')
    recent = [json.loads(line) for line in lines[-100:]]
    
    avg_cpu = sum(m['cpu_percent'] for m in recent) / len(recent)
    avg_mem = sum(m['memory_percent'] for m in recent) / len(recent)
    
    print(f'Average CPU (last 100 samples): {avg_cpu:.2f}%')
    print(f'Average Memory (last 100 samples): {avg_mem:.2f}%')
"

# 2. Check alert frequency
wc -l logs/alerts.jsonl

# 3. Review consciousness system learning
python validate_integration.py | grep -A 5 "Consciousness System"

# 4. Update dependencies (check for updates only)
pip list --outdated
```

### Backup Verification (10 minutes)
```bash
# 1. Verify all critical files exist
ls -lh backend/*.py frontend/*.{html,js,css} config/*.json

# 2. Test system restore capability
cp -r /app/default_project_1646/Numtema_AGENCY /tmp/aura_backup_test
cd /tmp/aura_backup_test && ./run_tests.sh
rm -rf /tmp/aura_backup_test

# 3. Document backup status
echo "$(date): Backup verified" >> logs/maintenance.log
```

## Monthly Maintenance

### Security Updates (30 minutes)
```bash
cd /app/default_project_1646/Numtema_AGENCY

# 1. Update Python packages
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# 2. Run security audit
pip check
pip-audit  # if available

# 3. Review access logs
grep -E "401|403|500" logs/aura.log | tail -50

# 4. Update dependencies in requirements.txt
pip freeze > requirements.txt.new
# Review differences before applying
diff requirements.txt requirements.txt.new

# 5. Run full test suite
./run_tests.sh
python validate_integration.py
```

### Performance Optimization (45 minutes)
```bash
# 1. Profile RRLA pipeline
python -c "
import sys
sys.path.insert(0, 'backend')
from aura_glm import AuraModel1GLM
import time

model = AuraModel1GLM()
query = 'Explain quantum entanglement'

start = time.time()
result = model.process(query)
elapsed = time.time() - start

print(f'Processing time: {elapsed:.2f}s')
print(f'Characters generated: {len(result[\"response\"])}')
print(f'Throughput: {len(result[\"response\"])/elapsed:.2f} chars/sec')
"

# 2. Analyze memory usage patterns
python -c "
import json
from pathlib import Path

metrics = Path('logs/metrics.jsonl')
if metrics.exists():
    data = [json.loads(line) for line in metrics.read_text().strip().split('\n')]
    peak_mem = max(m['memory_percent'] for m in data)
    print(f'Peak memory usage: {peak_mem:.2f}%')
    
    if peak_mem > 85:
        print('WARNING: Consider memory optimization')
"

# 3. Clean up old logs (keep last 30 days)
find logs/ -name "*.log" -mtime +30 -delete
find logs/ -name "*.jsonl" -mtime +30 -delete
```

### Documentation Review (20 minutes)
```bash
# 1. Verify all documentation is current
ls -l docs/*.md

# 2. Update version information
echo "Last maintenance: $(date)" >> docs/MAINTENANCE_LOG.md

# 3. Review and update OPERATIONAL_GUIDE.md if needed
nano docs/OPERATIONAL_GUIDE.md
```

## Quarterly Maintenance

### Comprehensive System Review (2 hours)

#### 1. Architecture Review
- Review system architecture documentation
- Identify potential improvements
- Plan optimization initiatives
- Update ARCHITECTURE.md

#### 2. Disaster Recovery Test
```bash
# Full system restore simulation
cd /tmp
mkdir aura_dr_test
cd aura_dr_test

# Clone from version control or backup
cp -r /app/default_project_1646/Numtema_AGENCY .

# Verify restore
cd Numtema_AGENCY
pip install -r requirements.txt
./run_tests.sh
python validate_integration.py

# Test server startup
timeout 30s python backend/server.py &
sleep 5
curl http://localhost:8000/health

# Cleanup
cd /tmp && rm -rf aura_dr_test
```

#### 3. Capacity Planning
```bash
# Analyze growth trends
python -c "
import json
from pathlib import Path
from datetime import datetime, timedelta

metrics_file = Path('logs/metrics.jsonl')
if metrics_file.exists():
    lines = metrics_file.read_text().strip().split('\n')
    data = [json.loads(line) for line in lines]
    
    # Calculate 90-day moving average
    recent = data[-12960:]  # ~90 days at 1 sample/min
    
    avg_cpu = sum(m['cpu_percent'] for m in recent) / len(recent)
    avg_mem = sum(m['memory_percent'] for m in recent) / len(recent)
    avg_disk = sum(m['disk_usage_percent'] for m in recent) / len(recent)
    
    print('=== 90-Day Resource Utilization ===')
    print(f'Average CPU: {avg_cpu:.2f}%')
    print(f'Average Memory: {avg_mem:.2f}%')
    print(f'Average Disk: {avg_disk:.2f}%')
    
    # Capacity warnings
    if avg_cpu > 70:
        print('⚠️  Consider CPU upgrade or optimization')
    if avg_mem > 70:
        print('⚠️  Consider memory upgrade')
    if avg_disk > 70:
        print('⚠️  Consider disk cleanup or expansion')
"
```

#### 4. Security Audit
- Review access controls
- Update authentication mechanisms
- Scan for vulnerabilities
- Review incident response procedures
- Update security documentation

#### 5. Performance Benchmarking
```bash
cd /app/default_project_1646/Numtema_AGENCY

# Run comprehensive benchmark suite
python -c "
import sys
import time
sys.path.insert(0, 'backend')
from aura_glm import AuraModel1GLM

model = AuraModel1GLM()
queries = [
    'Explain the Δ∞Ο framework',
    'What is consciousness in AI?',
    'How does RRLA reasoning work?',
    'Describe quantum computing',
    'What is machine learning?'
]

print('=== Performance Benchmark ===')
total_time = 0
for i, query in enumerate(queries, 1):
    start = time.time()
    result = model.process(query)
    elapsed = time.time() - start
    total_time += elapsed
    print(f'{i}. \"{query[:30]}...\" - {elapsed:.2f}s')

print(f'\nAverage response time: {total_time/len(queries):.2f}s')
print(f'Total benchmark time: {total_time:.2f}s')
"
```

## Emergency Maintenance

### Hotfix Deployment
```bash
cd /app/default_project_1646/Numtema_AGENCY

# 1. Backup current state
cp -r . ../Numtema_AGENCY_backup_$(date +%Y%m%d_%H%M%S)

# 2. Apply hotfix (example)
# - Edit necessary files
# - Test changes

# 3. Verify fix
./run_tests.sh
python validate_integration.py

# 4. Restart service
pkill -f server.py
./start_aura.sh

# 5. Monitor for 15 minutes
tail -f logs/aura.log

# 6. Verify health
curl http://localhost:8000/health
```

### Rollback Procedure
```bash
# 1. Stop current service
pkill -f server.py

# 2. Restore from backup
cd /app/default_project_1646
rm -rf Numtema_AGENCY
cp -r Numtema_AGENCY_backup_YYYYMMDD_HHMMSS Numtema_AGENCY

# 3. Restart service
cd Numtema_AGENCY
./start_aura.sh

# 4. Verify restoration
./run_tests.sh
curl http://localhost:8000/health
```

## Maintenance Checklist

### Pre-Maintenance
- [ ] Notify stakeholders (if user-facing)
- [ ] Backup current system state
- [ ] Document current configuration
- [ ] Prepare rollback plan
- [ ] Schedule maintenance window

### During Maintenance
- [ ] Follow maintenance procedures exactly
- [ ] Document all changes made
- [ ] Run tests after each major change
- [ ] Monitor system metrics continuously
- [ ] Keep stakeholders informed of progress

### Post-Maintenance
- [ ] Run full test suite
- [ ] Verify all functionality
- [ ] Monitor for 30 minutes minimum
- [ ] Document maintenance completion
- [ ] Notify stakeholders of completion
- [ ] Update maintenance log

## Maintenance Log Template

```markdown
## Maintenance Session: [YYYY-MM-DD HH:MM]

**Type**: [Daily/Weekly/Monthly/Emergency]
**Duration**: [Start] to [End]
**Performed By**: [Name/Team]

### Activities Completed
1. [Activity 1]
2. [Activity 2]
3. [Activity 3]

### Issues Encountered
- [Issue description and resolution]

### Observations
- [Notable findings or recommendations]

### Next Actions
- [ ] [Action item 1]
- [ ] [Action item 2]

**Status**: [Completed/Partial/Rescheduled]
```

## Troubleshooting Common Maintenance Issues

### Issue: Tests Failing After Update
1. Check Python version compatibility
2. Review requirements.txt changes
3. Clear Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +`
4. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
5. Rollback if unresolvable

### Issue: High Memory After Maintenance
1. Restart Python processes
2. Clear system cache if available
3. Check for memory leaks in new code
4. Review model loading strategy
5. Monitor for 1 hour post-maintenance

### Issue: Slow Performance After Updates
1. Profile code execution
2. Check for new dependencies
3. Review algorithm changes
4. Test with previous version
5. Optimize or rollback

---

**Last Updated**: 2025-11-21
**Review Schedule**: Monthly
**Document Owner**: Nümtema Agency Operations Team