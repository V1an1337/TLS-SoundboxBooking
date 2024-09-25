import requests

# 设置服务器URL
url = "http://localhost:5000/getSoundboxState"

# 设置Cookie（包含token）
cookies = {
    'token': 'V1an1337'
}

# 设置Query参数
params = {
    'startDate': '20240923',  # 可选
    'endDate': '20240930'      # 可选
}

# 发送GET请求
response = requests.get(url, cookies=cookies, params=params)

# 检查响应
if response.status_code == 200:
    print("请求成功，数据如下：")
    print(response.json())
elif response.status_code == 401:
    print("未授权，请检查token。")
else:
    print(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
