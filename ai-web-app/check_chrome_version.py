import subprocess
import re

def get_chrome_version():
    """获取Chrome浏览器版本"""
    try:
        # Windows系统下获取Chrome版本
        result = subprocess.run(
            ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            version_match = re.search(r'version\s+REG_SZ\s+([\d.]+)', result.stdout)
            if version_match:
                return version_match.group(1)
        
        # 尝试另一个注册表路径
        result = subprocess.run(
            ['reg', 'query', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Google\\Chrome\\BLBeacon', '/v', 'version'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            version_match = re.search(r'version\s+REG_SZ\s+([\d.]+)', result.stdout)
            if version_match:
                return version_match.group(1)
        
        return None
    except Exception as e:
        print(f"获取Chrome版本失败: {e}")
        return None

if __name__ == '__main__':
    version = get_chrome_version()
    if version:
        print(f"✅ 检测到Chrome浏览器版本: {version}")
        
        # 提取主版本号
        major_version = version.split('.')[0]
        print(f"   主版本号: {major_version}")
        print(f"\n请下载对应的ChromeDriver:")
        print(f"   https://chromedriver.chromium.org/downloads")
        print(f"   或使用自动化工具: https://googlechromelabs.github.io/chrome-for-testing/")
    else:
        print("❌ 未检测到Chrome浏览器")
        print("   请先安装Chrome浏览器: https://www.google.com/chrome/")
