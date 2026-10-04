"""Build the tidy dataset and subsidy estimates for the Gulf Fuel Subsidy Tracker.

Run from the project folder:  python scripts/build_data.py
Outputs go to data/processed/.
"""
import json, csv, os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","data","processed")
os.makedirs(OUT,exist_ok=True)
M=["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10"]
N=None
def usd(local,fx): return [None if v is None else round(v/fx,4) for v in local]
C={}
def add(code,name,group,cont,g,d,**kw):
    C[code]=dict(name=name,group=group,continent=cont,gasoline=g+[N]*(10-len(g)),diesel=d+[N]*(10-len(d)),**kw)
# ---- Gulf six (official pump prices, local currency per litre -> USD at peg) ----
add("AE","UAE","Gulf","Middle East",
    usd([2.42,2.33,2.48,3.28,3.55,3.83,3.29,3.49,3.69,4.28],3.6725),
    usd([2.55,2.52,2.72,4.69,4.69,4.33,3.60,3.80,4.30,4.80],3.6725),
    vat=0.05,vol=dict(gasoline=11.37,diesel=4.09),pop=10.99,grade="Special 95",regime="Market-linked, reset monthly",basis="Official monthly price, AED 3.6725 per USD")
add("SA","Saudi Arabia","Gulf","Middle East",usd([2.33]*10,3.75),usd([1.79]*10,3.75),
    vat=0.15,vol=dict(gasoline=29.55,diesel=35.33),pop=35.30,grade="Gasoline 95",regime="Capped by royal directive since July 2021",basis="Aramco price, SAR 3.75 per USD. October is the 1 Oct reading")
add("QA","Qatar","Gulf","Middle East",
    usd([2.00,1.85,1.90,2.05,2.10,2.10,2.10,2.10,2.10,2.10],3.64),
    usd([2.00,1.90,2.05,2.05,2.05,2.05,2.05,2.05,2.05,2.05],3.64),
    vat=0.0,vol=dict(gasoline=2.83,diesel=1.99),pop=2.86,grade="Super 95",regime="Set monthly; has not passed QAR 2.10 during the war",basis="QatarEnergy monthly price, QAR 3.64 per USD")
add("KW","Kuwait","Gulf","Middle East",usd([0.105]*9+[N],0.3085),usd([0.115]*9+[N],0.3085),
    vat=0.0,vol=dict(gasoline=5.00,diesel=3.11),pop=4.90,grade="Super 95",regime="Frozen each quarter by the subsidies committee",basis="Quarterly price, KWD 0.3085 per USD. Q4 decision not yet found")
add("BH","Bahrain","Gulf","Middle East",
    usd([0.235,0.235,0.235,0.253,0.269,0.269,0.247,0.247,0.247,0.277],0.376),
    usd([0.200,0.200,0.200,0.220,0.229,0.229,0.229,0.229,0.229,0.260],0.376),
    vat=0.0,vol=dict(gasoline=1.32,diesel=0.22),pop=1.59,grade="Mumtaz 95",regime="Monthly committee pricing since 30 Dec 2025",basis="Official monthly price, BHD 0.376 per USD")
# Iran: tier-2 price 30,000 rials/L, open-market exchange rate; only months with a dated rate quote
ir_fx=[N,1630000,N,N,N,N,N,2000000,2250000,2565000]
add("IR","Iran","Gulf","Middle East",[None if f is None else round(30000/f,4) for f in ir_fx],[N]*10,
    vat=0.0,vol=dict(gasoline=45.26,diesel=None),pop=91.57,grade="Tier 2 quota (30,000 rials)",regime="Three-tier quota: 15,000 / 30,000 / 100,000 rials",basis="Tier-2 price at open-market rial rate; shown only for months with a dated rate")
# ---- Comparison countries (USD per litre) ----
add("US","United States","Comparison","North America",[.742,.768,.961,1.084,1.183,1.070,1.039,1.072,1.150],[.931,.983,1.300,1.453,1.479,1.327,1.309,1.443,1.662],basis="EIA monthly average, regular / on-highway diesel")
add("CA","Canada","Comparison","North America",[.982,1.039,1.334,1.376,1.289,1.189,1.312,1.325,1.354],[1.189,1.240,1.727,1.612,1.502,1.353,1.633,1.702],basis="Kalibrate national average at month-end")
add("GB","United Kingdom","Comparison","Europe",[1.800,1.788,1.871,2.107,2.124,2.069,2.036,2.185,2.275],[1.925,1.917,2.117,2.552,2.525,2.350,2.242,2.464,2.584],basis="DESNZ weekly prices, monthly mean")
add("DE","Germany","Comparison","Europe",[2.040,2.082,2.340,2.465,2.316,2.152,2.397,2.486,2.610],[1.985,2.037,2.504,2.645,2.326,2.092,2.395,2.576,2.748],basis="ADAC monthly average, Super E10")
add("FR","France","Comparison","Europe",[1.990,2.020,2.195,2.330,2.379,2.227,2.250,2.328,2.443],[1.951,2.011,2.376,2.627,2.498,2.263,2.345,2.569,2.677],basis="Monthly barometer, SP95-E10")
add("IN","India","Comparison","Asia",[1.045,1.044,1.020,1.015,1.022,1.075,1.065,1.070,1.070],[.966,.966,.944,.939,.948,1.002,.993,.998,.997],basis="Delhi administered price")
add("CN","China","Comparison","Asia",[N,1.054,1.191,N,N,N,N,N,1.381],[N,.927,N,N,N,N,N,N,N,1.241],basis="Point-in-time readings only (95-octane)")
add("JP","Japan","Comparison","Asia",[.990,1.007,1.083,1.058,1.070,1.056,1.046,1.071,1.089],[.915,.932,1.008,.991,1.003,.989,.980,1.004,1.020],basis="METI survey monthly average; Sep is the 28 Sep reading")
add("NG","Nigeria","Comparison","Africa",[.730,.774,.938,1.125,1.167,N,N,N,1.055],[],basis="NBS national average Jan-May; Sep is a Lagos/Abuja reading")
add("ZA","South Africa","Comparison","Africa",[1.272,1.255,1.213,1.409,1.615,1.710,1.585,1.580,1.662],[1.129,1.119,1.108,1.563,1.890,1.702,1.506,1.616,1.798],basis="Regulated inland 95 ULP; diesel is the wholesale list price")
add("BR","Brazil","Comparison","South America",[1.181,1.210,1.258,1.336,1.330,1.289,1.282,1.267,1.282],[1.143,1.172,1.353,1.477,1.438,1.379,1.360,1.339,1.428],basis="ANP national average; Sep is the week of 20-26 Sep")
add("AU","Australia","Comparison","Oceania",[1.076,1.205,1.804,1.283,1.308,1.064,1.348,1.459,1.682],[N,1.245,2.261,1.752,1.664,1.218,1.621,1.776,2.019],basis="ACCC five-city average, single day near month-end")
B=dict(brent=[66.60,70.89,103.13,117.29,107.14,85.40,83.76,91.08,116.8,N],
       spot=dict(gasoline=[.542,.522,.758,.856,.922,.796,.866,.878,.988,N],diesel=[.558,.608,1.012,1.034,1.020,.887,1.023,1.112,1.287,N]),
       margin=0.185)
json.dump(dict(months=M,countries=C,bench=B),open(os.path.join(OUT,"data.json"),"w"),separators=(",",":"))
# tidy CSV
with open(os.path.join(OUT,"fuel_prices_tidy.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["country","group","continent","month","period","fuel","price_usd_per_litre","basis"])
    for k,c in C.items():
        for fuel in ("gasoline","diesel"):
            for m,v in zip(M,c[fuel]):
                if v is not None: w.writerow([c["name"],c["group"],c["continent"],m,"pre-war" if m<"2026-03" else "since war",fuel,v,c["basis"]])
with open(os.path.join(OUT,"benchmarks.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["month","brent_usd_per_bbl","usgc_gasoline_spot_usd_per_litre","usgc_diesel_spot_usd_per_litre"])
    for i,m in enumerate(M): w.writerow([m,B["brent"][i],B["spot"]["gasoline"][i],B["spot"]["diesel"][i]])
# ---- checks / KPIs ----
def avg(x):
    x=[v for v in x if v is not None]; return sum(x)/len(x) if x else None
def last(x):
    for v in reversed(x):
        if v is not None: return v
out=[]
for fuel in ("gasoline","diesel"):
    print("=====",fuel)
    ae=[v/1.05 for v in C["AE"][fuel]]
    for k,c in C.items():
        p=c[fuel]; pre=avg(p[:2]); post=avg(p[2:]); la=last(p)
        if pre is None and la is None: continue
        line=f"{c['name']:15s} pre {pre if pre is None else round(pre,3)} post {round(post,3) if post else None} latest {la} chg {None if not pre else round((la/pre-1)*100,1)}%"
        if c["group"]=="Gulf":
            gr=[None if v is None else ae[i]*(1+c["vat"])-v for i,v in enumerate(p)]
            gi=[None if (v is None or B['spot'][fuel][i] is None) else (B['spot'][fuel][i]+.185)*(1+c["vat"])-v for i,v in enumerate(p)]
            vol=c["vol"][fuel]
            line+=f" | REG gap pre {round(avg(gr[:2]),3)} post {round(avg(gr[2:]),3)} latest {round(last(gr),3)} | INT gap pre {avg(gi[:2]) and round(avg(gi[:2]),3)} post {round(avg(gi[2:]),3)}"
            if vol: line+=f" | $bn/yr REG post {round(avg(gr[2:])*vol,1)} INT post {round(avg(gi[2:])*vol,1)} pre REG {round(avg(gr[:2])*vol,1)}"
            out.append([c["name"],fuel,round(avg(gr[:2]),3),round(avg(gr[2:]),3),round(avg(gi[:2]),3) if avg(gi[:2]) is not None else "",round(avg(gi[2:]),3),vol or "",round(avg(gr[2:])*vol,2) if vol else "",round(avg(gi[2:])*vol,2) if vol else ""])
        print(line)
with open(os.path.join(OUT,"subsidy_estimates.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["country","fuel","gap_prewar_regional_usd_l","gap_sincewar_regional_usd_l","gap_prewar_international_usd_l","gap_sincewar_international_usd_l","annual_volume_bn_litres_2023","annualised_subsidy_regional_usd_bn","annualised_subsidy_international_usd_bn"]); w.writerows([[0.0 if isinstance(v,float) and abs(v)<0.005 else v for v in r] for r in out])
