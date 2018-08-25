import requests, re
from TTS import rachel
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}

def parser(text,links=False,getlinks=False):
    if links or getlinks:
        out=''
        temp=''
        stack=[]
        link='https://en.wikipedia.org/'
        escape=box=False
        for x in text:
            if x =='<':
                escape=True
                if len(link)>25:
                    if links: out+=' (%s)'%link
                    stack.append(link)
                    link='https://en.wikipedia.org/'
            elif x =='>':
                escape=False
                continue
            if escape:
                if temp=='href="/':
                    if x!='"':link+=x
                    else: temp=''
                elif x in 'href="/': temp+=x
                else: temp=''
                continue
            else:
                if x=='[': box=True
                elif x==']':
                    box=False
                    continue
                if box: continue
                else:out+=x
        return out,stack
    else:
        out=''
        escape=False
        box=False
        for x in text:
            if x =='<':escape=True
            elif x =='>':
                escape=False
                continue
            if escape:continue
            else:
                if x=='[': box=True
                elif x==']':
                    box=False
                    continue
                if box: continue
                else:out+=x
        return out    

def wikipedia_runner(url):
    html=requests.get(url,headers=headers).text
    text='\n'.join(re.findall('<p>(.*?)</p>',html))
    return parser(text,getlinks=True)

search="Hinduism"
search=input("What you wanna wiki about?: ")
url='https://en.wikipedia.org/wiki/Special:Search/'+search.replace(' ','_')
html=requests.get(url).text
paragraphs=re.findall('<p>(.*?)</p>',html)
for para in paragraphs:
    para=parser(para).encode('ascii','ignore').decode('ascii','ignore')
    print(para)
    rachel(para)
