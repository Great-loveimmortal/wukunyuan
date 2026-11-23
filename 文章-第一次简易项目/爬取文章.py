import requests,time,random
from lxml import etree
import os
import re

def check_folder_path(path_str):
    """
    校验文件夹地址是否合法可用
    返回: (是否通过校验(bool), 提示信息(str))
    """
    # 1. 基础格式校验：是否为空
    if not path_str or not path_str.strip():
        return False, "路径不能为空！"
    
    path_str = path_str.strip()

    # 2. 格式校验：检查是否包含 Windows 或 Linux 不允许的非法字符
    # Windows 文件夹名称禁止包含: \ / : * ? " < > |
    # 注意：这里针对的是 Windows 环境，如果跨平台可以稍微放宽
    invalid_chars = r'[<>:"|?*]'
    # 把盘符的冒号排除掉，比如 C:\ 是合法的
    path_to_check = re.sub(r'^[a-zA-Z]:', '', path_str) 
    
    if re.search(invalid_chars, path_to_check):
        return False, f"路径包含非法字符: {re.findall(invalid_chars, path_to_check)}"

    # 3. 判断路径是否存在
    if not os.path.exists(path_str):
        return False, "该文件夹路径不存在！"

    # 4. 判断该路径是否是文件夹（而不是一个文件）
    if not os.path.isdir(path_str):
        return False, "输入的路径是一个文件，而不是文件夹！"

    # 5. 判断是否有读取权限（尝试列出里面的文件）
    try:
        os.listdir(path_str)
    except PermissionError:
        return False, "没有读取该文件夹的权限！"

    # 6. 判断是否有写入权限（尝试创建一个临时文件并删除）
    test_file = os.path.join(path_str, ".test_write_permission.tmp")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file) # 测试成功后删掉它
    except PermissionError:
        return False, "没有写入该文件夹的权限！"
    except Exception as e:
        return False, f"写入测试失败: {e}"

    # 所有校验通过
    return True, "路径合法且可用！"

while True:
    test_path = input("请输入需要保存的文件夹地址：")
    
    is_valid, msg = check_folder_path(test_path)
    
    if is_valid:
        print(f"✅ 校验通过: {msg}")
        break
    else:
        print(f"❌ 校验失败: {msg}")
        continue

myheaders = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0",
}

#etree.tostring()解析网页源码，防止因浏览器和lxml纠正产生的误差；用following-sibling抓取兄弟节点
print("为避免被网站检测到是爬虫程序，下载时间较久，请耐心等待。")

while True:
    choices = input("输入1开始第一阶段下载，输入2开始第二阶段下载，输入3退出程序：")
    match choices:
        case "1":
            print("开始下载")
            mourl = "https://jhsjk.people.cn/testnew/result?keywords=%E5%A5%8B%E5%8A%9B%E8%B0%B1%E5%86%99%E4%B8%AD%E5%9B%BD%E5%BC%8F%E7%8E%B0%E4%BB%A3%E5%8C%96&isFuzzy=0&searchArea=0&year=0&form=0&type=0&page=1&sortType=2&origin=%E5%85%A8%E9%83%A8&source=2"
            mourtext = requests.get(url = mourl,headers = myheaders)

            modata = etree.HTML(mourtext.text)
            sonurls = modata.xpath('//ul[@id="news_list"]//a/@href')

            for url in sonurls[3:]:
     
                sonurl = "https://jhsjk.people.cn/" + url
                response = requests.get(url = sonurl,headers = myheaders)
                sondata = etree.HTML(response.text)

                smalltitle = sondata.xpath(
                    '//div[@class="d2txt clearfix"]/h2[@class="jian"]//text() | '
                    '//div[@class="d2txt clearfix"]/h2[@class="jian"]/following-sibling::p[1]/text()'
                )[0]
                bigtitle = sondata.xpath('//div[@class="d2txt clearfix"]/h1/text()')[0]
    
                sontime0 = sondata.xpath('//div[@class="d2txt_1 clearfix"][contains(text(), "来源")]/text()')
                if sontime0:
    # 取出第一个结果，并把 \xa0 替换成普通空格
                    sontime = sontime0[0].replace('\xa0', ' ').strip()
                zhengwen = sondata.xpath('//div[@class="d2txt_con clearfix"]/p//text()')
                with open(rf"{test_path}\{smalltitle}.txt",'a',encoding = 'utf-8') as f:
                    f.write(smalltitle+'\n')
                    f.write(bigtitle+'\n')
                    f.write(sontime+'\n')
                for i in zhengwen:
                    if "新华社记者" in i or "摄" in i: # 过滤图片说明
                        continue
                    with open(rf"{test_path}\{smalltitle}.txt",'a',encoding = 'utf-8') as f:
                        f.write(i+'\n')
                time.sleep(random.randint(1,9))
                print("下载完成")
        case "2":
            print("开始下载")
            for i in range(1,3):
                mourl = "https://jhsjk.people.cn/testnew/result?keywords=%E5%A5%8B%E5%8A%9B%E8%B0%B1%E5%86%99%E4%B8%AD%E5%9B%BD%E5%BC%8F%E7%8E%B0%E4%BB%A3%E5%8C%96&isFuzzy=0&searchArea=0&year=0&form=0&type=0&page=" + "i" + "&sortType=2&origin=%E5%85%A8%E9%83%A8&source=2"
                mourtext = requests.get(url = mourl,headers = myheaders)

                modata = etree.HTML(mourtext.text)
                sonurls = modata.xpath('//ul[@id="news_list"]//a/@href')

                for url in sonurls:
     
                    sonurl = "https://jhsjk.people.cn/" + url
                    response = requests.get(url = sonurl,headers = myheaders)
                    sondata = etree.HTML(response.text)

                    smalltitle = sondata.xpath(
                        '//div[@class="d2txt clearfix"]/h2[@class="jian"]//text() | '
                        '//div[@class="d2txt clearfix"]/h2[@class="jian"]/following-sibling::p[1]/text()'
                    )[0]
                    bigtitle = sondata.xpath('//div[@class="d2txt clearfix"]/h1/text()')[0]
    
                    sontime0 = sondata.xpath('//div[@class="d2txt_1 clearfix"][contains(text(), "来源")]/text()')
                    if sontime0:
    # 取出第一个结果，并把 \xa0 替换成普通空格
                        sontime = sontime0[0].replace('\xa0', ' ').strip()
                    zhengwen = sondata.xpath('//div[@class="d2txt_con clearfix"]/p//text()')
                    with open(rf"{test_path}\{smalltitle}.txt",'a',encoding = 'utf-8') as f:
                        f.write(smalltitle+'\n')
                        f.write(bigtitle+'\n')
                        f.write(sontime+'\n')
                    for i in zhengwen:
                        if "新华社记者" in i or "摄" in i: # 过滤图片说明
                            continue
                        with open(rf"{test_path}\{smalltitle}.txt",'a',encoding = 'utf-8') as f:
                            f.write(i+'\n')
                    time.sleep(random.randint(1,9))
                    print("下载完成")
        case "3":
            break
        case _:
            print("系统错误QAQ")