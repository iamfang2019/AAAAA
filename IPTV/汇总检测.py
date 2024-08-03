import requests

# 直播源URL列表文件路径
input_file_path = 'IPTV/汇总.txt'
# 输出结果文件路径
output_file_path = '汇总.txt'

def is_url_valid(url):
    try:
        response = requests.get(url, timeout=10)  # 增加超时时间到10秒
        # 检查2xx状态码，表示请求成功
        return 200 <= response.status_code < 300
    except requests.RequestException as e:
        print(f"请求失败: {url}, 错误: {e}")
        return False

def check_live_sources(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        outfile.write("URL,Status\n")
        for line in infile:
            url = line.strip()
            if url:
                valid = is_url_valid(url)
                status = '有效' if valid else '无效'
                outfile.write(f"{url},{status}\n")
                print(f"{url} - {status}")  # 打印当前检查的URL和状态

check_live_sources(input_file_path, output_file_path)
