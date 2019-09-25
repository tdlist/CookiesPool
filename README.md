# CookiesPool
一个可扩展的 Cookie池，自带验证码API服务

目前支持站点
------------
* 天眼查
* 企查查
* 启信宝
* 七麦

扩展说明
------------
* 在 login 文件夹中实现待扩展站点的登录和注册脚本, 并在 generator.py 中继承通用生成器, 修改 new_cookies 方法即可。
* 在 tester.py 中继承通用检测器实现待扩展站点 cookies 检测。
* 配置文件 config.py 中 GENERATOR_MAP 添加待扩展站点的账号生成器和 Cookie 生成器, TESTER_MAP 中添加带扩展站点的检测器, TESTER_URL_MAP 中添加待扩展站点的检测 url。
* runner 下添加待扩展站点运行器入口, 如 run_qixinbao.py。

配置说明
-----------
* redies_url： redis 数据库连接, 用来存储账号和cookies。
* proxy_url：某些站点对单IP的账号注册登录有限制, 使用代理注册登录。
* yima_token: 易码平台账号认证, 手机号获取和短信获取服务 API 都需要该参数, 如果没有易码平台账号, 请先注册一个, 或者关闭账号注册服务。
* chaojiying_account: 超级鹰账号密码, 用来识别简单图文验证码, 请修改成自己的

使用说明
------------
* 修改所有配置参数为自己的, 并保证可用。
* 运行 GeetestCracker 滑动验证码服务器: run.py。若放在服务器上运行, 需修改 API 地址为服务器地址。
* 运行 runner 下的 run_xxx.py。
* 运行 api.py。
* 获取cookies: resp = requests.get('http://********:8778/qimai/random')
