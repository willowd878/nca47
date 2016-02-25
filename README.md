# nca47

networking configuration automation

## 项目介绍

## 开发指导手册

### 编程规范

所有提交的项目代码必须符合**python pep8**编程规范。

pep8参考文档：

* [python pep8](https://www.python.org/dev/peps/pep-0008/)
* [pep8中文译本](http://blog.sae.sina.com.cn/archives/4781)

### git配置

配置git bash的用户变量

> git config --global user.name "XXX"

> git config --global user.email "XXX@XXXXXX.com"

使用[官方指导文档](https://help.github.com/articles/generating-an-ssh-key/#platform-windows)的方法，配置git使用的ssh key。

### git commit message规范

所有commit的代码，要求按照如下规范编写commit message：

* 第一行编写本次commit修改的概要，不能超过50字符
* 第二行空行
* 从第三行开始编写本次commit修改的详细描述，需要时描述内容可以分段，详细描述部分每行不能超过72字符，超过72个字符之前必须换行
* commit message使用英文编写

commit message示例

> ML2: Simplified boolean variable check

> <br />

> Currently 'flows' is being checked for empty list in a non standard 

> way 'if flows == []:'. This patch simplifies logic so that above check

> is unnecessary.


