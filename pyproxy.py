#!/bin/python2.7
#coding:utf-8
import socket
import threading
import base64
bind_host='0.0.0.0'
port=8881
#server_list=("192.168.128.134","192.168.128.131")
not_log_type=('ico','gif','jpg','png','js','html')

proxy_sock_to_client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_sock_to_client.bind((bind_host,port))
proxy_sock_to_client.listen(100)

print "lisenting:%s:%d" %(bind_host,port)
#print "only forward to server_list",server_list



def log(url,post_data,alldata_from_server):
    #只存储请求url类型 在proxy_type中的请求
    if url.split(".")[-1]  in not_log_type:
        print "not log %s" % url
    else:
        with open('log.csv','a+') as hand:
            hand.write('%s,%s,%s\n' %(url,post_data,base64.b64encode(alldata_from_server)))
            print "log:%s\t%s" %(url,post_data)


def deal_request(conn,addr):
    try:
        #接收客户端请求数据
        data_client = conn.recv(4096)
        alldata_client=data_client
        #解析client请求
        header=alldata_client.split("\r\n")
        method=header[0].split(" ")[0]
        url = header[0].split(" ")[1]
        host=url.split("/")[2]

        if method=="POST":
            postdata=header[-1]
        else:
            postdata="GET"

        if ":" in host:
            port=int(host.split(":")[1])
            host=host.split(":")[0]
        else:
            port=80

        #只转发和回传host在server_list中的请求
        if True:
        #if (host in server_list):
            #
            print "%s\t%s\t%s" % (method, host, url)
            # 转发client请求到server
            proxy_sock_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_sock_to_server.connect((host, port))
            proxy_sock_to_server.sendall(alldata_client)
            #接收server数据并转发到client
            alldata_from_server=''
            count=0
            while True:
                data_from_server = proxy_sock_to_server.recv(4096)
                count+=1
                if data_from_server:
                    conn.send(data_from_server)
                    alldata_from_server+=data_from_server
                    #print "send data to client %d time ,data_length:%d" % (count, len(data_from_server))
                else:
                    #print "got alldata from server:%s to client:%s success!" % (host, addr[0])
                    break
            #关闭连接并保存信息
            
            proxy_sock_to_server.shutdown(2)
            proxy_sock_to_server.close()
            conn.shutdown(2)
            conn.close()
            log(url, postdata, alldata_from_server)

            #print "close connection bettween  client:%s and server:%s" % (addr[0], host)
        else:
            pass
    except Exception as e:
        with open("exception.log",'a') as hand:
            #print "exception:%s\n" %(str(e))
            hand.writelines("exception:%s" %str(e))


while True:
    try:
        conn,addr=proxy_sock_to_client.accept()
        threading.Thread(target=deal_request,args=(conn,addr)).start()
    except Exception as e:
        print e
