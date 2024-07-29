import requests
from tqdm import tqdm
import threading
import queue

# 打印开始信息
print("请注意，文件名不能有特殊符号，否则闪退\n\n请注意，文件名不能有特殊符号，否则闪退\n")
print("检测前请先过滤文本中的空格和mitv以及p2p等迅雷链接\n\n以免导致不可能的错误\n")
print("读取进度百分百后请静待进程完成\n\n完成后会有提示\n")

# 测试HTTP连接
def test_connectivity(url, max_attempts=10):
    for _ in range(max_attempts):
        try:
            response = requests.head(url, timeout=15)  # 发送HEAD请求，仅支持V4
            #response = requests.get(url, timeout=15)  # 发送get请求，支持V6
            return response.status_code == 200  # 返回True如果状态码为200
        except requests.RequestException:  # 捕获requests引发的异常
            pass  # 发生异常时忽略
    return False  # 如果所有尝试都失败，返回False

# 使用队列来收集结果的函数
def process_line(line, result_queue):
    parts = line.strip().split(",")  # 去除行首尾空白并按逗号分割
    if len(parts) == 2 and parts[1]:  # 确保有URL，并且URL不为空
        channel_name, channel_url = parts  # 分别赋值频道名称和URL
        if test_connectivity(channel_url):  # 测试URL是否有效
            result_queue.put((channel_name, channel_url, "有效"))  # 将结果放入队列
        else:
            result_queue.put((channel_name, channel_url, "无效"))  # 将结果放入队列

# 主函数
def main():
    with open('IPTV/TW.txt', "r", encoding="utf-8") as source_file:  # 打开源文件
        lines = source_file.readlines()  # 读取所有行

    result_queue = queue.Queue()  # 创建队列

    threads = []  # 初始化线程列表
    for line in tqdm(lines, desc="加载中,任务完成后会有提示"):  # 显示进度条
        thread = threading.Thread(target=process_line, args=(line, result_queue))  # 创建线程
        thread.start()  # 启动线程
        threads.append(thread)  # 将线程加入线程列表

    for thread in threads:  # 等待所有线程完成
        thread.join()

    # 初始化计数器
    valid_count = 0
    invalid_count = 0

    with open("TW.txt", "w", encoding="utf-8") as output_file:  # 打开输出文件
        for _ in range(result_queue.qsize()):  # 使用队列的大小来循环
            item = result_queue.get()  # 获取队列中的项目
            if item[0] and item[1]:  # 确保channel_name和channel_url都不为None
                output_file.write(f"{item[0]},{item[1]},{item[2]}\n")  # 写入文件
                if item[2] == "有效":
                    valid_count += 1
                else:
                    invalid_count += 1
    print(f"任务完成, 有效源数量: {valid_count}, 无效源数量: {invalid_count}")  # 打印结果

if __name__ == "__main__":
    main()

# 以下代码段是独立的，不需要缩进在main函数内
# 过滤文本函数
def filter_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    filtered_lines = [line for line in lines if 'genre' in line or '有效' in line]
    return filtered_lines

# 写入过滤后的行到新文件
def write_filtered_lines(output_file_path, filtered_lines):
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(filtered_lines)

# 替换规则函数
def replace_lines(file_path, replacements):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(file_path, 'w', encoding='utf-8') as new_file:
        for line in lines:
            for old, new in replacements.items():
                line = line.replace(old, new)
            new_file.write(line)

# 执行过滤和替换操作
input_file_path = "TW.txt"
output_file_path = "TW.txt"

filtered_lines = filter_lines(input_file_path)
write_filtered_lines(output_file_path, filtered_lines)

replacements = {
    ",有效": "",
    "#genre#,无效": "#genre#"
}
replace_lines(output_file_path, replacements)

print("新文件已保存。")
