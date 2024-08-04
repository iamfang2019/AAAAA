# -*- coding:utf-8 -*-
import threading
import requests
from pypinyin import lazy_pinyin
import re
import os
from opencc import OpenCC
from tqdm import tqdm

# 使用requests.get下载响应体来检查URL的有效性
def checker(url):
    try:
        response = requests.get(url, timeout=0.2)
        if response.status_code == 200 and response.content:
            return True
    except:
        pass
    return False

# 读取文本文件中的频道信息，忽略空格、空行和格式错误的行
def read_channels_from_file(file_path):
    channels = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line and ',' in stripped_line:  # 确保行不为空且包含逗号分隔
                channels.append(stripped_line)
    return channels

# 检查频道的可用性并将结果保存到文件
def check_and_save_channel_availability(channel, output_file_path):
    try:
        parts = channel.split(',', 1)
        if len(parts) == 2:
            name, url = parts
            if checker(url):
                with open(output_file_path, 'a', encoding='utf-8') as output_file:
                    output_file.write(f"{name}, {url}\n")
    except Exception as e:
        print(f"Error processing channel {channel}: {e}")

# 多线程工作函数
def worker(channel, output_file_path):
    check_and_save_channel_availability(channel, output_file_path)

# 主函数
def main(input_file_path, output_file_path):
    channels = read_channels_from_file(input_file_path)
    threads = []

    # 创建并启动线程
    for channel in channels:
        thread = threading.Thread(target=worker, args=(channel, output_file_path))
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    input_file_path = 'IPTV/汇总.txt'  # 指定输入文件路径
    output_file_path = '2.txt'  # 指定输出文件路径
    main(input_file_path, output_file_path)



########################################################################################################################################################################################
#################文本排序
file_path = '2.txt'  # 定义文件路径
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()
# 定义一个函数，用于提取每行的第一个数字
def extract_first_number(line):
    match = re.search(r'\d+', line)
    return int(match.group()) if match else float('inf')
# 对列表中的行进行排序
# 按照第一个数字的大小排列，如果不存在数字则按中文拼音排序
sorted_lines = sorted(lines, key=lambda x: (not 'CCTV' in x, extract_first_number(x) if 'CCTV' in x else lazy_pinyin(x.strip())))
# 将排序后的行写入新的utf-8编码的文本文件，文件名基于原文件名
output_file_path = "sorted_" + os.path.basename(file_path)
# 写入新文件
with open('2.txt', "w", encoding="utf-8") as file:
    for line in sorted_lines:
        file.write(line)
print(f"文件已排序并保存为: {output_file_path}")
########################################################################################################################################################################################
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
check_and_write_file('2.txt',  'a0.txt',  keywords="央视频道, 8K, 4K, 4k")
check_and_write_file('2.txt',  'a.txt',  keywords="央视频道, CCTV, 8K, 4K, 爱上4K, 纯享, 风云剧场, 怀旧剧场, 影迷, 高清电影, 动作电影, 第一剧场, 家庭影院, 影迷电影, 星光, 华语, 峨眉")
check_and_write_file('2.txt',  'a1.txt',  keywords="央视频道, 文物宝库, 风云音乐, 生活时尚, 台球, 网球, 足球, 女性, 地理, 纪实科教, 纪实人文, 兵器, 北京纪实, 发现, 法治")

check_and_write_file('2.txt',  'b.txt',  keywords="卫视频道, 卫视, 凤凰， 星空")

check_and_write_file('2.txt',  'c.txt',  keywords="影视频道, 爱情喜剧, 爱喜喜剧, 电影, 惊嫊悬疑, 东北热剧, 无名, 都市剧场, iHOT, 剧场, 欢笑剧场, 重温经典, 明星大片, 中国功夫, 军旅, 东北热剧, 中国功夫, 军旅剧场, 古装剧场, \
家庭剧场, 惊悚悬疑, 欢乐剧场, 潮妈辣婆, 爱情喜剧, 精品大剧, 超级影视, 超级电影, 黑莓动画, 黑莓电影, 海外剧场, 精彩影视, 无名影视, 潮婆辣妈, 超级剧, 热播精选")
check_and_write_file('2.txt',  'c1.txt',  keywords="影视频道, 求索动物, 求索, 求索科学, 求索记录, 爱谍战, 爱动漫, 爱科幻, 爱青春, 爱自然, 爱科学, 爱浪漫, 爱历史, 爱旅行, 爱奇谈, 爱怀旧, 爱赛车, 爱都市, 爱体育, 爱经典, \
爱玩具, 爱喜剧, 爱悬疑, 爱幼教, 爱院线")
check_and_write_file('2.txt',  'c2.txt',  keywords="影视频道, 军事评论, 农业致富, 哒啵赛事, 怡伴健康, 武博世界, 超级综艺, 哒啵, HOT, 炫舞未来, 精品体育, 精品萌宠, 精品记录, 超级体育, 金牌, 武术世界, 精品纪录")

check_and_write_file('2.txt',  'd.txt',  keywords="少儿频道, 少儿, 卡通, 动漫, 宝贝, 哈哈")

check_and_write_file('2.txt',  'e.txt',  keywords="港澳频道, TVB, 澳门, 龙华, 民视, 中视, 华视, AXN, MOMO, 采昌, 耀才, 靖天, 镜新闻, 靖洋, 莲花, 年代, 爱尔达, 好莱坞, 华丽, 非凡, 公视, 寰宇, 无线, EVEN, MoMo, 爆谷, 面包, momo, 唐人, \
中华小, 三立, CNA, FOX, RTHK, Movie, 八大, 中天, 中视, 东森, 凤凰, 酒店, 天映, 美亚, 环球, 翡翠, 亚洲, 大爱, 大愛, 明珠, 半岛, AMC, 龙祥, 台视, 1905, 纬来, 神话, 经典都市, 视界, 番薯, 私人, 酒店, TVB, 凤凰, 半岛, 星光视界, \
番薯, 大愛, 新加坡, 星河, 明珠, 环球, 翡翠台")

check_and_write_file('2.txt',  'f0.txt',  keywords="省市频道, 湖北, 武汉")
check_and_write_file('2.txt',  'f.txt',  keywords="省市频道, 松滋, 十堰, 咸宁, 远安, 崇阳, 黄石, 荆州, 当阳, 恩施, 五峰, 来凤, 枝江, 黄冈, 随州, 荆门, 秭归, 孝感, 鄂州, 垄上, 宜都")

check_and_write_file('2.txt',  'f1.txt',  keywords="浙江频道, 浙江, 杭州, 宁波, 平湖, 庆元, 缙云, 嵊, 义乌, 东阳, 文成, 云和, 象山, 衢江, 萧山, 龙游, 武义, 兰溪, 开化, 丽水, 上虞, NBTV, 舟山, 新密, 衢州, 嘉兴, 绍兴, 温州, \
湖州, 永嘉, 诸暨, 钱江, 松阳, 苍南, 遂昌, 青田, 龙泉, 余杭, 新昌, 杭州, 余杭, 丽水, 龙泉, 青田, 松阳, 遂昌, 宁波, 余姚, 上虞, 新商都, 绍兴, 温州, 永嘉, 诸暨, 钱江, 金华, 苍南, 临平")

###############################################################################################################################################################################################################################
##############################################################对生成的文件进行合并
file_contents = []
file_paths = ["a0.txt", "a.txt", "a1.txt", "b.txt", "c.txt", "c1.txt", "c2.txt", "d.txt", "f0.txt", "f.txt", "f1.txt", "e.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            file_contents.append(content)
    else:                # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file_path} 不存在，跳过")
# 写入合并后的文件
with open("去重.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))
###############################################################################################################################################################################################################################

# 打开文档并读取所有行 
with open('去重.txt', 'r', encoding="utf-8") as file:
 lines = file.readlines()
 
# 使用列表来存储唯一的行的顺序 
 unique_lines = [] 
 seen_lines = set() 
# 遍历每一行，如果是新的就加入unique_lines 
for line in lines:
 if line not in seen_lines:
  unique_lines.append(line)
  seen_lines.add(line)
# 将唯一的行写入新的文档 
with open('汇总.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)
################################################################################################任务结束，删除不必要的过程文件
files_to_remove = ['去重.txt', "2.txt", "e.txt", "a0.txt", "a.txt", "a1.txt", "b.txt", "c.txt", "c1.txt", "c2.txt", "d.txt", "f0.txt", "f.txt", "f1.txt", "o1.txt", "o.txt", "2.txt"]
for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
    else:              # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file} 不存在，跳过删除。")
print("任务运行完毕，汇总频道列表可查看文件夹内txt文件！")
