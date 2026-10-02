"""Monte Carlo launch simulator: per-post power-law reach, per-platform ramps, hit effects, ladder, gate.
Outputs percentile bands for retained MRR, booked MRR, cash, views, posts by day. All inputs are ASSUMPTIONS (labeled)."""
import random, math, csv, json, statistics as st
LEVELS={
 'conservative': dict(med0=250, ramp=1.25, tail=1.9, hitp=1/400, tr_share=0.20, grad=0.06, link=0.002, lp=0.65, cvr=0.025, renew=0.40, churn=0.10, wl=0.05, lists=0.005, coached=0.03, ceiling=360000),
 'central':      dict(med0=500, ramp=1.45, tail=1.7, hitp=1/200, tr_share=0.35, grad=0.10, link=0.004, lp=0.70, cvr=0.05,  renew=0.50, churn=0.07, wl=0.10, lists=0.015, coached=0.05, ceiling=600000),
 'breakout':     dict(med0=900, ramp=1.65, tail=1.55, hitp=1/120, tr_share=0.60, grad=0.18, link=0.006, lp=0.75, cvr=0.08, renew=0.60, churn=0.05, wl=0.15, lists=0.03, coached=0.07, ceiling=1200000),
}
# per-platform: (median multiplier vs IG, tail exponent tweak, ramp multiplier). Lower tail = fatter tail.
PLAT={'ig':(1.0,0.0,1.0),'fb':(0.9,0.05,1.15),'tt':(0.6,-0.15,0.9),'yt':(0.4,0.1,0.8),'th':(0.12,0.1,1.0),'x':(0.12,0.1,1.0)}
def pareto(xm,a): return xm*(1-random.random())**(-1/a)
def sim(L, seed, lists=30000, wl=1500, days=180):
    random.seed(seed); P=LEVELS[L]
    opens={p:-7 for p in range(4)}; hit_boost={}; cohorts=[]; cash=0; ret=0; out=[]
    def ladder(r): return (7,9,20) if r>=30000 else (5,8,20) if r>=10000 else (4,6,20)
    for d in range(1,days+1):
        npages,masters,trials=ladder(ret); trials=10 if d<=7 else trials
        for p in range(npages): opens.setdefault(p,d)
        views=0; posts=0; plat_v={k:0 for k in PLAT}
        for p in range(npages):
            age=d-opens[p]+7
            med=P['med0']*(P['ramp']**(age/14.0))*hit_boost.get(p,1.0)
            med=min(med, 40000)
            pv=0
            for plat,(m,tt,rm) in PLAT.items():
                n = masters if plat!='yt' else min(masters,4)
                if plat=='fb': n=masters+4
                a=P['tail']+tt
                for i in range(n):
                    v=pareto(med*m*(rm**(age/30)), a)
                    if random.random()<P['hitp']: v*=random.choice([20,50,100,300])
                    v=min(v, 3_000_000); pv+=v; plat_v[plat]+=v
                posts+=n
            # trial reels on IG
            for i in range(trials):
                v=pareto(med*P['tr_share']*0.77, P['tail']); 
                if random.random()<P['grad']: v*=2.5
                pv+=v; plat_v['ig']+=v
            posts+=trials
            if pv>P['ceiling']: pv=P['ceiling']
            # hit effect: raise page baseline for 14 days if any post > 20x median
            if pv>med*masters*8: hit_boost[p]=min(3.0,hit_boost.get(p,1.0)*1.6)
            else: hit_boost[p]=max(1.0,hit_boost.get(p,1.0)*0.96)
            views+=pv
        buyers=views*P['link']*P['lp']*P['cvr']
        if d<=3: buyers+=wl*P['wl']/3
        if d<=14: buyers+=lists*P['lists']/14
        paid=0
        if ret>=30000:
            paid=max(0,0.25*ret/30-16-(masters*npages*1.28+trials*npages*0.225)); buyers+=paid/85
        cohorts.append([d,buyers]); booked=0; ret=0; members=0
        for cd,b in cohorts:
            a=d-cd; s=1 if a<30 else P['renew']*((1-P['churn'])**((a-30)/30)); booked+=b*s*25*0.95; members+=b*s
            ret+=b*(P['renew'] if a<30 else s)*25*0.95
        if d>=10:
            elig=sum(b*(1 if d-cd<30 else P['renew']*((1-P['churn'])**((d-cd-30)/30))) for cd,b in cohorts if d-cd>=10); c=elig*P['coached']; booked+=c*147*0.95; ret+=c*147*0.95
        rev=buyers*12+sum(b*(P['renew']*((1-P['churn'])**((d-cd-30)/30)))*25 for cd,b in cohorts if (d-cd)%30==0 and d-cd>=30)
        cost=masters*npages*1.28+trials*npages*0.225+16+paid+posts*20/3600*20
        cash+=rev*0.97-cost
        out.append(dict(day=d,pages=npages,posts=posts,views=views,buyers=buyers,members=members,booked=booked,retained=ret,cash=cash,cost=cost,paid=paid,**{f'v_{k}':v for k,v in plat_v.items()}))
    return out
def band(L,n=300,**kw):
    runs=[sim(L,s,**kw) for s in range(n)]
    keys=['posts','views','buyers','members','booked','retained','cash','cost','paid','v_ig','v_fb','v_tt','v_yt','v_th','v_x']
    rows=[]
    for i in range(180):
        r={'day':i+1,'pages':runs[0][i]['pages']}
        for k in keys:
            vals=sorted(x[i][k] for x in runs); r[k+'_p10']=vals[int(n*0.1)]; r[k+'_p50']=vals[n//2]; r[k+'_p90']=vals[int(n*0.9)]
        rows.append(r)
    def prob(t,by): return sum(1 for x in runs if any(x[i]['retained']>=t for i in range(by)))/n
    probs={'p_100k_by45':prob(100000,45),'p_250k_by90':prob(250000,90),'p_30k_by14':prob(30000,14),'p_10k_by7':prob(10000,7)}
    return rows,probs
if __name__=='__main__':
    import sys
    res={}
    for L in LEVELS:
        rows,probs=band(L); res[L]=probs
        with open(f'data/mc_{L}.csv','w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        print(L, probs)
        for r in rows:
            if r['day'] in (1,3,7,14,21,30,45,60,90,180): print(' ',r['day'],r['pages'],round(r['posts_p50']),round(r['views_p10']),round(r['views_p50']),round(r['views_p90']),'| ret',round(r['retained_p10']),round(r['retained_p50']),round(r['retained_p90']),'| cash',round(r['cash_p50']))
    json.dump(res,open('data/mc_probs.json','w'),indent=1)
