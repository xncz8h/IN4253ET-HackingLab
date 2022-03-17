import json

def main_process(file_name):

    with open(f"out/{file_name}.json", "r") as f:
        data = json.load(f)

    res = {}
    
    for website, cookies in data.items():
        l = []
        for c in cookies:
            if c["third_party"]:
                l.append(c)
        
        
        if l:
            res[website] = l

    with open(f"out/{file_name}-out.json", "w") as f:
        json.dump(res, f, indent=2)

if __name__ == "__main__":
    main_process("universities")