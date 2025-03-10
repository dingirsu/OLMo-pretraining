import os
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def download_file(url, base_dir="/ssd/data/weijia/olmo/data", retries=3):
    """下载单个文件并保持目录结构"""
    try:
        parsed = urlparse(url)
        path = parsed.path.lstrip('/')
        local_path = os.path.join(base_dir, path)
        
        # 创建目标目录
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # 如果文件已存在则跳过
        if os.path.exists(local_path):
            return True, url, "Already exists"
            
        # 下载文件
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # 写入文件
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True, url, "Success"
        
    except Exception as e:
        if retries > 0:
            return download_file(url, base_dir, retries-1)
        return False, url, str(e)

def batch_download(urls_file, max_workers=20):
    """批量下载"""
    with open(urls_file) as f:
        urls = [line.strip() for line in f if line.strip()]
        
    print(f"Total files to download: {len(urls)}")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_file, url): url for url in urls}
        
        successes = 0
        errors = []
        
        # 使用tqdm显示进度条
        with tqdm(total=len(urls), desc="Downloading") as pbar:
            for future in as_completed(futures):
                success, url, msg = future.result()
                if success:
                    successes += 1
                else:
                    errors.append((url, msg))
                pbar.update(1)
                
        print(f"\nDownload complete. Success: {successes}/{len(urls)}")
        if errors:
            print("\nFailed downloads:")
            for url, error in errors[:10]:  # 最多显示10个错误
                print(f"{url} - {error}")

if __name__ == "__main__":
    # 使用说明
    urls_file = "data_urls.txt"  # 包含所有下载链接的文本文件
    batch_download(urls_file)
