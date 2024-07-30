import requests
from tqdm import tqdm
import cv2
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

#  获取远程港澳台直播源文件
url = "https://raw.githubusercontent.com/frxz751113/AAAAA/main/IPTV/TW.txt"          #源采集地址
r = requests.get(url)
open('TW.txt','wb').write(r.content)         #打开源文件并临时写入





# 函数：获取视频分辨率
def get_video_resolution(video_path, timeout=25):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return (width, height)

# 函数：处理每一行
def process_line(line, output_file, order_list, valid_count, invalid_count, total_lines):
    parts = line.strip().split(',')
    if '#genre#' in line:
        # 如果行包含 '#genre#'，直接写入新文件
        with threading.Lock():
            output_file.write(line)
            print(f"已写入genre行：{line.strip()}")
    elif len(parts) == 2:
        channel_name, channel_url = parts
        resolution = get_video_resolution(channel_url, timeout=5)
        if resolution and resolution[1] >= 720:  # 检查分辨率是否大于等于720p
            with threading.Lock():
                output_file.write(f"{channel_name}[{resolution[1]}p],{channel_url}\n")
                order_list.append((channel_name, resolution[1], channel_url))
                valid_count[0] += 1
                print(f"Channel '{channel_name}' accepted with resolution {resolution[1]}p at URL {channel_url}.")
        else:
            invalid_count[0] += 1
    with threading.Lock():
        print(f"有效: {valid_count[0]}, 无效: {invalid_count[0]}, 总数: {total_lines}, 进度: {(valid_count[0] + invalid_count[0]) / total_lines * 100:.2f}%")

# 函数：多线程工作
def worker(task_queue, output_file, order_list, valid_count, invalid_count, total_lines):
    while True:
        try:
            line = task_queue.get(timeout=1)
            process_line(line, output_file, order_list, valid_count, invalid_count, total_lines)
        except Queue.Empty:
            break
        finally:
            task_queue.task_done()

# 主函数
def main(source_file_path, output_file_path):
    order_list = []
    valid_count = [0]
    invalid_count = [0]
    task_queue = Queue()

    # 读取源文件
    with open(source_file_path, 'r', encoding='utf-8') as source_file:
        lines = source_file.readlines()

    with open(output_file_path + '.txt', 'w', encoding='utf-8') as output_file:
        # 创建线程池
        with ThreadPoolExecutor(max_workers=32) as executor:
            # 创建并启动工作线程
            for _ in range(4):
                executor.submit(worker, task_queue, output_file, order_list, valid_count, invalid_count, len(lines))

            # 将所有行放入队列
            for line in lines:
                task_queue.put(line)

            # 等待队列中的所有任务完成
            task_queue.join()

    print(f"任务完成，有效频道数：{valid_count[0]}, 无效频道数：{invalid_count[0]}, 总频道数：{len(lines)}")

if __name__ == "__main__":
    source_file_path = 'TW.txt'  # 替换为你的源文件路径
    output_file_path = 'TW'  # 替换为你的输出文件路径,不要后缀名
    main(source_file_path, output_file_path)

#######################################################################################################################################################################################
################################################################定义关键词分割规则
def check_and_write_file(input_file, output_file, keywords):
    # 使用 split(', ') 而不是 split(',') 来分割关键词
    keywords_list = keywords.split(', ')
    first_keyword = keywords_list[0]  # 获取第一个关键词作为头部信息

    pattern = '|'.join(re.escape(keyword) for keyword in keywords_list)
    extracted_lines = False

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write(f'{first_keyword},#genre#\n')  # 使用第一个关键词作为头部信息

        for line in lines:
            if 'genre' not in line and 'epg' not in line:
                if re.search(pattern, line):
                    out_file.write(line)
                    extracted_lines = True

    # 如果没有提取到任何关键词，则不保留输出文件
    if not extracted_lines:
        os.remove(output_file)  # 删除空的输出文件
        print(f"未提取到关键词，{output_file} 已被删除。")
    else:
        print(f"文件已提取关键词并保存为: {output_file}")

# 按类别提取关键词并写入文件
check_and_write_file('TW.txt',  'a0.txt',  keywords="港澳频道, 影, 剧, 戏")
check_and_write_file('TW.txt',  'a.txt',  keywords="港澳频道, ,")
##############################################################对生成的文件进行合并
file_contents = []
file_paths = ["a0.txt", "a.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            file_contents.append(content)
    else:                # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file_path} 不存在，跳过")
# 写入合并后的文件
with open("TW.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))

###############################################################################################################################################################################################################################

################################################################################################任务结束，删除不必要的过程文件
files_to_remove = ["a0.txt", "a.txt"]

for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
    else:              # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file} 不存在，跳过删除。")

print("任务运行完毕，分类频道列表可查看文件夹内综合源.txt文件！")



