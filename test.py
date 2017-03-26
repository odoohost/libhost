# -*- coding:utf-8 -*-

import bsddb

users = bsddb.db.DB()
users.open('/etc/vsftpd/users.db',dbtype=bsddb.db.DB_HASH)
print users.items()
users.close()




import commands as cmd
import bsddb

# ftp_name = 'local3'

# users = bsddb.db.DB()
# users.open('/etc/vsftpd/users.db',dbtype=bsddb.db.DB_HASH,flags=bsddb.db.DB_CREATE)
# users.put(ftp_name,'123456')
# users.close()
# (status,output) = cmd.getstatusoutput('echo -n "write_enable=YES\nlocal_root=/odoo/{0}" > /etc/vsftpd/{0}'.format(ftp_name))
# print (status,output.decode('utf-8'))
# cmdline = 'mkdir /odoo/{0} && chown -R vsftpd /odoo/{0} && mkdir /odoo/{0}/extra-addons && chmod 777 /odoo/{0}/extra-addons && mkdir /odoo/{0}/backups && chmod 777 /odoo/{0}/backups'.format(ftp_name)
# (status,output) = cmd.getstatusoutput(cmdline)
# print (status,output.decode('utf-8'))
#
# users = bsddb.db.DB()
# users.open('/etc/vsftpd/users.db',dbtype=bsddb.db.DB_HASH)
# if users[ftp_name] == '123456':
#     users[ftp_name] = '654321'
#     users.close()

# users = bsddb.db.DB()
# users.open('/etc/vsftpd/users.db',dbtype=bsddb.db.DB_HASH)
# del users[ftp_name]
# users.close()
# (status,output) = cmd.getstatusoutput('rm -rf /etc/vsftpd/'+ftp_name)
# #删除主机上的文件夹
# (status,output) = cmd.getstatusoutput('rm -rf /odoo/'+ftp_name)




import libhost

# domain = 'rajasoft.cn' #默认根域名
# cluster_address = 'https://master4g1.cs-cn-shanghai.aliyun.com:19504/projects/' #阿里云容器应用接口地址

host = libhost.Host('', '', '.')
name = 'aaaa'
print host.update_ftp_password(name,'12344321','11111111')
# host._set_json_payload('test1','测试用户','1G','erp.renren.com')
# if host.create(name,'123456','测试用户','512M'): print host.view(name)
# if host.update(name,'测试用户','2G'): print host.view(name)
# if host.stop(name): print host.view(name)
# if host.start(name): print host.view(name)
# print host.view(name)
# host.delete(name)




# import os,sys
# print os.path.abspath(sys.path[0]+'/ca.pem')