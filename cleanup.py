#!/usr/bin/env python3
"""
Cleanup Script - Kill all processes and reset ports
====================================================

Kills all Python/uvicorn processes and resets the system.
Works on macOS and Linux.
"""

import os
import subprocess
import time
import signal

def run_command(cmd):
    """Run shell command silently"""
    try:
        subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
    except:
        pass

def main():
    print("\n" + "="*70)
    print("🧹 SYSTEM CLEANUP - Kill all processes and reset ports")
    print("="*70 + "\n")
    
    # Kill Python processes
    print("❌ Killing Python processes...")
    run_command("pkill -f 'python' 2>/dev/null")
    run_command("pkill -f 'uvicorn' 2>/dev/null")
    run_command("pkill -f 'api' 2>/dev/null")
    time.sleep(1)
    
    # Kill processes on specific ports
    print("❌ Killing processes on ports 8000-8090...")
    for port in range(8000, 8091):
        run_command(f"lsof -ti:{port} | xargs kill -9 2>/dev/null")
    time.sleep(1)
    
    print("✅ Cleanup complete!\n")
    
    # Verify cleanup
    print("🔍 Verification:\n")
    
    # Check for remaining Python processes
    result = subprocess.run(
        "ps aux | grep -E 'python|uvicorn|api' | grep -v grep",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        print("⚠️  Remaining processes:")
        print(result.stdout)
    else:
        print("✅ No Python/uvicorn processes running")
    
    # Check ports
    print("\n🔍 Port Status:")
    for port in [8000, 8080, 8081]:
        result = subprocess.run(
            f"lsof -Pi :{port} -sTCP:LISTEN -t 2>/dev/null",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print(f"⚠️  Port {port} is still in use")
        else:
            print(f"✅ Port {port} is free")
    
    print("\n" + "="*70)
    print("✅ System reset complete!")
    print("="*70)
    print("\n🚀 Ready to start fresh. Run:\n")
    print("   python backend.py")
    print("   or")
    print("   uvicorn backend:app --host 0.0.0.0 --port 8081\n")

if __name__ == "__main__":
    main()
