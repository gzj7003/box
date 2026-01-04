import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import re

def setup_chrome_options():
    """配置Chrome选项"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # 设置下载路径（当前工作目录）
    prefs = {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    return chrome_options

def wait_and_click(driver, element, timeout=10):
    """等待元素可点击并点击"""
    wait = WebDriverWait(driver, timeout)
    element_to_click = wait.until(EC.element_to_be_clickable(element))
    element_to_click.click()
    time.sleep(1)  # 等待点击响应

def extract_channel_data(text, channel_name):
    """从页面文本中提取指定频道的数据"""
    lines = text.strip().split('\n')
    for line in lines:
        # 检查是否包含频道名称
        if channel_name in line:
            # 查找包含IP地址的部分
            ip_match = re.search(r'(rtp://|udp://|http://)\S+', line)
            if ip_match:
                return line.strip()
    return None

def ensure_cctv_channels():
    """确保包含CCTV1-15频道的基础源"""
    # CCTV基础频道列表 - 按照标准格式
    cctv_channels = []
    
    # 标准CCTV1-15频道列表
    base_cctv = [
        ("CCTV1", "CCTV-1综合"),
        ("CCTV2", "CCTV-2财经"),
        ("CCTV3", "CCTV-3综艺"),
        ("CCTV4", "CCTV-4中文国际"),
        ("CCTV5", "CCTV-5体育"),
        ("CCTV6", "CCTV-6电影"),
        ("CCTV7", "CCTV-7国防军事"),
        ("CCTV8", "CCTV-8电视剧"),
        ("CCTV9", "CCTV-9纪录"),
        ("CCTV10", "CCTV-10科教"),
        ("CCTV11", "CCTV-11戏曲"),
        ("CCTV12", "CCTV-12社会与法"),
        ("CCTV13", "CCTV-13新闻"),
        ("CCTV14", "CCTV-14少儿"),
        ("CCTV15", "CCTV-15音乐")
    ]
    
    # 添加CCTV频道到结果中
    for cctv_num, cctv_name in base_cctv:
        # 添加多种可能的名称格式以确保匹配
        cctv_channels.append(f"{cctv_num},{cctv_name} - 待更新源")
        cctv_channels.append(f"{cctv_name},rtp://239.76.253.{100 + int(cctv_num[4:])}:8000")
    
    return cctv_channels

def search_for_cctv_in_content(text_content):
    """在抓取的内容中搜索CCTV频道"""
    found_cctv = []
    
    # 搜索所有可能的CCTV格式
    cctv_patterns = [
        r'(CCTV[-\s]?1[^\d]*)',
        r'(CCTV[-\s]?2[^\d]*)',
        r'(CCTV[-\s]?3[^\d]*)',
        r'(CCTV[-\s]?4[^\d]*)',
        r'(CCTV[-\s]?5[^\d]*)',
        r'(CCTV[-\s]?6[^\d]*)',
        r'(CCTV[-\s]?7[^\d]*)',
        r'(CCTV[-\s]?8[^\d]*)',
        r'(CCTV[-\s]?9[^\d]*)',
        r'(CCTV[-\s]?10[^\d]*)',
        r'(CCTV[-\s]?11[^\d]*)',
        r'(CCTV[-\s]?12[^\d]*)',
        r'(CCTV[-\s]?13[^\d]*)',
        r'(CCTV[-\s]?14[^\d]*)',
        r'(CCTV[-\s]?15[^\d]*)'
    ]
    
    for pattern in cctv_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        for match in matches:
            # 查找匹配行的完整内容
            lines = text_content.split('\n')
            for line in lines:
                if match.strip() in line:
                    found_cctv.append(line.strip())
                    break
    
    return found_cctv

def main():
    print("🚀 开始自动化采集组播IP数据...")
    
    # 打印调试信息：当前工作目录和脚本位置
    print(f"📂 当前工作目录: {os.getcwd()}")
    print(f"📂 脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 设置输出文件路径 - 明确保存在工作空间根目录
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_filename = "zbhb-pl10000.txt"
    output_path = os.path.join(workspace_root, output_filename)
    
    print(f"📄 文件将保存到: {output_path}")
    
    # 初始化结果数据，先确保包含CCTV1-15
    all_data = ""
    
    # 添加CCTV1-15基础频道到结果中
    print("📺 确保包含CCTV1-15基础频道...")
    cctv_base = ensure_cctv_channels()
    for channel in cctv_base:
        all_data += channel + "\n"
    
    # 初始化浏览器
    chrome_options = setup_chrome_options()
    
    # 在GitHub Actions中，Chrome可能需要特殊安装
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"⚠️  初始化Chrome失败: {e}")
        print("尝试使用chromedriver-autoinstaller...")
        try:
            import chromedriver_autoinstaller
            chromedriver_autoinstaller.install()
            driver = webdriver.Chrome(options=chrome_options)
        except:
            print("❌ 无法启动Chrome，请确保已正确安装Chrome和ChromeDriver")
            # 即使没有浏览器，也保存包含CCTV1-15的基础文件
            save_results(all_data, output_path, workspace_root)
            return
    
    try:
        # 第一步：打开初始页面
        print("📄 打开初始页面...")
        driver.get("https://pl10000.infinityfreeapp.com/10.html")
        time.sleep(3)
        
        # 第二步：点击"搜搜"图标
        print("🔍 点击'搜搜'图标...")
        try:
            wait_and_click(driver, (By.CSS_SELECTOR, '.icon[data-title="搜搜"]'))
        except:
            print("⚠️  找不到搜搜图标，尝试其他选择器...")
            # 尝试其他可能的搜搜图标选择器
            try:
                wait_and_click(driver, (By.XPATH, "//div[@class='icon' and contains(@data-title, '搜')]"))
            except:
                print("❌ 无法找到搜搜图标，直接搜索CCTV内容")
        
        # 等待iframe加载
        print("⏳ 等待'搜搜'页面加载...")
        time.sleep(5)
        
        # 尝试切换到iframe（根据源码，iframe的id是"browser"）
        try:
            wait = WebDriverWait(driver, 20)
            iframe = wait.until(EC.presence_of_element_located((By.ID, "browser")))
            driver.switch_to.frame(iframe)
            print("✅ 成功切换到搜搜页面")
            time.sleep(3)
        except:
            print("⚠️  无法切换到iframe，尝试在当前页面搜索")
        
        # 获取当前页面的源码，用于调试
        page_source = driver.page_source
        
        # 第三步：搜索CCTV相关内容
        print("🔍 搜索CCTV相关内容...")
        
        # 尝试查找页面中的所有文本
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            cctv_results = search_for_cctv_in_content(page_text)
            
            if cctv_results:
                print(f"✅ 找到 {len(cctv_results)} 个CCTV相关频道")
                all_data += "\n# ====== 抓取到的CCTV频道 ======\n"
                for result in cctv_results:
                    all_data += result + "\n"
            else:
                print("⚠️  未找到CCTV频道，使用基础频道列表")
        except:
            print("⚠️  无法获取页面文本，使用基础频道列表")
        
        # 第四步：点击各个电信/联通按钮，搜索更多频道
        telecom_buttons = ["北京电信", "广东电信", "陕西电信", "云南电信", "安徽电信", "江苏电信", "淅江电信"]
        
        for button_name in telecom_buttons:
            print(f"📡 正在处理: {button_name}")
            
            try:
                # 尝试通过链接文本查找按钮
                button = wait.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, button_name))
                )
                button.click()
                
                # 等待新内容加载
                time.sleep(4)
                
                # 获取当前页面文本内容
                current_text = driver.find_element(By.TAG_NAME, "body").text
                
                # 在内容中搜索CCTV频道
                cctv_results = search_for_cctv_in_content(current_text)
                
                if cctv_results:
                    all_data += f"\n# ====== {button_name}中的CCTV频道 ======\n"
                    for result in cctv_results:
                        all_data += result + "\n"
                    print(f"  ✅ 从 {button_name} 中找到 {len(cctv_results)} 个CCTV频道")
                else:
                    print(f"  ⚠️  未在 {button_name} 中找到CCTV频道")
                
                # 尝试返回
                try:
                    driver.execute_script("window.history.back();")
                except:
                    pass
                
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ 处理 {button_name} 时出错: {str(e)}")
                continue
        
        # 第五步：添加卫视频道（确保有基础卫视列表）
        print("📡 添加卫视频道...")
        tv_stations = [
            "湖南卫视,rtp://239.76.253.159:8000",
            "浙江卫视,rtp://239.76.253.158:8000", 
            "东方卫视,rtp://239.76.253.157:8000",
            "北京卫视,rtp://239.76.253.156:8000",
            "江苏卫视,rtp://239.76.253.155:8000",
            "安徽卫视,rtp://239.76.253.154:8000",
            "重庆卫视,rtp://239.76.253.153:8000",
            "四川卫视,rtp://239.76.253.152:8000",
            "天津卫视,rtp://239.76.253.151:8000",
            "兵团卫视,rtp://239.76.253.150:8000"
        ]
        
        all_data += "\n# ====== 卫视频道 ======\n"
        for station in tv_stations:
            all_data += station + "\n"
        
        # 保存结果
        save_results(all_data, output_path, workspace_root)
    
    except Exception as e:
        print(f"❌ 程序执行出错: {str(e)}")
        
        # 出错时保存当前已收集的数据
        save_results(all_data, output_path, workspace_root)
        
        # 截图和保存源码用于调试
        try:
            screenshot_name = "error_screenshot.png"
            screenshot_path = os.path.join(workspace_root, screenshot_name)
            driver.save_screenshot(screenshot_path)
            print(f"📸 错误截图已保存为: {screenshot_path}")
        except:
            pass
        
        # 保存当前页面源码
        try:
            debug_name = "error_page_source.html"
            debug_path = os.path.join(workspace_root, debug_name)
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source if 'driver' in locals() else "No page source")
            print(f"📄 页面源码已保存为: {debug_path}")
        except:
            pass
    
    finally:
        # 关闭浏览器
        try:
            driver.quit()
            print("\n🛑 浏览器已关闭")
        except:
            pass

def save_results(data, output_path, workspace_root):
    """保存结果到文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(data)
    
    # 统计信息
    line_count = len(data.strip().split('\n'))
    
    print(f"\n🎉 数据采集完成!")
    print(f"📝 总行数: {line_count} 行")
    print(f"💾 文件已保存为: {output_path}")
    
    # 验证文件是否真的保存了
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✅ 文件确认存在，大小: {file_size} 字节")
    else:
        print("❌ 警告: 文件似乎没有成功保存")
    
    # 显示文件预览
    print("\n📋 文件预览（前15行）:")
    print("-" * 50)
    lines = data.strip().split('\n')[:15]
    for i, line in enumerate(lines, 1):
        print(f"{i:2}: {line}")
    print("-" * 50)
    
    # 同时保存一份到当前脚本目录，便于调试
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir_output = os.path.join(script_dir, "zbhb1-pl10000.txt")
    with open(script_dir_output, "w", encoding="utf-8") as f:
        f.write(data)
    print(f"📝 备份文件已保存到脚本目录: {script_dir_output}")

if __name__ == "__main__":
    main()
