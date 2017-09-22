#!/bin/python2.7
#coding:utf-8
import socket
import threading
import base64
import time
bind_host='0.0.0.0'
port=8881
#server_list=("192.168.128.134","192.168.128.131")
not_log_type=('ico','gif','jpg','png','js','html')

proxy_sock_to_client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_sock_to_client.bind((bind_host,port))
proxy_sock_to_client.listen(10000)

print "lisenting:%s:%d" %(bind_host,port)
print "only forward to server_list",server_list



def log(uri,post_data,alldata_from_server):
    #只存储请求url类型 在proxy_type中的请求
    if uri.split(".")[-1]  in not_log_type:
        print "not log %s" % uri
    else:
        with open('log.csv','a+') as hand:
            hand.write('%s,%s,%s\n' %(uri,post_data,base64.b64encode(alldata_from_server)))
            print "log:%s\t%s" %(uri,post_data)
#接收原始的httprequest,返回请求的字典，dic['method'],dic['uri'],dic['postdata'],其他如Host，需要主要大小写，与http协议一致
def get_header_dic(client_http_requests):
    dic = {}
    #第一次分割，将请求分为请求头和消息体
    header=client_http_requests.split("\r\n\r\n",1)
    dic['postdata']=header[1]
    #第二次分割，将请求头以“换行符”作分割，每行存在数组中
    header=header[0].split("\r\n")
    header_lines_count=len(header)
    method=header[0].split(" ")[0]
    uri=header[0].split(" ")[1]
    dic['method']=method
    dic['uri']=uri

    for x in range(1,header_lines_count-2):
        line=header[x]
        line = line.split(":",1)
        dic[line[0]] = line[1]
    return dic

def deal_request(conn,addr):
    try:
        #接收客户端请求数据
        data_client = conn.recv(4096)
        header_dic=get_header_dic(data_client)
        #解析client请求
        host=header_dic['Host'].strip()
        uri=header_dic['uri']
        method=header_dic['method']
        postdata=header_dic['postdata']

        if ":" in host:
            port=int(host.split(":")[1])
            host=host.split(":")[0]
        else:
            port=80

        #只转发和回传host在server_list中的请求i
        if True:
        #if (host in server_list):
            #
            print "%s\t%s\t%s" % (method, host, uri)
            # 转发client请求到server
            proxy_sock_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_sock_to_server.connect((host, port))
            proxy_sock_to_server.sendall(data_client)
            #接收server数据并转发到client
            alldata_from_server=''
            count=0
            while True:
                data_from_server = proxy_sock_to_server.recv(4096)
                count+=1
                if data_from_server:
                    conn.send(data_from_server)
                    alldata_from_server+=data_from_server
                    print "send  to client %d time#####data_length:%d#####from:%s" % (count, len(data_from_server),uri)
                else:
                    #print "got alldata from server:%s to client:%s success!" % (host, addr[0])
                    break
            #关闭连接并保存信息
            #log(uri, postdata, alldata_from_server)
            proxy_sock_to_server.shutdown(socket.SHUT_RDWR)
            proxy_sock_to_server.close()
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()


            #print "close connection bettween  client:%s and server:%s" % (addr[0], host)
        else:
            pass
    except Exception as e:
        print e
        with open("exception.log",'a') as hand:
            #print "exception:%s\n" %(str(e))
            hand.writelines("exception:%s" %str(e))



while True:
    start_time = time.time()
    conn, addr = proxy_sock_to_client.accept()
    try:
        threading.Thread(target=deal_request,args=(conn,addr)).start()
        print u"上次线程启动:%fs后启动,当前线程数量：%d" %(time.time()-start_time,threading.activeCount())
    except Exception as e:
        print e
