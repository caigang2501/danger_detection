from collections import deque

def wardrobeFinishing( m: int, n: int, cnt: int) -> int:
    if m+n-2>cnt:
        a,b = max(cnt+1-m,0),max(cnt+1-n,0)
        print(a,b)
        return (cnt+1+1)*(cnt+1)//2-(a+1)*a//2-(b+1)*b//2
    else:
        return m*n

def wardrobeFinishingbfs(m: int, n: int, cnt: int) -> int:
    # 计算数字 x 的数位之和
    def digit_sum(x):
        return sum(map(int, str(x)))

    # 广度优先搜索
    def bfs():
        queue = deque([(0, 0)])  # 初始化队列，起点为 (0, 0)
        visited = set()  # 记录已访问的格子
        count = 0  # 统计满足条件的格子数量

        while queue:
            i, j = queue.popleft()
            # 如果超出边界或已经访问过，跳过
            if i >= m or j >= n or (i, j) in visited or digit_sum(i) + digit_sum(j) > cnt:
                continue
            # 标记当前格子为已访问
            visited.add((i, j))
            count += 1
            # 将右和下方向的格子加入队列
            queue.append((i + 1, j))
            queue.append((i, j + 1))

        return count

    return bfs()

r = wardrobeFinishingbfs(11,8,16)

print(r)

