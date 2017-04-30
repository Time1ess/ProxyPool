# ProxyPool

---
> 目前该工具处于开发中，`README`文档可能不能及时更新。
[Read in English(阅读英文版本)](README.md)

一个采用Python实现的代理池工具。

`ProxyPool`是一个基于[Scrapy](https://scrapy.org)和[Redis](http://redis.io)的自有代理池创建工具，该工具将会自动将可用代理添加至代理池及维护并删除代理池中不可用代理。

该工具目前只从四个数据来源获取代理IP，未来我将会添加更多数据来源。

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
* Flask 0.12

我并未对以上第三方模块的其他版本进行测试，但是我认为对大多数用户使用的版本来说都可以兼容。

## 特点

* 自动将可用代理添加至代理池
* 自动从代理池中删除不可用代理
* 通过指定爬取规则减少编写代码工作，提高可扩展性

## 操作流程

要启动该工具，请于命令行输入:
> $ ./start.sh

该命令将会启动*代理爬取任务*、*代理池维护任务*、*维护调度任务*、*规则维护任务*以及*网页控制台*

要停止该工具，请于命令行输入:
> $ sudo ./stop.sh

要添加对更多代理数据来源的爬取支持，本工具提供了一种较为常见的爬取结构，支持大多数免费代理网站结构:

1. 启动工具
2. 打开[网页控制台](http://localhost:5000)(默认端口:5000)
3. 切换至**规则管理**页面
4. 点击**添加新规则**按钮
5. 完成表单填写并提交
	* `规则名`用于区分不同规则，
	* `URL格式`将会用于格式化生成待爬取页面，免费代理提供网站的编码规则一般都是`xxx.com/yy/5`
	* `行模式`将会用于从页面内容中提取一个数据行
	* `代理ip模式`将会用于从之前提取的数据行中提取代理ip
	* `代理端口模式`将会用于提取代理端口
	* `代理地址模式`将会用于提取代理地址
	* `代理类型模式`将会用于提起代理工作模式
	* `代理协议模式`将会用于提取代理协议
	* `验证时间模式`将会用于提取代理验证时间
	* `最大页面数量`将会控制待爬取页面数量
	* 以上的`模式`可以被设置为`null`以注明使用默认值`unknown` 
6. 提交表单后该规则将会自动应用并开始爬取

## Redis数据格式

本工具所有的数据信息都存储在Redis中。

### Rule(散列)

键|描述
:---|:---
name|规则名
url_fmt|URL格式
row_xpath|行模式
host_xpath|代理ip模式
port_xpath|代理端口模式
addr_xpath|代理地址模式
mode_xpath|代理类型模式
proto_xpath|代理协议模式
vt_xpath|验证时间模式
max_page|最大页面数量

### proxy_info(散列)

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

### Jobs(列表)

FIFO队列，格式为:`cmd|rule_name`，用于指示*规则维护任务*处理规则对应爬虫的开始、暂停、停止、删除等操作。

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

## 为其他应用获取可用代理
要获得当前可用代理，使用任意Redis客户端从`available_proxies`中获取即可。
一个scrapy中间件示例:

```Python
class RandomProxyMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        s.conn = redis.Redis(decode_responses=True)
        return s

    def process_request(self, request, spider):
        proxies = list(self.conn.smembers('available_proxies'))
        if proxies:
            while True:
                proxy = choice(proxies)
                if proxy.startswith('http'):
                    break
            request.meta['proxy'] = proxy
```
