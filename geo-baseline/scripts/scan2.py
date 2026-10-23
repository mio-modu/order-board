import json, urllib.request, re
from concurrent.futures import ThreadPoolExecutor
exec(open('scan.py').read().split('A=scan(')[0])   # ask / gen_questions / detect / scan 재사용

R={}
R['calc']=scan("계산모아 — 생활 계산기 카테고리",
  "연봉 실수령액·적금 복리·대출이자·부가세 같은 생활 계산기를 웹에서 찾아 쓰는 상황",
  [["계산모아","gyesanmoa"],["사람인","saramin"],["잡코리아"],["네이버 임금계산기","네이버 계산기"],
   ["토스","toss"],["뱅크샐러드"],["찾아줘세무사"],["국세청 홈택스","홈택스"]], 12)

R['gov']=scan("받을돈 — 정부지원금 찾기 카테고리",
  "근로장려금·청년월세·부모급여 등 내가 받을 수 있는 정부지원금을 찾는 상황",
  [["받을돈","badeuldon"],["정부24"],["복지로"],["보조금24"],["토스","toss"],
   ["뱅크샐러드"],["카카오페이"],["국세청 홈택스","홈택스"]], 12)

json.dump({k:v[1] for k,v in R.items()}, open("scan2_result.json","w"), ensure_ascii=False)
