from app import create_app, db
from app.models import User, CrawlerSource, CrawlerTask, CrawlerData, CollectionData, AIModel, AIModelUsage

app = create_app()

with app.app_context():
    print("正在重新创建数据库...")
    
    db.drop_all()
    print("已删除所有表")
    
    db.create_all()
    print("已创建所有表")
    
    print("\n数据库初始化完成！")
    print("登录信息：")
    print("用户名: admin")
    print("密码: 123456")
