#           Preprocessing

import pandas as pd
import numpy as np
df = pd.read_excel(r'交易資料集.xlsx')

#數量 0 or 負 表示退貨、註銷 需剔除
df_fin = df.drop(df[df['QUANTITY']<=0].index)

#刪除其他不相干欄位
df_fin = df_fin.drop(columns=['CUST_ID'])
df_fin = df_fin.drop(columns=['ITEM_ID'])
df_fin = df_fin.drop(columns=['ITEM_NO'])
df_fin = df_fin.drop(columns=['TRX_DATE'])


df_fin = (df_fin.groupby(['INVOICE_NO', 'PRODUCT_TYPE'])['QUANTITY']
          .sum().unstack().reset_index().fillna(0)
          .set_index('INVOICE_NO'))

dele = (df_fin.iloc[:,1:]>0).sum(axis=1) == 1

df_fin = df_fin.drop(df_fin[dele].index)
#檢查
#print(df_fin)

#df_fin.to_csv("preprocess.csv", encoding="utf-8")

#ohe

def ohe(x):
    if(x>0):
        return 1
    else:
        return 0

df_fin_ohe = df_fin.applymap(ohe)

data = df_fin_ohe

#           apriori

from apyori import apriori
from mlxtend.frequent_patterns import apriori, association_rules
from time import time

apristart = time()

frq_items = apriori(data, min_support = 0.00375, use_colnames = True)
# print(frq_items)

rules = association_rules(frq_items, metric='confidence', min_threshold=0.8)
#print(rules)
apritime = time() - apristart
print("Apriori花費時間:"+str(apritime))
rules_df = pd.DataFrame(rules)
rules_df.to_csv("apriori_rules.csv", encoding="utf-8", index=False)

#      user input predict

def string_to_list(string):
    string = string.replace("frozenset({'", "")
    string = string.replace("'})", "")
    string = string.replace("'", "")
    string = string.split(", ")
    return string

rules_a = pd.read_csv(r'apriori_rules.csv')

uinput = input("Apriori 請輸入一串商品 用,分隔:")
item = uinput.split(',')
prediction_items = list(map(str,item))

item = []
item = set(item)

for index, row in rules_a.iterrows():
    rules = string_to_list(row['antecedents'])
    if set(prediction_items).issubset(rules):
        item.update(string_to_list(row['consequents']))

print("you may buy"+str(item))

from mlxtend.frequent_patterns import fpgrowth

fpg0 = time()
fpg_items = fpgrowth(data, min_support=0.00375, use_colnames=True)
#print(fpg)
rules = association_rules(fpg_items, metric='confidence', min_threshold=0.8)
#print(rules)
fpgtime= time()-fpg0
print("FP-growth花費時間:"+str(fpgtime))
rules_df=pd.DataFrame(rules)
rules_df.to_csv("fpg_rules.csv", encoding="utf-8", index=False)

#print(rules)

rules_f = pd.read_csv(r'fpg_rules.csv')

uinput = input("FP-growth 請輸入一串商品 用,分隔:")
item = uinput.split(',')
prediction_items = list(map(str,item))

item = []
item = set(item)

for index, row in rules_f.iterrows():
    rules = string_to_list(row['antecedents'])
    if set(prediction_items).issubset(rules):
        item.update(string_to_list(row['consequents']))

print("you may buy"+str(item))