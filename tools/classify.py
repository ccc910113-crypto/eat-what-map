import json,re,sys
S=json.load(open('shops.json')); R=json.load(open('reviewed.json'))
def norm(n): return re.sub(r'[\s　・·\-–_()（）\[\]【】「」『』,，.。!！&＆]|台北|臺北|大安|店$|分店|門市|科技大樓|和平|復興|復南|瑞安|旗艦','',n).lower()
inc={norm(s['name']):s['id'] for s in S}
inc_keys=list(inc)
rev={norm(k):v for k,v in R.items()}
AUTO=[("早餐／早午餐",r'早餐|早午餐|brunch|豆漿|美而美|麥味登|蛋餅|飯糰|晨間|早安|吐司|森之豆|呷尚寶|找餐|和平食光|好食|真芳|福七|永和'),
      ("咖啡／甜點／飲料",r'咖啡|cafe|café|coffee|甜品|甜點|烘焙|蛋糕|麵包|冰|茶|優格|鯛魚燒|泡芙|bakery|juice|KURE|雪坊|酒窩'),
      ("素食",r'素食|蔬食|素'),
      ("酒吧／餐酒館",r'酒|bar|bistro|pub|居酒屋|wine'),
      ("高價或合菜（每人超過 300）",r'牛排館$|鐵板燒|涮涮|燒肉|壽喜|割烹|鮨|料亭|fine|西班牙|法國|MVSA|Ephernité|La Clé|Longtail|千松谷|燈燈庵|紅豆食府|葉公館|上海醉月樓|鴻儒園|麒雲|馬可波羅|月之意大利|SEMINAR|The House|卡奈基|Big Table|Kyoto Koji'),
      ("速食連鎖（另查）",r'肯德基|漢堡王|麥當勞|必勝客|Subway|摩斯'),
      ("非餐廳／不明",r'^便當$|^素食$|^炒飯$|^麵攤$|^飯麵$|協民隆|國際餐飲|桌遊|甜品屋|悠客|嘰嘰喳喳|婷亭|badudu|xai|Seven Fine|The Unique|le corner|Coffee Naps|URBN')]
def classify(name):
    n=norm(name)
    for k in inc_keys:
        if k and (k in n or n in k) and min(len(k),len(n))>=2: return ("已收錄",inc[k])
    for k,v in rev.items():
        if k and (k in n or n in k) and min(len(k),len(n))>=2: return ("已查核排除",v)
    for lab,rx in AUTO:
        if re.search(rx,name,re.I): return ("不適合晚餐",lab)
    return ("待查",'')
if __name__=="__main__":
    src=sys.argv[1]
    rows=[]
    if src=="osm":
        for e in json.load(open('pois.json'))['elements']:
            t=e.get('tags',{});n=t.get('name')
            if not n: continue
            if t.get('cuisine','') in ('breakfast','coffee_shop','ice_cream','juice','bubble_tea'): rows.append((n,"不適合晚餐","早餐／飲料")); continue
            c=classify(n); rows.append((n,)+c)
    else:
        for e in json.load(open('ifoodie_all.json')):
            n=e['name']
            if e.get('closed'): rows.append((n,"已歇業（愛食記標示）","")); continue
            tags="".join(e.get('tags',[]))
            c=classify(n)
            if c[0]=="待查":
                if re.search(r'早餐|早午餐|咖啡|甜點|下午茶|飲料|烘焙|冰品|素食|酒吧|居酒屋|蛋糕|麵包',tags) and not re.search(r'晚餐',tags): c=("不適合晚餐","類型："+tags[:20])
                elif e.get('avg') and e['avg']>350: c=("不適合晚餐",f"均消 {e['avg']}")
            rows.append((n,)+c)
    from collections import Counter
    seen=set();uniq=[]
    for r_ in rows:
        if r_[0] in seen: continue
        seen.add(r_[0]);uniq.append(r_)
    cnt=Counter(r_[1] for r_ in uniq)
    print(src,len(uniq),dict(cnt))
    json.dump(uniq,open(f'coverage_{src}.json','w'),ensure_ascii=False,indent=0)
    for r_ in uniq:
        if r_[1]=="待查": print("  待查:",r_[0])
