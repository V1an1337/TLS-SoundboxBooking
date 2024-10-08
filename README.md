# SoundboxBooking

This repository refers to TLS Soundbox Booking Project

# MySQL Configuration

Create user "soundbox" with corresponding password:
```
username: soundbox
password: V1an1337
host: localhost
```

# Run SoundboxBooking

Install python libraries：


```pip -r requirements.txt```

If you already installed python2, use：  
```pip3 -r requirements.txt```

Initialise the database：

```
python init_db.py
```

# Test：

Add test data and run the server (It will automatically add data of future weekdays):
```
python server.py
```
When the program ask you to choose HTTP/HTTPS, choose as you like.  
However, if you want to enable HTTPS, please change fullchain.pem and privkey.key to your own certificate.  

Use apifox to test APIs

# Ms-identity-python-webapp-master

这个文件夹是一个单独的Microsoft graph登录示例，appID和Key已经包含在配置文件中，下载可以直接用。  
启动服务器

```
python app.py
```

然后访问http://localhost:5000

* 注意！SoundboxBooking server不可以和Ms-identity-python-webapp-master一起启动！（因为共用5000端口）
