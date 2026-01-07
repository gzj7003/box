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

def get_base_channels():
    """获取基础频道列表（CCTV1-15 + 卫视）"""
    base_channels = []
    
    # CCTV1-15频道
    cctv_channels = [
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
    
    # 卫视频道
    tv_stations = [
        "江苏卫视",
        "浙江卫视", 
        "东方卫视",
        "北京卫视"
    ]
    
    return cctv_channels, tv_stations

def extract_valid_channels(text):
    """从文本中提取有效的频道数据"""
    valid_channels = []
    
    # 分割行并处理
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 跳过注释行
        if line.startswith('#'):
            continue
            
        # 查找频道名和地址
        if ',' in line:
            parts = line.split(',', 1)
            if len(parts) == 2:
                channel_name, channel_url = parts
                channel_name = channel_name.strip()
                channel_url = channel_url.strip()
                
                # 验证URL格式
                if re.search(r'^(rtp://|udp://|http://|https://)', channel_url):
                    valid_channels.append(f"{channel_name},{channel_url}")
    
    return valid_channels

def search_channels_in_content(text_content, target_channels):
    """在内容中搜索目标频道"""
    found_channels = []
    
    # 将目标频道名称转换为正则表达式模式
    for channel in target_channels:
        # 转义特殊字符
        escaped_channel = re.escape(channel)
        # 创建匹配模式，允许频道名称前后有其他字符
        pattern = rf'.*{escaped_channel}[^,]*,(rtp://|udp://|http://|https://)\S+'
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        
        if matches:
            # 查找匹配的完整行
            for line in text_content.split('\n'):
                if channel.lower() in line.lower():
                    found_channels.append(line.strip())
                    break
    
    return found_channels

def get_suzhou_channels():
    """获取苏州地方台频道"""
    suzhou_channels = [
        "苏州新闻综合,http://live-auth.51kandianshi.com/szgd/csztv1.m3u8",
        "苏州社会经济,http://live-auth.51kandianshi.com/szgd/csztv2.m3u8",
        "苏州文化生活,http://live-auth.51kandianshi.com/szgd/csztv3.m3u8",
        "苏州生活资讯,http://live-auth.51kandianshi.com/szgd/csztv5.m3u8",
        "苏州4K,http://live-auth.51kandianshi.com/szgd/csztv4k_hd.m3u8"
    ]
    return suzhou_channels

def remove_duplicate_channels(channels):
    """去除重复的频道（基于频道名称）"""
    seen = set()
    unique_channels = []
    
    for channel in channels:
        # 提取频道名称
        if ',' in channel:
            name = channel.split(',', 1)[0].strip()
            if name not in seen:
                seen.add(name)
                unique_channels.append(channel)
    
    return unique_channels

def filter_channels_by_type(channels, channel_list):
    """根据频道列表过滤频道"""
    filtered = []
    for channel in channels:
        name = channel.split(',', 1)[0].strip()
        if any(target in name for target in channel_list):
            filtered.append(channel)
    return filtered

def main():
    print("🚀 开始自动化采集直播源数据...")
    
    # 打印调试信息：当前工作目录和脚本位置
    print(f"📂 当前工作目录: {os.getcwd()}")
    print(f"📂 脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 设置输出文件路径 - 明确保存在工作空间根目录
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_filename = "zbhb1-pl10000.txt"
    output_path = os.path.join(workspace_root, output_filename)
    
    print(f"📄 文件将保存到: {output_path}")
    
    # 获取基础频道列表
    cctv_channels, tv_stations = get_base_channels()
    all_cctv_names = [cctv[0] for cctv in cctv_channels] + [cctv[1] for cctv in cctv_channels]
    
    # 初始化收集的频道数据
    collected_channels = []
    
    # 初始化浏览器
    chrome_options = setup_chrome_options()
    
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
            # 即使没有浏览器，也保存基础文件
            save_results(collected_channels, output_path, workspace_root, cctv_channels, tv_stations)
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
            try:
                wait_and_click(driver, (By.XPATH, "//div[@class='icon' and contains(@data-title, '搜')]"))
            except:
                print("❌ 无法找到搜搜图标，尝试在当前页面搜索")
        
        # 等待iframe加载
        print("⏳ 等待页面加载...")
        time.sleep(5)
        
        # 尝试切换到iframe
        try:
            wait = WebDriverWait(driver, 20)
            iframe = wait.until(EC.presence_of_element_located((By.ID, "browser")))
            driver.switch_to.frame(iframe)
            print("✅ 成功切换到搜搜页面")
            time.sleep(3)
        except:
            print("⚠️  无法切换到iframe，尝试在当前页面搜索")
        
        # 第三步：抓取所有电信/联通页面的频道数据
        telecom_buttons = ["北京电信", "广东电信", "陕西电信", "云南电信", "安徽电信", "江苏电信", "浙江电信"]
        
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
                
                # 提取有效频道
                channels_from_page = extract_valid_channels(current_text)
                
                if channels_from_page:
                    # 过滤出CCTV和卫视频道
                    cctv_from_page = filter_channels_by_type(channels_from_page, all_cctv_names)
                    tv_from_page = filter_channels_by_type(channels_from_page, tv_stations)
                    
                    if cctv_from_page:
                        collected_channels.extend(cctv_from_page)
                        print(f"  ✅ 找到 {len(cctv_from_page)} 个CCTV频道")
                    
                    if tv_from_page:
                        collected_channels.extend(tv_from_page)
                        print(f"  ✅ 找到 {len(tv_from_page)} 个卫视频道")
                else:
                    print(f"  ⚠️  未在 {button_name} 中找到有效频道")
                
                # 尝试返回
                try:
                    driver.execute_script("window.history.back();")
                except:
                    pass
                
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ 处理 {button_name} 时出错: {e}")
                continue
        
        # 第四步：添加苏州地方台
        print("📡 添加苏州地方台...")
        suzhou_channels = get_suzhou_channels()
        
        # 第五步：保存结果
        save_results(collected_channels, output_path, workspace_root, cctv_channels, tv_stations)
    
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        
        # 出错时保存当前已收集的数据
        save_results(collected_channels, output_path, workspace_root, cctv_channels, tv_stations)
        
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

def save_results(collected_channels, output_path, workspace_root, cctv_channels, tv_stations):
    """保存结果到文件"""
    # 去重
    unique_channels = remove_duplicate_channels(collected_channels)
    
    # 组织输出内容
    output_content = "# ====== CCTV频道 ======\n"
    
    # 收集CCTV频道
    cctv_found = []
    other_channels = []
    
    for channel in unique_channels:
        name = channel.split(',', 1)[0].strip()
        # 检查是否是CCTV频道
        is_cctv = False
        for cctv in cctv_channels:
            if cctv[0].lower() in name.lower() or cctv[1].lower() in name.lower():
                cctv_found.append(channel)
                is_cctv = True
                break
        
        if not is_cctv:
            other_channels.append(channel)
    
    # 添加CCTV频道
    for i, (cctv_num, cctv_name) in enumerate(cctv_channels):
        found = False
        for channel in cctv_found:
            if cctv_num.lower() in channel.lower() or cctv_name.lower() in channel.lower():
                output_content += channel + "\n"
                found = True
                break
        
        # 如果没有找到该CCTV频道，添加占位符（但不写"待更新源"）
        if not found:
            output_content += f"{cctv_name},# 等待抓取有效源\n"
    
    # 添加卫视频道
    output_content += "\n# ====== 卫视频道 ======\n"
    
    tv_found = []
    other_channels_filtered = []
    
    for channel in other_channels:
        name = channel.split(',', 1)[0].strip()
        is_tv = any(tv.lower() in name.lower() for tv in tv_stations)
        if is_tv:
            tv_found.append(channel)
        else:
            other_channels_filtered.append(channel)
    
    # 按卫视列表顺序添加
    for tv in tv_stations:
        found = False
        for channel in tv_found:
            if tv.lower() in channel.lower():
                output_content += channel + "\n"
                found = True
                break
        
        if not found:
            output_content += f"{tv},# 等待抓取有效源\n"
    
    # 添加其他频道（如果有）
    if other_channels_filtered:
        output_content += "\n# ====== 其他频道 ======\n"
        output_content += "\n".join(other_channels_filtered) + "\n"
    
    # 添加苏州地方台
    output_content += "\n# ====== 苏州地方台 ======\n"
    suzhou_channels = get_suzhou_channels()
    output_content += "\n".join(suzhou_channels) + "\n"
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_content)
    
    # 统计信息
    line_count = len(output_content.strip().split('\n'))
    
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
    print("\n📋 文件预览（前20行）:")
    print("-" * 50)
    lines = output_content.strip().split('\n')[:20]
    for i, line in enumerate(lines, 1):
        print(f"{i:2}: {line}")
    print("-" * 50)
    
    # 同时保存一份到当前脚本目录，便于调试
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir_output = os.path.join(script_dir, "zbhb1-pl10000.txt")
    with open(script_dir_output, "w", encoding="utf-8") as f:
        f.write(output_content)
    print(f"📝 备份文件已保存到脚本目录: {script_dir_output}")

if __name__ == "__main__":
    main()
