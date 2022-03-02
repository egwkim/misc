"""
수학의 정석 수1 실력 p.218 연습문제 15-5
어떤 단세포 생물의 집단은 1분마다 30%가 죽고, 나머지는 각각 두 마리로 분열한다고 한다.
처음 10마리의 단세포 생물의 수가 처음으로 1000마리 이상이 되는 것은 몇 분 후인가?

계산 과정에서 집단의 30%가 실수가 나오는데, 이를 계산하는 방법에 따라 세 경우로 나눴다.
a: 30%를 내림으로 계산 (최고값)
b: 생물의 수를 실수로 계산
c: 30%를 올림으로 계산 (최저값)
"""

import math

a = 10
b = 10
c = 10

for i in range(100):
    a = (a - math.floor(a * 0.3)) * 2
    b = b * 1.4
    c = (c - math.ceil(c * 0.3)) * 2
    print(a, b, c)