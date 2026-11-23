from lxml import etree
import requests,time,random,os
from DrissionPage import ChromiumPage,ChromiumOptions

co = ChromiumOptions().headless() 
page = ChromiumPage(co)

page.get("https://jhsjk.people.cn/")
time.sleep(2)
page.ele('xpath://input[@type="text"]').input("奋力谱写中国式现代化")
time.sleep(1)
page.ele('xpath://div[@class="submitBtnJing newBtnFuzzy active"]').click()
time.sleep(3)
real_ua = page.user_agent
page.quit

myheaders = {
    "User-Agent":real_ua,
}

allurls = []
while True:
    # 1. 接收输入，并用 strip() 去掉两端多余的空格和用户误输入的回车
    user_path = input("请输入保存文件夹的绝对路径（例如 D:\\我的文章）：").strip()
    
    # 2. 清洗：去掉 Windows 复制路径时自带的双引号
    user_path = user_path.strip('"').strip("'")
    
    # 3. 判断是否为空
    if not user_path:
        print("❌ 路径不能为空，请重新输入！")
        continue
        
    # 4. 判断路径是否存在，不存在则自动创建
    if not os.path.exists(user_path):
        try:
            os.makedirs(user_path, exist_ok=True)
            print(f"✅ 文件夹不存在，已自动创建：{user_path}")
        except Exception as e:
            print(f"❌ 无法创建该文件夹（可能是权限不足或路径非法）：{e}")
            continue # 创建失败，要求重新输入
            
    # 5. 验证该路径确实是文件夹（而不是一个文件）
    if not os.path.isdir(user_path):
        print("❌ 输入的路径是一个文件，请提供文件夹路径！")
        continue
        
    print(f"🎉 保存路径已设置为：{user_path}")
    break # 验证通过，跳出循环


for i in range(1,4):
    mourl = f"https://jhsjk.people.cn/testnew/result?keywords=%E5%A5%8B%E5%8A%9B%E8%B0%B1%E5%86%99%E4%B8%AD%E5%9B%BD%E5%BC%8F%E7%8E%B0%E4%BB%A3%E5%8C%96&isFuzzy=0&searchArea=0&year=0&form=0&type=0&page={i}&sortType=2&origin=%E5%85%A8%E9%83%A8&source=2"
    mourtext = requests.get(url = mourl,headers = myheaders)

    modata = mourtext.json()
    urls = modata['list']
    for i in urls:
        k = i['article_id']
        url = "https://jhsjk.people.cn/article/" + k
        #print(url)
        allurls.append(url)

record = 0


for j in allurls:
    response = requests.get(url = j,headers = myheaders)
    sondata = etree.HTML(response.text)
    t = random.randint(1,5)
    record += 1
    time.sleep(t)

    try:
        smalltitle = sondata.xpath(
            '//div[@class="d2txt clearfix"]/h2[@class="jian"]//text() | '
            '//div[@class="d2txt clearfix"]/h2[@class="jian"]/following-sibling::p[1]/text()'
        )[0]
    except:
        print(f"第{record}次提取主标题出错")
    try:
        bigtitle = sondata.xpath('//div[@class="d2txt clearfix"]/h1/text()')[0]
    except:
        print(f"第{record}次提取副标题出错")
    try:
        sontime0 = sondata.xpath('//div[@class="d2txt_1 clearfix"][contains(text(), "来源")]/text()')
        if sontime0:
            # 取出第一个结果，并把 \xa0 替换成普通空格
            sontime = sontime0[0].replace('\xa0', ' ').strip()
    except:
        print(f"第{record}次提取时间出错")
    try:
        zhengwen = sondata.xpath('//div[@class="d2txt_con clearfix"]/p//text()')
    except:
        print(f"第{record}次提取正文出错")
    
    with open(rf"{user_path}\{smalltitle}.txt",'a',encoding = 'utf-8') as f:
        f.write(smalltitle+'\n')
        f.write(bigtitle+'\n')
        f.write(sontime+'\n')
    for i in zhengwen:
        if "新华社记者" in i or "摄" in i: # 过滤图片说明
            continue
        with open(rf"{user_path}\{smalltitle}.txt",'a',encoding = 'utf-8') as f:
            f.write(i+'\n')

