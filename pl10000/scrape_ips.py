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

def extract_and_filter_channels(text):
    """从页面文本中提取并过滤频道数据"""
    lines = text.strip().split('\n')
    filtered_channels = {}
    
    # 定义需要保留的频道模式
    cctv_patterns = [
        r'CCTV-?1[^0-9]', r'CCTV-?2[^0-9]', r'CCTV-?3[^0-9]', r'CCTV-?4[^0-9]',
        r'CCTV-?5[^0-9]', r'CCTV-?6[^0-9]', r'CCTV-?7[^0-9]', r'CCTV-?8[^0-9]',
        r'CCTV-?9[^0-9]', r'CCTV-?10[^0-9]', r'CCTV-?11[^0-9]', r'CCTV-?12[^0-9]',
        r'CCTV-?13[^0-9]', r'CCTV-?14[^0-9]', r'CCTV-?15[^0-9]',
        r'央视-?1[^0-9]', r'央视-?2[^0-9]', r'央视-?3[^0-9]', r'央视-?4[^0-9]',
        r'央视-?5[^0-9]', r'央视-?6[^0-9]', r'央视-?7[^0-9]', r'央视-?8[^0-9]',
        r'央视-?9[^0-9]', r'央视-?10[^0-9]', r'央视-?11[^0-9]', r'央视-?12[^0-9]',
        r'央视-?13[^0-9]', r'央视-?14[^0-9]', r'央视-?15[^0-9]'
    ]
    
    # 卫视模式
    satellite_patterns = [
        r'卫视', r'湖南卫视', r'浙江卫视', r'江苏卫视', r'东方卫视', r'北京卫视',
        r'安徽卫视', r'山东卫视', r'天津卫视', r'重庆卫视', r'四川卫视',
        r'广东卫视', r'深圳卫视', r'黑龙江卫视', r'辽宁卫视', r'河南卫视',
        r'湖北卫视', r'福建卫视', r'江西卫视', r'广西卫视', r'山西卫视',
        r'陕西卫视', r'贵州卫视', r'云南卫视', r'甘肃卫视', r'青海卫视',
        r'宁夏卫视', r'新疆卫视', r'西藏卫视', r'内蒙古卫视', r'河北卫视',
        r'吉林卫视', r'海南卫视'
    ]
    
    for line in lines:
        line = line.strip()
        
        # 查找频道名称和URL
        if ',' in line and ('http://' in line or 'udp://' in line or 'rtp://' in line):
            parts = line.split(',', 1)
            if len(parts) == 2:
                channel_name, channel_url = parts
                
                # 检查是否为CCTV频道
                is_cctv = any(re.search(pattern, channel_name, re.IGNORECASE) for pattern in cctv_patterns)
                
                # 检查是否为卫视频道
                is_satellite = any(re.search(pattern, channel_name, re.IGNORECASE) for pattern in satellite_patterns)
                
                # 只保留CCTV1-15和卫视
                if is_cctv or is_satellite:
                    # 标准化CCTV名称
                    if 'CCTV' in channel_name.upper() or '央视' in channel_name:
                        # 提取CCTV编号
                        match = re.search(r'CCTV[- ]?(\d+)', channel_name.upper())
                        if match:
                            cctv_num = int(match.group(1))
                            if 1 <= cctv_num <= 15:
                                filtered_channels[f"CCTV{cctv_num}"] = channel_url
                    else:
                        # 卫视频道
                        filtered_channels[channel_name] = channel_url
    
    return filtered_channels

def add_suzhou_local_channels():
    """添加苏州地方台"""
    suzhou_channels = {
        "苏州新闻综合": "http://live-auth.51kandianshi.com/szgd/csztv1.m3u8",
        "苏州社会经济": "http://live-auth.51kandianshi.com/szgd/csztv2.m3u8",
        "苏州文化生活": "http://live-auth.51kandianshi.com/szgd/csztv3.m3u8",
        "苏州生活资讯": "http://live-auth.51kandianshi.com/szgd/csztv5.m3u8",
        "苏州生活资讯2": "http://180.108.166.124:4022/rtp/239.49.8.116:8000"
    }
    return suzhou_channels

def main():
    print("🚀 开始自动化采集直播源数据...")
    
    # 打印调试信息：当前工作目录和脚本位置
    print(f"📂 当前工作目录: {os.getcwd()}")
    print(f"📂 脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 设置输出文件路径 - 明确保存在工作空间根目录
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_filename = "zbhb-pl10000.txt"
    output_path = os.path.join(workspace_root, output_filename)
    
    print(f"📄 文件将保存到: {output_path}")
    
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
            return
    
    try:
        # 第一步：打开初始页面
        print("📄 打开初始页面...")
        driver.get("https://pl10000.infinityfreeapp.com/10.html")
        time.sleep(3)
        
        # 第二步：点击"搜搜"图标
        print("🔍 点击'搜搜'图标...")
        # 根据提供的HTML源码，搜搜图标有data-title="搜搜"属性
        wait_and_click(driver, (By.CSS_SELECTOR, '.icon[data-title="搜搜"]'))
        
        # 等待iframe加载
        print("⏳ 等待'搜搜'页面加载...")
        time.sleep(5)
        
        # 切换到iframe（根据源码，iframe的id是"browser"）
        wait = WebDriverWait(driver, 20)
        iframe = wait.until(EC.presence_of_element_located((By.ID, "browser")))
        driver.switch_to.frame(iframe)
        
        print("✅ 成功切换到搜搜页面")
        time.sleep(3)
        
        # 获取当前页面的源码，用于调试
        page_source = driver.page_source
        
        # 第三步：点击各个电信/联通按钮
        telecom_buttons = ["北京电信", "广东电信", "陕西电信", "云南电信", "安徽电信", "江苏电信", "淅江电信"]
        all_channels = {}  # 使用字典避免重复
        
        for button_name in telecom_buttons:
            print(f"📡 正在处理: {button_name}")
            
            try:
                # 尝试通过链接文本查找按钮
                button = wait.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, button_name))
                )
                button.click()
                
                # 等待新内容加载（根据页面行为调整等待时间）
                time.sleep(4)
                
                # 获取当前页面文本内容
                current_text = driver.find_element(By.TAG_NAME, "body").text
                
                # 提取并过滤频道数据
                filtered = extract_and_filter_channels(current_text)
                
                if filtered:
                    # 合并到总字典
                    all_channels.update(filtered)
                    print(f"  ✅ 从 {button_name} 获取了 {len(filtered)} 个有效频道")
                else:
                    print(f"  ⚠️  未从 {button_name} 提取到有效频道")
                
                # 点击后可能需要返回或等待页面稳定
                try:
                    # 尝试查找返回按钮
                    back_btn = driver.find_elements(By.XPATH, "//a[contains(text(),'返回') or contains(text(),'Back')]")
                    if back_btn:
                        back_btn[0].click()
                    else:
                        # 如果没有返回按钮，使用浏览器后退
                        driver.execute_script("window.history.back();")
                except:
                    # 如果后退失败，刷新页面回到初始状态
                    driver.refresh()
                
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ 处理 {button_name} 时出错: {str(e)}")
                continue
        
        # 第四步：添加苏州地方台
        print("📡 添加苏州地方台...")
        suzhou_channels = add_suzhou_local_channels()
        all_channels.update(suzhou_channels)
        print(f"  ✅ 添加了 {len(suzhou_channels)} 个苏州地方台")
        
        # 第五步：整理和排序频道
        print("📊 整理频道数据...")
        
        # 分离CCTV和卫视
        cctv_channels = {}
        satellite_channels = {}
        suzhou_local_channels = {}
        
        for name, url in all_channels.items():
            # 检查是否为苏州地方台
            if '苏州' in name:
                suzhou_local_channels[name] = url
            # 检查是否为CCTV
            elif 'CCTV' in name.upper():
                cctv_channels[name] = url
            else:
                satellite_channels[name] = url
        
        # 对CCTV按数字排序
        sorted_cctv = sorted(
            cctv_channels.items(),
            key=lambda x: int(re.search(r'(\d+)', x[0].upper()).group(1)) if re.search(r'(\d+)', x[0].upper()) else 0
        )
        
        # 对卫视按拼音排序（简单按名称排序）
        sorted_satellite = sorted(satellite_channels.items(), key=lambda x: x[0])
        
        # 对苏州地方台排序
        sorted_suzhou = sorted(suzhou_local_channels.items(), key=lambda x: x[0])
        
        # 第六步：保存数据到文件
        with open(output_path, "w", encoding="utf-8") as f:
            # 写入CCTV频道
            f.write("# ====== CCTV频道 ======\n")
            for name, url in sorted_cctv:
                f.write(f"{name},{url}\n")
            
            f.write("\n# ====== 卫视频道 ======\n")
            for name, url in sorted_satellite:
                f.write(f"{name},{url}\n")
            
            f.write("\n# ====== 苏州地方台 ======\n")
            for name, url in sorted_suzhou:
                f.write(f"{name},{url}\n")
        
        # 统计信息
        total_channels = len(sorted_cctv) + len(sorted_satellite) + len(sorted_suzhou)
        print(f"\n🎉 数据采集完成!")
        print(f"📊 频道统计:")
        print(f"  CCTV频道: {len(sorted_cctv)} 个")
        print(f"  卫视频道: {len(sorted_satellite)} 个")
        print(f"  苏州地方台: {len(sorted_suzhou)} 个")
        print(f"  总计: {total_channels} 个频道")
        print(f"💾 文件已保存为: {output_path}")
        
        # 验证文件是否真的保存了
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ 文件确认存在，大小: {file_size} 字节")
        else:
            print("❌ 警告: 文件似乎没有成功保存")
        
        # 显示文件预览
        print("\n📋 文件预览（前20行）:")
        print("-" * 50)
        with open(output_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[:20]
            for i, line in enumerate(lines, 1):
                print(f"{i:2}: {line.rstrip()}")
        print("-" * 50)
        
        # 同时保存一份到当前脚本目录，便于调试
        script_dir_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
        with open(script_dir_output, "w", encoding="utf-8") as f:
            f.write(open(output_path, "r", encoding="utf-8").read())
        print(f"📝 备份文件已保存到脚本目录: {script_dir_output}")
        
    except Exception as e:
        print(f"❌ 程序执行出错: {str(e)}")
        
        # 出错时截图
        screenshot_name = "error_screenshot.png"
        screenshot_path = os.path.join(workspace_root, screenshot_name)
        driver.save_screenshot(screenshot_path)
        print(f"📸 错误截图已保存为: {screenshot_path}")
        
        # 保存当前页面源码
        debug_name = "error_page_source.html"
        debug_path = os.path.join(workspace_root, debug_name)
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"📄 页面源码已保存为: {debug_path}")
    
    finally:
        # 关闭浏览器
        driver.quit()
        print("\n🛑 浏览器已关闭")

if __name__ == "__main__":
    main()
