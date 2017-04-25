# ProxyPool

---
[Read in English(阅读英文版本)](README.md)

一个采用Python实现的代理池工具。

`ProxyPool`是一个基于[Scrapy](https://scrapy.org)和[Redis](http://redis.io)的自有代理池创建工具，该工具将会自动将可用代理添加至代理池及维护并删除代理池中不可用代理。

该工具目前只从三个数据来源获取代理IP，未来我将会添加更多数据来源。

## 兼容性

该工具在**macOS Sierra 10.12.4**和**Ubuntu 16.04 LTS**系统上进行了测试。

系统依赖:

* UNIX类系统(macOS、Ubuntu等)

基础依赖:

* Redis 3.2.8
* Python 3.0+

Python第三方模块依赖:

* Scrapy 1.3.3
* redis 2.10.5

我并未对以上第三方模块的其他版本进行测试，但是我认为对大多数用户使用的版本来说都可以兼容。

## 特点

* 自动将可用代理添加至代理池
* 自动从代理池中删除不可用代理
* 添加更多代理来源的可扩展性

## 操作流程

要启动该工具，请于命令行输入:
> $ ./start.sh

该命令将会启动*代理池维护进程*和*代理爬虫进程*

要停止该工具，请于命令行输入:
> $ sudo ./stop.sh

要添加对更多代理数据来源的爬取支持:

1. 切换工作目录到**spiders**下

	> $ cd ProxyCrawl/ProxyCrawl/spiders

2. 使用scrapy内置命令创建一个新的spider:

	> $ scrapy genspider [spider_name] [site_domain]

	或者你也可以自己创建一个新的`.py`文件

3. 打开新生成的`.py`文件更改其继承为`base_spider.BaseSpider`(如果你想添加的网站结构跟预置的不一致，你可以编写自己的逻辑)

4. 重写`url_fmt`属性以及`parse`方法以符合现有逻辑的要求。
	* `url_fmt`将会用于格式化生成待爬取页面，免费代理提供网站的编码规则一般都是`xxx.com/yy/5`
	* `parse`方法应该处理对响应内容的解析以在`items.py`中定义的结构生成新的`ProxyItem`对象

5. 完成，剩下的工具将会由该工具完成，下面就直接启动该工具吧。

## Redis数据格式

所有的代理数据信息都存储在Redis中，如何配置Redis对于本工具来说并不重要。

### proxy_info(有序集合)

键|描述
:---|:---
proxy|完整代理地址，格式: 127.0.0.1:80
ip|代理IP，格式: 127.0.0.1
port|代理端口，格式: 80
addr|代理的实际地址
mode|是否匿名
protocol|HTTP还是HTTPS
validation_time|来源站点检查时间
failed_times|最近一次连接成功后连接失败次数
latency|跟来源站点的延迟

### rookies_proxies(集合)

新的还未被测试的代理将会被存放于此，一个能成功连接的新代理将会被移动到`available_proxies`或者在达到最大失败重试次数后被移除。

### available_proxies(集合)

所有当前可用代理将会存放于此，每一个代理都将在特定时间被维护进程维护。

### availables_checking(有序集合)

当前可用代理维护队列，这些代理在有序集合中的分值为一个指示优先级的时间戳。

### rookies_checking(有序集合)

新代理维护队列，与`availables_checking`相似。

## 工作原理

### 获取新代理

1. 爬取指定页面
2. 从响应页面中提取`ProxyItem`
3. 将新的`ProxyItem`的对象存入Redis

### 代理池维护

**对于新代理**:

* 依次遍历每一个新代理
	* 可用	
		* 移至`available_proxies`
	* 不可用 
		* 删除该代理

**对于可用代理**:

* 依次遍历每一个代理
	* 可用	
		* 重置`failed_times`并等待下一次检查
	* 不可用 
		* 未达到最大失败重试次数
			* 尽快进行下一次检查
		* 达到最大失败重试次数
			* 删除该代理

要获得当前可用代理，使用任意Redis客户端从`available_proxies`中获取即可。