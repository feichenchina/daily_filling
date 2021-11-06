from configparser import ConfigParser
import json,schedule
import datetime
import requests
from helium import *
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
class TB():
    def __init__(self,path):
        self.path = path
        self.ReadConf()
        # self.chrome_options = Options()
        # self.chrome_options.add_argument('--headless')

    def ReadConf(self):
        cf = ConfigParser()
        cf.read(self.path,encoding="utf-8")
        self.password = cf.get("JC", "password")
        self.chromeDriverPath = cf.get("JC", "chromedriver")
        self.url = cf.get("JC", "url")
        self.dd = cf.get("JC", "dd")
        self.time = cf.get("TIME", "run")
        message = cf.get("TB", "message")
        message = json.loads(message)
        self.message = list(map(self.DealMessage,message))
        print(self.message)

    def DealMessage(self,x):
        x["add"] = x.get("add") if x.get("add") else "金水区"
        x["mes"] = x.get("mes") if x.get("mes") else "已接种第一针"
        return x

    def run(self):
        for i in self.message:
            driver = webdriver.Chrome(executable_path = self.chromeDriverPath)
            driver.get(self.url)
            set_driver(driver)
            try:
                write(self.password,"请输入密码")
                click("确定")
                phone = S("#root > div > div > div.form-content > div > div.fx-form.has-footer > div.widget-wrapper > div:nth-child(1) > div:nth-child(5) > div.field-component > div > div > input")
                print("1",phone.exists,phone)
                wait_until(phone.exists,10,0.5)
                print(phone.exists(),phone)
                click(phone)
                element_phone = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[1]/div/div[2]/div[1]/div[1]/div[5]/div[3]/div[1]/div/input')
                write(i.get("tel"),element_phone)
                click("点击自动匹配")
                click("手动选择")
                click("请选择地址")
                write(i.get("add"),"搜索")
                click("河南省/郑州市")
                # click(i.get("mes"))
                click(Text("否",below="现在是否在京（含北三县）？"))
                time.sleep(2)
                click(Text("否",below="是否属于离京情况？"))
                time.sleep(1)
                click("提交")
                time.sleep(1)
                start_time = time.time()
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                msg = f"填报于 {local_time} 失败，请检查程序"
                while True:
                    end_time = time.time()
                    ex = ""
                    try:
                        ex = driver.find_element_by_xpath("//div[@class='x-msg-toast-container top-right']/div").text
                    except Exception as e:
                        print("找元素出现问题")
                    if end_time - start_time >= 10:
                        break
                    if Text("提交成功").exists():
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        msg = f"填报于 {local_time} 成功执行"
                        break
                    if Text("此项内容已存在").exists():
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        msg = f"填报于 {local_time} 重复执行"
                        break
                    if ex:
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        msg = f"填报于 {local_time} 重复执行,消息提示为：参数错误请刷新页面或今日已填报！"
                        break
                    if Text("今日已填报").exists():
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        msg = f"填报于 {local_time} 重复执行"
                        break
                    if Text("请填写").exists():
                        print("进入")
                        exist = driver.find_element_by_xpath('//div[@class="field-invalid-info"]/../../div[1]').text
                        print("判断文本:", exist)
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        msg = f"填报于 {local_time} ，参数  {exist}  未填写"
                        break
                    time.sleep(0.5)
            except Exception as e:
                print("判断发生异常",e)
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                msg = f"填报于 {local_time} 失败，请检查程序"
            print(msg)
            driver.close()
            self.send_msg(i.get("tel"),msg)

    def send_msg(self,phone,msg):
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        data = {
            "msgtype": "text",
            "text": {
                "content": msg + '\n'
            },
            "at": {
                "atMobiles": [
                    phone
                ],
                "isAtAll": False
            }
        }
        print(self.dd)
        r = requests.post(self.dd, data=json.dumps(data), headers=headers)
        return r.text

def conf(path):
    cf1 = ConfigParser()
    cf1.read(path, encoding="utf-8")
    time_res = cf1.get("TIME", "run")
    return time_res

def job():
    print('Job5:每隔5秒到10秒执行一次，每次执行3秒')
    print('Job5-startTime:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    time.sleep(3)
    print('Job5-endTime:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print('------------------------------------------------------------------------')
    path = "Tb.conf"
    tb = TB(path)
    tb.run()


if __name__ == '__main__':
    # path = "Tb.conf"
    # tb = TB(path)
    # tb.run()
    path = "Tb.conf"
    time_res = conf(path)
    job = schedule.every().day.at(time_res).do(job)
    while True:
        schedule.run_pending()
        time.sleep(5)
        name = copy(time_res)
        time_res = conf(path)
        print(name,time_res)
        if (name != time_res):
            print("进入取消行列")
            schedule.cancel_job(job)
        all_jobs = schedule.get_jobs()
        print(all_jobs)
        if not len(all_jobs):
            break
    pwd = os.getcwd()
    os.system(f"cd {pwd} && python mrtb.py")

