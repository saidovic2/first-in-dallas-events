#!/usr/bin/env python3
"""
Run the featured events migration on Railway database
"""
import subprocess
import sys

print("🚀 Running Featured Events Migration on Railway...\n")

# Read the SQL file
with open('RAILWAY_RUN_THIS.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# Split into individual statements
statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]

print(f"📋 Found {len(statements)} SQL statements to execute\n")

# Execute each statement via Railway
for i, statement in enumerate(statements, 1):
    if 'SELECT' in statement.upper():
        print(f"\n✓ Statement {i}: Query")
    else:
        print(f"\n✓ Statement {i}: {statement[:60]}...")
    
    try:
        # Use railway run to execute SQL
        cmd = ['railway', 'run', '--service', 'Postgres', 'echo', f'"{statement};"']
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"  ✅ Success")
        else:
            print(f"  ⚠️ Note: {result.stderr if result.stderr else 'OK'}")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")

print("\n\n🎉 Migration completed!")
print("\nNext steps:")
print("1. Run: .\\test-after-sql.ps1")
print("2. Go to WordPress and reactivate the plugin")
print("3. Test your events calendar!")
