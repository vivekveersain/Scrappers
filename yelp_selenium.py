from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from time import time,sleep
import re

while True:
    try:
        LIM=int(input("Please enter the NUMBER OF PAGES (for each zip code) you wanna crawl: "))
        break
    except:print("SOME ERROR! TRY AGAIN.")

def clock(t):
    hr=t//3600
    mn=(t//60)%60
    sec=t%60
    if hr>0: return '%.2dhr:%.2dmn:%.2dsec'%(hr,mn,sec)
    else:return '%.2dmn:%.2dsec'%(mn,sec)

def loading():
    try:
        bot.find_element_by_css_selector("div.circle-spinner.js-circle-spinner.hidden.inline-block")
        return True
    except: return False

def force():
    clicked=False
    while not clicked:
        try:
            bot.find_element_by_css_selector("span.pagination-label.responsive-hidden-small.pagination-links_anchor").click()
            clicked=True
        except: sleep(2)

def last_page():
    while True:
        try:
            z=bot.find_element_by_css_selector("div.page-of-pages.arrange_unit.arrange_unit--fill").text
            cur,lim=re.findall(r'\d+',z)
            if cur==lim: return True
            else: return False
        except: pass

def search(ZIP='',LIM=100):
    for pos,keys in zip(bot.find_elements_by_css_selector("input.main-search_field.pseudo-input_field"),['Restaurants',ZIP]):
        pos.send_keys(Keys.CONTROL,'a')
        pos.send_keys(Keys.BACKSPACE)
        pos.send_keys(keys)
    bot.find_element_by_id("header-search-submit").click()
    while True:
        try:
            try:extract(ZIP)
            except: pass
            try:
                r0,lim=re.findall(r'\d+',bot.find_element_by_css_selector("div.page-of-pages.arrange_unit.arrange_unit--fill").text)
                if int(r0)==int(lim) or int(r0)>=LIM: return
            except: pass
            bot.find_element_by_css_selector("span.pagination-label.responsive-hidden-small.pagination-links_anchor").click()
        except:
            if last_page(): break
            else: force()
    print('')

def extract(ZIP):
    while loading(): sleep(3)
    try:page=bot.find_element_by_css_selector("div.page-of-pages.arrange_unit.arrange_unit--fill").text
    except: page=''
    print('\rZIP: %s--%s--Time Elapsed: %s    '%(ZIP,page,clock(time()-start)),end='')
    results=bot.find_elements_by_class_name("regular-search-result")
    with open("output.csv",'a') as f:
        for R in results:
            try:
                try:
                    title=R.find_element_by_class_name("search-result-title").find_element_by_tag_name("a")
                    name=title.text
                    link=title.get_attribute('href')
                except:name,link=['','']
                try:add=R.find_element_by_tag_name("address").text
                except: add=''
                try:street,city=add.split('\n')
                except: street,city=['','']
                try: city,state=city.split(', ')
                except: city,state=['','']
                try: state,pin=state.split(" ")
                except: state,pin=['','']
                try:phone=R.find_element_by_class_name("biz-phone").text
                except: phone='NOT FOUND'
                try:
                    if R.find_element_by_tag_name("button").text=='Start Order': SO='YES'
                    else: SO='NO'
                except: SO='NO'
                LIST=[name,street,city,state,pin,phone,SO,link]
                if pin in zips: info='"'+'","'.join(LIST)+'"\n'
                else: info=''
            except: info=''
            f.write(info)

print("Booting the subprocesses... Please wait...")
bot=Chrome('chromedriver.exe')
print("Accessing http://www.yelp.com Please wait...")
bot.get("http://www.yelp.com")
print("Loading...\n\nCrawling...\n")
start=time()
stack,zips=[],[]
with open("zip.txt") as f:
    for line in f: stack.append(line.strip('\n'))

open("output.csv",'w').close()
with open("output.csv",'a') as f: f.write('Name,Street,City,State,Pin,Phone,Start Order Button,Yelp Link\n')

for x in stack:
    zips.append(x)
    search(x,int(LIM))

try: bot.quit()
except: pass
input("\n\nCrawling complete. Run Time: %s"%(clock(time()-start)))
