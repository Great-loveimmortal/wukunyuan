from DrissionPage import ChromiumPage,ChromiumOptions
from lxml import etree
import time

#co = ChromiumOptions().headless()
page = ChromiumPage()

page.get("https://jhsjk.people.cn/")
time.sleep(2)
page.ele('xpath://input[@type="text"]').input("奋力谱写中国式现代化")
time.sleep(1)
page.ele('xpath://div[@class="submitBtnJing newBtnFuzzy active"]').click()
time.sleep(3)
#page.ele('#pages').eles('tag:span')[2].click()

if page.ele('tag:iframe'):
    print("页面有 iframe！")
    # 切换进 iframe 再找
    iframe = page.get_frame('tag:iframe') 
    print("iframe 源码：", iframe.html)
