import  pandas  as pd
import math

"""Current Ratio"""
"""Interest Coverage Ratio"""
"""Return on Assets"""
"""Price/Book"""
"""Sales/Working Capital"""

df=pd.read_excel('c:/Users/admin/Desktop/result3.xlsx')
item_name_list = ['Current Ratio', 'Interest Coverage Ratio', 'Return on Assets', 'Price/Book', 'Sales/Working Capital']
mean_list = []
sqrt_DX_list = []
#EXY_list_2d = []
EXY_list_2d = [[3.741358230764316], [128.52310915792907, 4415.0248569608275], [0.20234987716942837, 6.95112142368266, 0.01094401291322254], [7.5330511583267405, 258.77531543297493, 0.40742208646691513, 15.167448892583652], [54.10862970979373, 1858.7392314893596, 2.9264437940080685, 108.9452146974796, 782.5350122843928]]
cov_list_2d = []
r_list_2d = []

#计算单个均值
def cal_mean_by_name(name):
    val = 0.0
    for id in df.index.values:
        val += df[name][id]
    return val / df.index.size

#计算单个EXY
def cal_EXY_by_name(name1, name2):
    val = 0.0
    for i in df.index.values:
        for j in df.index.values:
            val += df[name1][i] * df[name2][j]
    return val / (df.index.size * df.index.size)

#计算单个协方差
#可以通过mean_list和EXY_list_2d来算
def cal_covXY_by_name(name1, name2):
    i = item_name_list.index(name1)
    j = item_name_list.index(name2)
    #EXY = cal_EXY_by_name(name1, name2)
    #EX = cal_mean_by_name(name1)
    #EY = cal_mean_by_name(name2)
    EXY = EXY_list_2d[i][j]
    EX = mean_list[i]
    EY = mean_list[j]
    print("EXY =", EXY)
    print("EX =", EX)
    print("EY =", EY)
    cov = EXY - (EX * EY)
    if (abs(cov) < 1e-6): cov = 0.0
    return cov

#计算单个标准差
def cal_sqrt_DX_by_name(name):
    id = item_name_list.index(name)
    #EXX = cal_EXY_by_name(name, name)
    #EX = cal_mean_by_name(name)
    EXX = EXY_list_2d[id][id]
    EX = mean_list[id]
    DX = EXX - (EX * EX)
    sqrt_DX = math.sqrt(DX)
    return sqrt_DX

#计算均值
def cal_mean_list():
    for name in item_name_list:
        EX = cal_mean_by_name(name)
        mean_list.append(EX)

#cal EXY list_2d
def cal_EXY_list_2d():
    for name1 in item_name_list:
        ans_list = []
        for name2 in item_name_list:
            if (item_name_list.index(name1) < item_name_list.index(name2)): continue
            EXY = cal_EXY_by_name(name1, name2)
            ans_list.append(EXY)
        print(ans_list)
        EXY_list_2d.append(ans_list)

#计算标准差
def cal_sqrt_DX_list():
    for name in item_name_list:
        sqrt_DX = cal_sqrt_DX_by_name(name)
        sqrt_DX_list.append(sqrt_DX)

#计算协方差
def cal_cov_list_2d():
    for name1 in item_name_list:
        ans_list = []
        for name2 in item_name_list:
            if (item_name_list.index(name1) < item_name_list.index(name2)): continue
            covXY = cal_covXY_by_name(name1, name2)
            # print(name1, '&', name2, ':')
            #print('covXY =', covXY)
            ans_list.append(covXY)
        print(ans_list)
        cov_list_2d.append(ans_list)


#计算相关系数
def cal_r_list_2d():
    for name1 in item_name_list:
        ans_list = []
        for name2 in item_name_list:
            i = item_name_list.index(name1)
            j = item_name_list.index(name2)
            if (i < j): continue
            covXY = cov_list_2d[i][j]
            sqrt_DX = sqrt_DX_list[i]
            sqrt_DY = sqrt_DX_list[j]
            r = covXY / (sqrt_DX * sqrt_DY)
            ans_list.append(r)
        print(ans_list)
        r_list_2d.append(ans_list)



if __name__=='__main__':
    print('cal_mean_list:')
    cal_mean_list()
    print('mean list:', mean_list)

    print('cal_EXY_list_2d:')
    #cal_EXY_list_2d()
    print('EXY list:', EXY_list_2d)

    print('cal_cov_list_2d:')
    cal_cov_list_2d()
    print('cov_list_2d:', cov_list_2d)

    print('cal_sqrt_DX_list:')
    cal_sqrt_DX_list()
    print('sqrt_DX_list:', sqrt_DX_list)



    print('cal_r_list_2d:')
    cal_r_list_2d()
    print('r_list_2d:', r_list_2d)
