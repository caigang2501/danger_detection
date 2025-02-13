import datetime,os,string
from collections import deque
from typing import List

class Solution:
    def movesToStamp(self, stamp: str, target: str) -> List[int]:
        ns = [0]
        ans = []
        start = 0
        for c in target:
            nst = []
            for n in ns:
                if n==len(stamp)-1:
                    if stamp[n]==c:
                        nst = [i for i in range(len(stamp))]
                        break
                else:
                    if stamp[n]==c:
                        nst.append(n+1)
                    elif c==stamp[0]:
                        if 1 not in nst:
                            nst.append(1)
            ns = nst
            if not ns:
                return []
            print(ns)

s = Solution()
r = s.movesToStamp("abca", target = "aabcaca")

