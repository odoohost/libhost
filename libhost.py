#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests as req
import commands as cmd
import bsddb
import time
import json
import os


class Host:

    def __init__(self, path, prod=False):
        self.VERIFY = os.path.abspath(path+'/ca.pem')
        self.CERT = (os.path.abspath(path+'/cert.pem'),os.path.abspath(path+'/key.pem'))
        self.PROD = prod
        if prod:
            self.IMAGE = 'registry-vpc.cn-hangzhou.aliyuncs.com/odoohost/odoo10'
            self.DOMAIN = 'rajasoft.cn'
            self.CLUSTER_ADDRESS = 'https://master4g4.cs-cn-hangzhou.aliyun.com:13121/projects/'
            self.HOST_BASE_DIR = '/mnt/acs_mnt/nas/odoo'
        else:
            self.IMAGE = 'registry.cn-hangzhou.aliyuncs.com/odoohost/odoo10'
            self.DOMAIN = 'youbaninfo.com'
            self.CLUSTER_ADDRESS = 'https://master4g1.cs-cn-shanghai.aliyun.com:19504/projects/'
            self.HOST_BASE_DIR = '/odoo'
        
    #查询
    def view(self, name):
        res = req.get(self.CLUSTER_ADDRESS+name, verify=self.VERIFY, cert=self.CERT)
        return json.loads(res.content)

    #创建
    #name实例名称不能重复
    #customer客户名称
    def create(self, name, password, customer, memory):
        # #创建文件夹,ftp目录，也是容器卷，设置用户vsftpd增加安全性
        cmdline = 'mkdir -p /odoo/customers/{0}/extra-addons && chmod 777 /odoo/customers/{0}/extra-addons && mkdir /odoo/customers/{0}/data  && chmod 777 /odoo/customers/{0}/data'.format(name)
        (status , output) = cmd.getstatusoutput(cmdline)
        print (status, output)
        #创建容器
        json_payload = self._set_json_payload(name=name, customer=customer, memory=memory)
        res = req.post(self.CLUSTER_ADDRESS,json=json_payload, verify=self.VERIFY, cert=self.CERT)
        print (res.status_code, res.content)
        if res.status_code == req.codes.created:
            #创建FTP帐号并限定主目录
            users = bsddb.db.DB()
            users.open('/etc/vsftpd/users.db',dbtype=bsddb.db.DB_HASH,flags=bsddb.db.DB_CREATE)
            users.put(name, password)
            users.close()
            (status,output) = cmd.getstatusoutput('echo -n "write_enable=YES\nlocal_root=/odoo/{0}" > /etc/vsftpd/{0}'.format(name))
            print (status, output)
            return True
        return False

    #删除
    #到期后7天执行删除
    def delete(self, name):
        #删除容器
        res = req.delete(self.CLUSTER_ADDRESS+name+'?force=true&v=true', verify=self.VERIFY, cert=self.CERT)
        print (res.status_code, res.content)
        if res.status_code == req.codes.ok:
            #删除FTP账号
            try:
                users = bsddb.db.DB()
                users.open('/etc/vsftpd/users.db',dbtype=bsddb.db.DB_HASH)
                del users[name]
            finally:
                users.close()
            (status,output) = cmd.getstatusoutput('rm -rf /etc/vsftpd/'+name)
            print (status, output)
            #删除主机上的文件夹
            (status,output) = cmd.getstatusoutput('rm -rf /odoo/'+name)
            print (status, output)
            return True
        return False

    #更新
    #更新内存
    #更新用户自定义域名，不自定义可以使用“实例名.根域名”
    def update(self, name, customer, memory, uri=None):
        json_payload = self._set_json_payload(name,customer,memory,uri)
        res = req.post(self.CLUSTER_ADDRESS+name+'/update',json=json_payload, verify=self.VERIFY, cert=self.CERT)
        print (res.status_code, res.content)
        if res.status_code == req.codes.accepted:
            return True
        return False

    #更新FTP密码
    @staticmethod
    def update_ftp_password(name, newpwd, oldpwd):
        users = bsddb.db.DB()
        users.open('/etc/vsftpd/users.db',dbtype=bsddb.db.DB_HASH)
        if users[name] == oldpwd:
            users[name] = newpwd
            users.close()
            return True
        users.close()
        return False


    #启动
    def start(self, name):
        res = req.post(self.CLUSTER_ADDRESS+name+'/start', verify=self.VERIFY, cert=self.CERT)
        print (res.status_code, res.content)
        if res.status_code == req.codes.ok:
            return True
        return False

    #停止
    def stop(self, name):
        res = req.post(self.CLUSTER_ADDRESS+name+'/stop', verify=self.VERIFY, cert=self.CERT)
        print (res.status_code, res.content)
        if res.status_code == req.codes.ok:
            return True
        return False

    #终止，阿里云提供的接口，但没有明确什么时候使用
    def kill(self, name):
        res = req.post(self.CLUSTER_ADDRESS+name+'/kill', verify=self.VERIFY, cert=self.CERT)
        print (res.status_code, res.content)
        if res.status_code == req.codes.ok:
            return True
        return False

    def _set_json_payload(self, name, customer,memory, uri=None):
        #支持双uri,一是由“实例名.根域名”组成，二是由用户指定
        uri_proxy = uri_routing = name+'.'+self.DOMAIN
        if uri:
            uri_proxy += ','+uri
            uri_routing += ';'+uri

        #备忘：当使用NAS后无法映射到主机目录，目录总为空
        template = """{0}:
        expose:
            - 8069/tcp
        image: '{4}'
        mem_limit: {1}
        environment:
            - 'ODOO_RC=/etc/odoo/odoo.conf'
            - 'PGDATA=/var/lib/postgresql/data'
            - 'HOST_BASE_DIR={5}'
            - 'INSTANCE_NAME={0}'
        labels:
            aliyun.proxy.VIRTUAL_HOST: '{2}'
            aliyun.routing.port_8069: '{3}'
            aliyun.scale: '1'
        restart: always""".format(name, memory, uri_proxy, uri_routing, self.IMAGE, self.HOST_BASE_DIR)
        print template

        payload = {
            "name": name,
            "description": customer,
            "template": template,
            "version": time.strftime('%y%m%d%H%M%S')
        }
        return payload
