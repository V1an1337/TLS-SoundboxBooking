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
python insert_data.py
```

# Test：

Add test data and run the server:
```
python insert_data_1day.py
python server.py
```

Use apifox to test APIs

# Ms-identity-python-webapp-master

这个文件夹是一个单独的Microsoft graph登录示例，appID和Key已经包含在配置文件中，下载可以直接用。  
启动服务器

```
python app.py
```

然后访问http://localhost:5000

* 注意！SoundboxBooking server不可以和Ms-identity-python-webapp-master一起启动！（因为共用5000端口）
