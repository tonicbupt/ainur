# Ainur

Web UI for Eru.

# Run

## Dependencies

* Redis
* MySQL

# Dev Config

## User

若数据库中用户表为空, 需要登入一次内网 OpenID, 产生一个用户.

然后, 登入数据库, 手动将用户的 `priv_flags` 设置为 7, 则该用户具有管理员和 LB 配置权限. 然后注销并重新登入一次, 便可访问所有页面.
