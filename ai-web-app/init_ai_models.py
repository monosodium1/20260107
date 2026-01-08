from app import create_app, db
from app.models import AIModel, AIModelUsage

app = create_app()

with app.app_context():
    print("Creating AI model tables...")
    
    db.create_all()
    
    print("AI model tables created successfully!")
    
    print("\nChecking if AIModel table exists...")
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'ai_model' in tables:
        print("✓ ai_model table exists")
    else:
        print("✗ ai_model table does not exist")
    
    if 'ai_model_usage' in tables:
        print("✓ ai_model_usage table exists")
    else:
        print("✗ ai_model_usage table does not exist")
    
    print("\nDatabase initialization completed!")
