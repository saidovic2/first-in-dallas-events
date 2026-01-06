"""Check what enum values are allowed"""
from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway'

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check price_tier enum values
        result = conn.execute(text("""
            SELECT unnest(enum_range(NULL::pricetier)) as price_tier
        """))
        
        print("Allowed price_tier values:")
        for row in result:
            print(f"  - '{row[0]}'")
        
        # Check event columns
        result = conn.execute(text("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'events'
            AND column_name IN ('price_tier', 'status', 'source_type')
        """))
        
        print("\nColumn types:")
        for row in result:
            print(f"  {row[0]}: {row[1]} ({row[2]})")
            
except Exception as e:
    print(f"[ERROR] {e}")
