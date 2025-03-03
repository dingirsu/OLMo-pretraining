import argparse
import os
import requests
import concurrent
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def download_file(url, output_dir, retries=3, timeout=10):
    """下载单个文件并保存到指定目录"""
    try:
        filename = os.path.basename(urlparse(url).path)
        save_path = os.path.join(output_dir, filename)
        
        for attempt in range(retries):
            try:
                with requests.get(url, stream=True, timeout=timeout) as r:
                    r.raise_for_status()
                    with open(save_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                print(f"Downloaded: {filename}")
                return True
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {filename}: {str(e)}")
                if attempt == retries - 1:
                    print(f"Failed to download {filename} after {retries} attempts")
                    return False
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='olmo2 traning data downloader')
    parser.add_argument('-i', '--input', required=True, help='urls')
    parser.add_argument('-o', '--output', default='downloads')
    parser.add_argument('-t', '--threads', type=int, default=20)
    
    args = parser.parse_args()

    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)

    # 读取URL列表
    with open(args.input) as f:
        urls = [line.strip() for line in f if line.strip()]

    # 使用线程池下载
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(download_file, url, args.output) for url in urls]
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ == "__main__":
    main()
