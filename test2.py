

result = [0,0,0,1,1,0]
start = False
warning = False
filed_result = []
for j,n in enumerate(result):
    if start:
        if n!=0 and not warning:
            if j-i>=1:
                filed_result.append((i+j)//2)
                file_name = f"frame_{(i+j)//2}.jpg"
                warning = True
        else:
            start = False
            warning = False
    else:
        if n>=1:
            i = j
            start = True

print(filed_result)