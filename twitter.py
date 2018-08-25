from requests_oauthlib import OAuth1
import requests
from time import time, sleep
start=time()

# Enter OAuth Details...


def clock(t):
    hr=t//3600
    mn=(t//60)%60
    sec=t%60
    if hr>0: return '%.2dhr:%.2dmin:%.2dsec'%(hr,mn,sec)
    else:return '%.2dmin:%.2dsec'%(mn,sec)

def Filter(user,who=''):
    stack=[who]
    with open("users.txt",'a') as f:f.write(str(user['screen_name'])+'\n')
    for p in keys:
        try:stack.append(str(user[p]).replace('\n',' ').replace('\r',' ').encode('ascii','ignore').decode())
        except: stack.append('')
    with open("sample.csv",'a') as f:f.write('"'+'","'.join(stack)+'"\n')

def extract(username,who='friends', limit=1):
    global counter
    global stopwatch
    if who not in ['friends','followers']:
        print("What you wanna extract?")
        return
    cursor,pager=-1,0
    timer=time()
    while cursor!=0 and pager<limit:
        pager+=1
        counter+=1
        reply=False
        while not reply:
            try:
                response=requests.get('https://api.twitter.com/1.1/%s/list.json?screen_name=%s&cursor=%d&count=200'%(who,username,cursor), auth=OAuth1()).json()
                reply=True
            except:
                sleep(2)
                counter+=1
        for user in response['users']: Filter(user,who.strip('s'))
        cursor=response['next_cursor']
        print("\rExtracted %d page(s) of %s in %s"%(pager,who,clock(time()-timer)),end='')
        if counter%15==0 and cursor!=0 and pager<limit:
            t_rem=stopwatch+15*60+10-time()
            while t_rem>0:
                print("\rSleep: %s                                     "%(clock(t_rem)),end='')
                sleep(min(5,t_rem))
                t_rem=stopwatch+15*60+10-time()
            stopwatch=time()
    print('')

def twitter(username):
    for group in ['followers']: extract(username,group,30)

keys='name,screen_name,id,followers_count,friends_count,location,description,favourites_count,follow_request_sent,verified,url,created_at,time_zone,following,profile_image_url,profile_banner_url,listed_count,default_profile,default_profile_image,blocking,profile_text_color,muting,utc_offset,contributors_enabled,profile_background_tile,lang,profile_use_background_image,statuses_count,profile_link_color,profile_image_url_https,is_translation_enabled,notifications,protected,profile_background_color,blocked_by,profile_background_image_url_https,geo_enabled,profile_sidebar_border_color,is_translator,has_extended_profile,id_str,profile_background_image_url,profile_sidebar_fill_color'.split(',')
with open("sample.csv",'a') as f: f.write('Relationship,'+','.join(keys)+'\n')

counter=0
stopwatch=time()
twitter("larrytankjones")
print("Time to scrape: %f seconds"%(clock(time()-start)))
input()
