import tkinter as tk
from tkinter import scrolledtext
import re
import json
import requests
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("输入与日志展示")
        self.root.geometry("800x600")  # 设置窗口大小

        # 输入框：noneedcolor
        tk.Label(root, text="不需要的颜色，默认全都要，英文逗号分隔，举例 Blue,Purple:").pack(pady=5)
        self.entry_noneedcolor = tk.Entry(root)
        self.entry_noneedcolor.pack(pady=5)

        # 输入框：needmem
        tk.Label(root, text="需要的内存规格，默认128G，英文逗号分隔，举例 128G,256G:").pack(pady=5)
        self.entry_needmem = tk.Entry(root)
        self.entry_needmem.pack(pady=5)

        # 提交按钮
        submit_button = tk.Button(root, text="提交", command=self.submit_values)
        submit_button.pack(pady=10)

        # 日志展示区域
        self.log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=50, width=100)
        self.log_text.pack(pady=10)
        self.log_text.config(state=tk.DISABLED)  # 设置为只读模式

    def log_message(self, message):
        """向日志区域添加一条消息"""
        self.log_text.config(state=tk.NORMAL)  # 暂时启用编辑
        self.log_text.insert(tk.END, message + "\n")  # 插入消息
        self.log_text.see(tk.END)  # 滚动到最新内容

    def submit_values(self):
        """获取用户输入并处理"""
        noneedcolor = self.entry_noneedcolor.get().strip()
        needmem = self.entry_needmem.get().strip()

        # 检查输入是否为空
        # if not noneedcolor or not needmem:
        #     self.log_message("错误：请输入两个值！")
        #     return

        # 处理输入并记录日志
        self.log_message(f"不需要的颜色: {noneedcolor}")
        self.log_message(f"需要的内存规格: {needmem}")
        
        no_need_color = set()
        if len(noneedcolor)>0:
            for color in noneedcolor.split(","):
                no_need_color.add(color)
        need_mem = set()
        if len(needmem)>0:
            for mem in needmem.split(","):
                need_mem.add(mem)
        # cookie = args.cookie
        headers = {"Content-type": "application/json",
                # "Cookie": cookie,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        listUrl = 'https://www.apple.com/shop/refurbished/iphone/iphone-14-iphone-14-pro'
        host = 'https://www.apple.com'
        response = requests.post(listUrl, headers=headers)
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            exit()
        # 提取网页内容
        html_content = response.text

        # 使用正则表达式匹配 <script> 标签中的内容
        pattern = r'window\.REFURB_GRID_BOOTSTRAP\s*=\s*({.*?});'
        match = re.search(pattern, html_content, re.DOTALL)

        if not match:
            print("未找到 window.REFURB_GRID_BOOTSTRAP 的定义")
            exit()

        # 提取 {} 中的内容
        json_data = match.group(1)

        # 将 JSON 数据解析为 Python 对象
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            exit()
        detailJsonUrl = "https://www.apple.com/shop/fulfillment-messages?little=false&parts.0={partNumber}&mts.0=regular&fts=true"
        for title in data["tiles"]:
            detailUrl = title["productDetailsUrl"]
            partNumber = title["partNumber"]
            name = title["title"]
            needSkip = False
            for color in no_need_color:
                if color in detailUrl:
                    needSkip = True
                    break
            hasMemExist = False
            for mem in need_mem:
                if mem in detailUrl or mem.lower() in detailUrl:
                    hasMemExist= True
                    break
            if not hasMemExist:
                needSkip= True
            if needSkip:
                continue
            response = requests.get(detailJsonUrl.format(partNumber=partNumber), headers=headers)
            detail= response.json()
            if detail["body"]["content"]["deliveryMessage"][partNumber]["regular"]["isBuyable"] == True:
                printData= "{name}有库存，购买链接: {detailUrl}".format(name=name,detailUrl=host+detailUrl)
                self.log_message(printData)
    

# 创建主窗口并运行应用
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()