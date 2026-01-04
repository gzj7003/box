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

def extract_ip_data(text):
    """从页面文本中提取IP地址数据"""
    lines = text.strip().split('\n')
    ip_lines = []
    
    for line in lines:
        # 提取包含IP地址的行（格式如：xxx.xxx.xxx.xxx:xxxx）
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', line.strip()):
            ip_lines.append(line.strip())
        # 或者包含"rtp://"或"udp://"的行
        elif line.strip().startswith(('rtp://', 'udp://')):
            ip_lines.append(line.strip())
    
    return '\n'.join(ip_lines)

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
        telecom_buttons = ["北京电信", "广东电信", "天津电信", "湖北电信", "安徽电信", "江苏电信", "淅江电信"]
        all_data = ""
        
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
                
                # 提取IP数据
                ip_data = extract_ip_data(current_text)
                
                if ip_data:
                    all_data += f"# ====== {button_name} ======\n"
                    all_data += ip_data + "\n\n"
                    print(f"  ✅ 成功获取 {button_name} 数据")
                else:
                    # 如果没有提取到IP数据，保存原始文本的前500字符用于调试
                    all_data += f"# ====== {button_name} ======\n"
                    all_data += current_text[:500] + "\n\n"
                    print(f"  ⚠️  未提取到IP格式数据，保存原始文本")
                
                # 点击后可能需要返回或等待页面稳定
                # 尝试点击返回按钮或重新加载页面
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
                # 尝试其他选择器
                try:
                    # 尝试通过XPath查找包含按钮文本的元素
                    xpath_btn = driver.find_element(
                        By.XPATH, f"//*[contains(text(), '{button_name}')]"
                    )
                    xpath_btn.click()
                    time.sleep(3)
                    print(f"  ✅ 通过XPath找到并点击了 {button_name}")
                except:
                    print(f"  ❌ 无法找到 {button_name} 按钮")
                    continue
        
        # 第四步：保存数据到文件
        if all_data.strip():
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(all_data)
            
            # 统计行数
            line_count = len(all_data.strip().split('\n'))
            print(f"\n🎉 数据采集完成!")
            print(f"📊 共采集 {len(telecom_buttons)} 个地区的数据")
            print(f"📝 总行数: {line_count} 行")
            print(f"💾 文件已保存为: {output_path}")
            
            # 验证文件是否真的保存了
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ 文件确认存在，大小: {file_size} 字节")
            else:
                print("❌ 警告: 文件似乎没有成功保存")
            
            # 显示文件前10行预览
            print("\n📋 文件预览（前10行）:")
            print("-" * 50)
            lines = all_data.strip().split('\n')[:10]
            for line in lines:
                print(line)
            print("-" * 50)
            
            # 同时保存一份到当前脚本目录，便于调试
            script_dir_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
            with open(script_dir_output, "w", encoding="utf-8") as f:
                f.write(all_data)
            print(f"📝 备份文件已保存到脚本目录: {script_dir_output}")
        else:
            print("⚠️  未采集到任何数据，可能是页面结构已变更")
            
            # 保存页面源码用于调试
            debug_filename = "debug_page_source.html"
            debug_path = os.path.join(workspace_root, debug_filename)
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(page_source)
            print(f"🔍 已保存页面源码到 {debug_path} 用于调试")
    
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
