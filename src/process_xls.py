import  pandas  as pd

#方法一：默认读取第一个表单
df=pd.read_excel('c:/Users/admin/Desktop/19年NYSE财务数据综合.xlsx')#这个会直接默认读取到这个Excel的第一个表单
data=df.head()#默认读取前5行的数据
#print("获取到所有的值:\n{0}".format(data))#格式化输出
#print("获取到所有的值:\n{0}".format(df))

#data=df.ix[0,2].values#0表示第一行 这里读取数据并不包含表头，要注意哦！
#print("读取指定行的数据：\n{0}".format(data))


#print(df['Price/Book'])
#print(df['Price/Book'][1])

#df['new_col'] = df['Total Debt/Total Assets'] * 2
#print("获取到所有的值:\n{0}".format(df))
"""Return on Assets"""
"""Interest Coverage Ratio"""
"""Cash Ratio"""
"""Current Ratio"""
"""Asset Turnover"""
"""Sales/Working Capital"""
"""Price/Book"""
"""Total Debt/Total Assets"""
pre_no = df['PERMNO'][0]
print(pre_no)
res = []
ROA=0.0
ICR=0.0
CR=0.0
CUR=0.0
AT=0.0
SWC=0.0
PB=0.0
TDTA=0.0
for id in df.index.values:
#for id in range(20):
    #print(id)
    if df['PERMNO'][id] == pre_no:
        #print(df['PERMNO'][id])
        ROA += df['Return on Assets'][id]
        #print(ROA)
        ICR += df['Interest Coverage Ratio'][id]
        CR += df['Cash Ratio'][id]
        CUR += df['Current Ratio'][id]
        AT += df['Asset Turnover'][id]
        SWC += df['Sales/Working Capital'][id]
        PB += df['Price/Book'][id]
        TDTA += df['Total Debt/Total Assets'][id]
    else:
        #print(df['PERMNO'][id])
        #print(ROA)
        res.append([pre_no, round(ROA/12.0, 3), round(ICR/12.0, 3), round(CR/12.0, 3), round(CUR/12.0, 3), round(AT/12.0, 3), round(SWC/12.0, 3), round(PB/12.0, 3), round(TDTA/12.0, 3)])
        pre_no = df['PERMNO'][id]

        ROA = df['Return on Assets'][id]
        ICR = df['Interest Coverage Ratio'][id]
        CR = df['Cash Ratio'][id]
        CUR = df['Current Ratio'][id]
        AT = df['Asset Turnover'][id]
        SWC = df['Sales/Working Capital'][id]
        PB = df['Price/Book'][id]
        TDTA = df['Total Debt/Total Assets'][id]
    pass

res.append([pre_no, round(ROA/12.0, 3), round(ICR/12.0, 3), round(CR/12.0, 3), round(CUR/12.0, 3), round(AT/12.0, 3), round(SWC/12.0, 3), round(PB/12.0, 3), round(TDTA/12.0, 3)])
#with open("c:/Users/admin/Desktop/result.txt", "w") as f:
    #for line in res:
        #print(str(line))
        #f.write(str(line)+"\n")

df2 = pd.DataFrame(res, columns=['PERMNO', 'Return on Assets', 'Interest Coverage Ratio', 'Cash Ratio', 'Current Ratio','Asset Turnover','Sales/Working Capital','Price/Book','Total Debt/Total Assets'])

df2.to_excel('c:/Users/admin/Desktop/result3.xlsx')