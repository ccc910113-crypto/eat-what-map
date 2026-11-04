import json,glob,urllib.parse,urllib.request,os
cache=json.load(open("geo_cache.json")) if os.path.exists("geo_cache.json") else {}
S=json.load(open("base.json"))
seen={x["id"] for x in S}
for f in sorted(glob.glob("extra_*.json")):
    for e in json.load(open(f)):
        if "ll" not in e:
            a=e["addr"]
            if a not in cache:
                u="https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=json&maxLocations=1&outFields=Addr_type&singleLine="+urllib.parse.quote(a)
                c=json.load(urllib.request.urlopen(u))["candidates"][0]
                cache[a]=[round(c["location"]["y"],6),round(c["location"]["x"],6),c["score"],c["attributes"]["Addr_type"],c["address"]]
            e["ll"]=cache[a][:2]; print(e["id"],cache[a][2:])
        if e["id"] in seen: continue
        seen.add(e["id"]); S.append(e)
json.dump(cache,open("geo_cache.json","w"),ensure_ascii=False)
import patches
S=patches.apply(S)
import patches_audit2
S=patches_audit2.apply(S)
import patches_audit3
S=patches_audit3.apply(S)
import patches_xcheck
S=patches_xcheck.apply(S)
import patches_gm
S=patches_gm.apply(S)
json.dump(S,open("shops.json","w"),ensure_ascii=False,indent=1)
print(len(S))
