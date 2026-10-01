import json,sys,re
F=json.load(open("fdc_sr_legacy_subset.json"))
for q in sys.argv[1:]:
    terms=[t.lower() for t in q.split("&")]
    hits=[(k,v) for k,v in F.items() if all(t in v["desc"].lower() for t in terms)]
    hits.sort(key=lambda kv: len(kv[1]["desc"]))
    print("==",q)
    for k,v in hits[:6]:
        print(" ",k,v["desc"][:90],"|",v.get("kcal"),v.get("protein_g"),v.get("fiber_g"),v.get("sodium_mg"),v.get("leucine_g"))
