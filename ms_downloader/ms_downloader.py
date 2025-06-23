import argparse
import os
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pypdl import Pypdl
from rich.logging import RichHandler
import logging

# 禁用 SSL 警告
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    # 如果导入失败，忽略警告禁用
    pass

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("mindspore_download")

# 基础 URL
BASE_URL = "https://repo.mindspore.cn/mindspore/mindspore/version/"

def generate_dates(start_date, end_date):
    """生成指定日期范围内的日期列表"""
    try:
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime("%Y%m%d"))
            current += timedelta(days=1)
        logger.info(f"生成 {len(dates)} 个日期，从 {start_date} 到 {end_date}")
        return dates
    except ValueError as e:
        logger.error(f"日期格式错误，必须为 YYYYMMDD: {e}")
        return []

def get_master_builds(date):
    """获取某日期下 master 分支的构建包目录"""
    yyyy_mm = date[:6]  # 提取 YYYYMM
    url = f"{BASE_URL}{yyyy_mm}/{date}/"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', id='list')
        if not table:
            logger.warning(f"{date} 未找到构建列表")
            return []
        
        builds = []
        for row in table.find('tbody').find_all('tr'):
            link = row.find('a')
            if link and link['href'].startswith('master_') and link['href'].endswith('_newest/'):
                builds.append(link['href'])
        logger.info(f"{date} 找到 {len(builds)} 个 master 分支构建")
        return builds
    except Exception as e:
        logger.error(f"获取 {date} 的构建失败: {e}")
        return []

def parse_file_size(size_text):
    """解析文件大小文本为字节数"""
    if not size_text or size_text == '-':
        return None
    
    size_text = size_text.strip()
    
    # 处理不同的单位
    units = {
        'B': 1,
        'KiB': 1024,
        'MiB': 1024**2,
        'GiB': 1024**3,
        'KB': 1000,
        'MB': 1000**2,
        'GB': 1000**3
    }
    
    for unit, multiplier in units.items():
        if size_text.endswith(unit):
            try:
                size_value = float(size_text[:-len(unit)].strip())
                return int(size_value * multiplier)
            except ValueError:
                continue
    
    # 如果没有单位，假设是字节
    try:
        return int(float(size_text))
    except ValueError:
        logger.warning(f"无法解析文件大小: {size_text}")
        return None

def get_download_links(date, build, python_version=None):
    """获取构建包目录下的下载链接和文件大小，可根据 Python 版本过滤"""
    yyyy_mm = date[:6]
    build_url = f"{BASE_URL}{yyyy_mm}/{date}/{build}unified/aarch64/"
    try:
        response = requests.get(build_url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', id='list')
        if not table:
            logger.warning(f"{build} 未找到文件列表")
            return []
        
        links_with_sizes = []
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 3:  # 确保有足够的列
                # 根据实际的HTML结构，第1列是文件链接，第2列是大小，第3列是日期
                link_cell = cells[0]  # 第1列是链接
                size_cell = cells[1]  # 第2列是大小
                
                link = link_cell.find('a')
                if link and link['href'].endswith('.whl'):
                    full_url = f"{build_url}{link['href']}"
                    if python_version and f"-{python_version}-" not in link['href']:
                        continue
                    
                    # 获取文件大小
                    size_text = size_cell.get_text(strip=True) if size_cell else None
                    file_size = parse_file_size(size_text)
                    
                    links_with_sizes.append((full_url, file_size))
                    logger.debug(f"找到文件: {link['href']}, 大小: {size_text} ({file_size} bytes)")
        
        logger.info(f"{build} 找到 {len(links_with_sizes)} 个 .whl 文件")
        return links_with_sizes
    except Exception as e:
        logger.error(f"获取 {build} 的下载链接失败: {e}")
        return []

def download_with_pypdl(urls_info, download_dir, max_workers):
    """使用 pypdl 并行下载文件"""
    # 准备下载任务
    os.makedirs(download_dir, exist_ok=True)
    
    # 创建 pypdl 下载器，启用重用模式进行并发下载
    dl = Pypdl(allow_reuse=True, max_concurrent=max_workers)
    
    # 准备任务列表
    tasks = []
    for url, date, build, size in urls_info:
        filename = url.split('/')[-1]
        build_dir = os.path.join(download_dir, date, build.strip('/'))
        os.makedirs(build_dir, exist_ok=True)
        save_path = os.path.join(build_dir, filename)
        
        # 添加任务到下载列表
        task = {
            'url': url,
            'file_path': save_path,
            'multisegment': True,
            'segments': 5,
            'retries': 3,
            'overwrite': True,
            'speed_limit': 0,  # 无速度限制
            'etag_validation': True,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': url.rsplit('/', 1)[0] + '/',
            }
        }
        tasks.append(task)
        logger.info(f"准备下载: {filename}")
    
    if not tasks:
        logger.warning("没有文件需要下载")
        return
    
    try:
        # 使用 pypdl 进行批量下载
        logger.info(f"开始下载 {len(tasks)} 个文件，使用 {max_workers} 个并发连接...")
        results = dl.start(
            tasks=tasks,
            display=True,      # 显示进度条
            block=True,        # 阻塞等待完成
            clear_terminal=False  # 不清除终端
        )
        
        # 处理下载结果
        success_count = 0
        if results:
            for url, result in results:
                filename = url.split('/')[-1]
                if result is not None:
                    success_count += 1
                    logger.info(f"✓ 下载成功: {filename}")
                else:
                    logger.error(f"✗ 下载失败: {filename}")
        
        logger.info(f"下载完成: {success_count}/{len(tasks)} 个文件成功下载")
        
    except Exception as e:
        logger.error(f"下载过程中发生错误: {e}")
    finally:
        # 关闭下载器
        dl.shutdown()

def main():
    parser = argparse.ArgumentParser(description="下载 MindSpore master 分支构建包")
    parser.add_argument("--start_date", required=True, help="起始日期，格式为 YYYYMMDD")
    parser.add_argument("--end_date", required=True, help="结束日期，格式为 YYYYMMDD")
    parser.add_argument("--download_dir", default="downloads", help="下载目录")
    parser.add_argument("--num_process", type=int, default=3, help="并行线程数")
    parser.add_argument("--python_version", help="指定 Python 版本（如 cp39, cp310, cp311），默认下载所有版本")
    args = parser.parse_args()

    os.makedirs(args.download_dir, exist_ok=True)
    logger.info(f"下载目录: {args.download_dir}")
    
    dates = generate_dates(args.start_date, args.end_date)
    if not dates:
        logger.error("无有效日期，退出")
        return

    all_links = []
    for date in dates:
        builds = get_master_builds(date)
        for build in builds:
            links_with_sizes = get_download_links(date, build, args.python_version)
            # 将 (url, size) 转换为 (url, date, build, size) 格式
            for url, size in links_with_sizes:
                all_links.append((url, date, build, size))

    if not all_links:
        logger.warning("未找到任何可下载的 .whl 文件")
        return

    download_with_pypdl(all_links, args.download_dir, args.num_process)

    logger.info("所有下载任务完成")

if __name__ == "__main__":
    main()
