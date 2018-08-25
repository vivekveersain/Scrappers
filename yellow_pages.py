from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
import re
from time import time,sleep

while True:
    try:
        LIM=int(input("Please enter the NUMBER OF RESTAURANTS you wanna scrape: "))
        break
    except:print("SOME ERROR! TRY AGAIN")

def clock(t):
    hr=t//3600
    mn=(t//60)%60
    sec=t%60
    if hr>0: return '%.2dhr:%.2dmin:%.2dsec'%(hr,mn,sec)
    else:return '%.2dmin:%.2dsec'%(mn,sec)

def save(stack,links):
    with open("output.csv",'a') as f:
        for x in stack: f.write('"'+'","'.join(x)+'"\n')
    with open("links.txt",'a') as f:
        for link in links:
            f.write(link+'\n')

def next_page():
    nextloc=bot.find_element_by_css_selector("a.next.ajax-page").location['y']
    bot.execute_script("window.scrollTo(0, %d)"%(nextloc-300))
    bot.find_element_by_css_selector("a.next.ajax-page").click()

def search(ZIP='',LIM=3000):
    what=bot.find_element_by_id("query")
    where=bot.find_element_by_id("location")
    for keys,place in zip(['restaurant',ZIP],[what,where]):
        place.send_keys(Keys.CONTROL,'a')
        place.send_keys(Keys.BACKSPACE)
        place.send_keys(keys)
    where.send_keys(Keys.ENTER)
    found=False
    while not found:
        try:
            r0,r1,lim=re.findall(r'\d+',bot.find_element_by_xpath("//div[@class='pagination']/p").text)
            if int(r0)==1: found=True
        except: pass
    while True:
        try:
            try:extract(ZIP)
            except: pass
            try:
                r0,r1,lim=re.findall(r'\d+',bot.find_element_by_xpath("//div[@class='pagination']/p").text)
                print("\rZIP: %s || Results: %s-%s of %s || %s      "%(ZIP,r0,r1,lim,clock(time()-start)),end='')
                store=r0
                if int(r1)>LIM-1 or int(r1)==int(lim): break
            except: pass
            while store==r0:
                try: next_page()
                except: pass
                sleep(2)
                r0,r1,lim=re.findall(r'\d+',bot.find_element_by_xpath("//div[@class='pagination']/p").text)
        except:
            print("\rError! Please open Chrome and make sure it navigated to results %s to %s" %(r0,r1),end='')
            sleep(5)
            print("\r                                                                                    ")
    print('')
                    
def extract(ZIP):
    found=False
    while not found:
        try:
            box=bot.find_element_by_css_selector("div.search-results.organic")
            results=box.find_elements_by_class_name("v-card")
            found=True
        except: pass
    stack,links=[],[]
    for R in results:
        try:
            title=R.find_element_by_class_name("business-name")
            name,link=title.text,title.get_attribute('href')
        except:name,link=['NOT FOUND']*2
        
        try:street=R.find_element_by_class_name("street-address").text
        except:street=''
        try:city=R.find_element_by_class_name("locality").text
        except: city=''
        try:state=R.find_element_by_xpath('//span[@itemprop="addressRegion"]').text
        except:state=''
        try:pin=R.find_element_by_xpath('//span[@itemprop="postalCode"]').text
        except:pin=''
        try:phone=R.find_element_by_css_selector("div.phones.phone.primary").text
        except:phone=''
        try:website=R.find_element_by_link_text("Website").get_attribute("href")
        except: website=''
        if pin==ZIP:
            stack.append([name,street,city,state,pin,phone,website,link])
            links.append(link)
    save(stack,links)

with open("deep extraction.csv",'w') as f: f.write("Name,Street,City,State,Zip Code,Phone,Category,Category,Website,E-mail,Twitter,Facebook\n")    
open("links.txt",'w').close()
with open("output.csv",'w') as f: f.write("Name,Street,City,State,Zip Code,Phone,Website,YP link\n")
print("Starting subprocesses...")
bot=Chrome('chromedriver.exe')
print("Accessing YP.com ...")
bot.get("http:www.yellowpages.com")
print("\n\nCrawling... (Surface Extraction)\n")
start=time()
pins=[]
zips=[]
with open("ZIP.txt") as f:
    for line in f: pins.append(line.strip('\n'))

for pin in pins:
    if len(pin)<5: continue
    zips.append(pin)
    search(pin,int(LIM))

try:bot.quit()
except: pass
print('\n\nSurface Extraction complete.\nStarting Deep Extraction...\n')

start=time()
import requests
from lxml import etree

def deep_extract(link):
    ID=link.split('?')[-1]
    try:
        try:response=requests.get(link,headers=head,data=ID)
        except: response=''
        TRY=1
        while str(response)!='<Response [200]>':
            try:
                print('\rERROR [TRIES = %d] - Website response - %s'%(TRY,str(response)),end='')
                TRY+=1
                response=requests.get(link,headers=head,data=ID)
            except: TRY+=1
            if TRY>3: return ''
        root=etree.HTML(response.text)
        try:name=root.xpath('//h1[@itemprop="name"]')[0].text
        except:name=''
        try:mail=root.xpath('//a[@class="email-business"]')[0].attrib['href'].replace('mailto:','')
        except: mail=""
        try:web=root.xpath('//a[@class="custom-link"]')[0].attrib['href']
        except: web=""
        try:street=root.xpath('//p[@class="street-address"]')[0].text
        except: street=''
        try:
            city,state,pin=['NOT FOUND']*3
            city=root.xpath('//span[@itemprop="addressLocality"]')[0].text
            state=root.xpath('//span[@itemprop="addressRegion"]')[0].text
            pin=root.xpath('//span[@itemprop="postalCode"]')[0].text
        except: pass
        try:phone=root.xpath('//p[@itemprop="telephone"]')[0].text
        except: phone=''
        try:cat1=root.xpath('//dd[@class="categories"]/span/a')[0].text
        except:cat1=''
        try:cat2=root.xpath('//dd[@class="categories"]/span/a')[1].text
        except: cat2=''
        try:
            soc1=root.xpath('//*[@id="business-details"]/dl[1]/dd[1]/a')[0].attrib['href']
            if 'twitter' not in soc1: 1/0
        except: soc1=''
        try:
            soc2=root.xpath('//*[@id="business-details"]/dl[1]/dd[1]/a')[1].attrib['href']
            if 'facebook' not in soc2: 1/0
        except: soc2=''
        if pin in zips: return '"'+'","'.join([name,street,city,state,pin,phone,cat1,cat2,web,mail,soc1,soc2])+'"\n'
        else: return ''
    except Exception as e: print(e)

start=time()
x="""Host: www.yellowpages.com
User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:46.0) Gecko/20100101 Firefox/46.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive"""
head=dict(r.split(": ") for r in x.split("\n"))
links=[]
with open("links.txt") as f:
    for line in f:
        links.append(line.strip('\n'))
counter=1
lim=len(links)
for link in links:
    try:
        print("\rNow Extracting: %d of %d || %s || %s      "%(counter,lim,clock(time()-start),clock((lim-counter)*(time()-start)/counter)),end='')
        counter+=1
        with open("deep extraction.csv",'a') as f: f.write(deep_extract(link))
    except Exception as e: print(e)
input("\n\nProcess Complete. Press <ENTER> to Exit.")
