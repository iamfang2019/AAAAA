import requests

# 直播源URL列表文件路径
input_file_path = 'IPTV/汇总.txt'
# 输出结果文件路径
output_file_path = '汇总.txt'

def is_url_valid(url):
    try:
        response = requests.get(url, timeout=5)
        # 这里可以根据HTTP状态码或其他逻辑来确定URL是否有效
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_live_sources(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        # 写入标题到输出文件
        outfile.write("URL,Status\n")

        for line in infile:
            url = line.strip()  # 移除可能的空白字符
            if url:  # 确保URL不为空
                valid = is_url_valid(url)
                # 写入结果到输出文件
                outfile.write(f"{url},{'有效' if valid else '无效'}\n")

# 调用函数执行检测
check_live_sources(input_file_path, output_file_path)
