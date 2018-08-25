from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from time import time
import re

def clock(t):
    hr=t//3600
    mn=(t//60)%60
    sec=t%60
    if hr>0: return '%.2dhr:%.2dmin:%.2dsec'%(hr,mn,sec)
    else:return '%.2dmin:%.2dsec'%(mn,sec)

def scroll(page):
    bot.find_element_by_tag_name('body').send_keys(Keys.END)
    bot.find_element_by_tag_name('body').send_keys(Keys.ARROW_UP)
    return page+1

def extract(page):
    global extracted
    page=scroll(page)
    while True:
        try:
            bot.find_element_by_xpath('//*[@id="list_results"]/div[%d]/div[2]/div[1]/div'%(page))
            break
        except: pass
    with open("Output.csv",'a') as f:
        for n in range(1,11):
            try:
                x=bot.find_element_by_xpath('//*[@id="list_results"]/div[%d]/div[2]/div[%d]/div'%(page,n))
                extracted+=1
                print("\rExtracting... [%d] || %s"%(extracted,clock(time()-start)),end='')
                n+=1
                line=x.text.split("\n")
                name,pin=line[0],line[2].split(' ')[-1]
                if name=='Sponsored': continue
                try: int(pin)
                except: pin=re.findall(r'\d{6}',x.text)[0]
                f.write('"'+name+'",'+pin+'\n')
            except: pass
    return page

print("Starting subprocesses...")
bot=Chrome('chromedriver.exe')
print("Loading http://search.insing.com/singapore/browse/food-drink\n")
bot.get("http://search.insing.com/singapore/browse/food-drink")
bot.maximize_window()
start=time()
timer,page=time(),0
extracted=0
while True:
    try:
        page=extract(page)
        timer=time()
    except:
        print("\rLoading...                                ",end='')
        if time()-timer>5:
            try:
                q=bot.find_elements_by_class_name("r-info")[-1].location['y']
                bot.execute_script("window.scrollTo(0, %d)"%(q))
            except: pass
