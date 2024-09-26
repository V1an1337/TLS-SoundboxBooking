# SoundboxBooking

TLS Soundbox Booking Project

# MySQL配置

```
username: soundbox
password: V1an1337
host: localhost
```

# SoundboxBooking-Main

安装Python库：


```pip -r requirements.txt```

如果你拥有python2，使用：
```pip3 -r requirements.txt```

初始化数据库：

```
python init_db.py
python insert_data.py
```

# 测试：

添加测试数据以及启动服务器

```
python insert_data_1day.py
python server.py
```

接着使用apifox进行测试（十分推荐！！！）  
或者启动getSoundboxState-Client.py (不推荐)

```
python getSoundboxState-Client.py
```

# Ms-identity-python-webapp-master

这个文件夹是Microsoft graph的登录示例，appID和Key已经包含在配置文件中，下载可以直接用。requirements.txt在文件夹里面有一个单独的，记得pip

启动服务器

```
python app.py
```

然后访问http://localhost:5000

* 注意！SoundboxBooking server不可以和Ms-identity-python-webapp-master一起启动！（因为共用5000端口）
