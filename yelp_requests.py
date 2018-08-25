import re,requests
from time import time,sleep
from lxml import etree

def clock(t):
    hr=t//3600
    mn=(t//60)%60
    sec=t%60
    if hr>0: return '%.2dhr:%.2dmin:%.2dsec'%(hr,mn,sec)
    else:return '%.2dmin:%.2dsec'%(mn,sec)

def LINKS(html):
    z=re.findall(r"""<a href=".*?" data-analytics='{"target":"name","feature_click":""}' rel="" itemprop="name""",html)
    links=[]
    for x in z: links.append("http://www.yellowpages.com"+x.replace('<a href="','').replace("""" data-analytics='{"target":"name","feature_click":""}' rel="" itemprop="name""",''))
    return links
    
def search(pin='',LIM=3000):
    Try=1
    while Try<=3:
        try:
            response=requests.get('http://www.yellowpages.com/search?search_terms=reastaurant&geo_location_terms='+pin,headers=head)
            break
        except:Try+=1
    try:
        while str(response)!='<Response [200]>':
            try:
                print('\rERROR [TRIES = %d] - Website response - %s'%(TRY,str(response)),end='')
                TRY+=1
                response=requests.get(link,headers=head,data=ID)
            except: pass
            if TRY>3: return ''
        page,error=2,0
        while True:
            try:
                root=etree.HTML(response.text)
                text=response.text.replace('\r','').replace('\n','')
                links=list(x.attrib['href'] for x in root.xpath('//*[@class="info"]/h3[1]/a[1]')[-30:])
                with open("links.txt",'a') as f:
                    for link in links: f.write('http://www.yellowpages.com'+link+'\n')
                try:
                    r0,r1,lim=re.findall(r'\d+',root.xpath('//div[@class="pagination"]/*/text()')[0])
                    print("\rZIP: %s || Results: %s-%s of %s || %s      "%(pin,r0,r1,lim,clock(time()-start)),end='')
                    if int(r1)>=LIM or int(r1)==int(lim): return
                except:
                    print("\rZIP: %s || Page: %d || %s      "%(pin,page,clock(time()-start)),end='')
                    if (page-1)*30>LIM: return
                response=requests.get('http://www.yellowpages.com/search?search_terms=reastaurant&geo_location_terms='+pin+'&page='+str(page),headers=head)
                while str(response)!='<Response [200]>':
                    error+=1
                    if error>5: return
                    response=requests.get('http://www.yellowpages.com/search?search_terms=reastaurant&geo_location_terms='+pin+'&page='+str(page),headers=head)
                else:error=0
                if error>3: return
                page+=1
            except Exception as e:
                input(e)
                error+=1
                if error>3: return 
    except: return ''

with open("deep extraction.csv",'w') as f: f.write("Name,Street,City,State,Zip,Phone,Category,Category,Wesite,E-mail,twitter,facebook\n")    
open("links.txt",'w').close()
print("Starting subprocesses...")
x="""Host: www.yellowpages.com
User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:46.0) Gecko/20100101 Firefox/46.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive"""
head=dict(r.split(": ") for r in x.split("\n"))
start=time()
pins=[]
zips=[]
with open("ZIP.txt") as f:
    for line in f: pins.append(line.strip('\n'))
for pin in pins:
    try:pin,LIM=pin.split('-')
    except: pin,LIM=pin,3000
    zips.append(pin)
    search(pin,int(LIM))
    print('')

print('\n\nSurface Extraction complete.\nStarting Deep Extraction...\n')

start=time()

def deep_extract(link):
    ID=link.split('?')[-1]
    try:
        try:response=requests.get(link,headers=head,data=ID)
        except: response=''
        TRY=1
        while str(response)!='<Response [200]>':
            try:
                #print('\rERROR [TRIES = %d] - Website response - %s'%(TRY,str(response)),end='')
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
links=[]
with open("links.txt") as f:
    for line in f:
        links.append(line.strip('\n'))
counter=1
lim=len(set(links))
for link in set(links):
    try:
        print("\rNow Extracting: %d of %d || %s || %s      "%(counter,lim,clock(time()-start),clock((lim-counter)*(time()-start)/counter)),end='')
        counter+=1
        with open("deep extraction.csv",'a') as f: f.write(deep_extract(link))
    except Exception as e: print(e)
input("\n\nProcess Complete. Press <ENTER> to Exit.")

