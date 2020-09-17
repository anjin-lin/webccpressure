import encodings.idna
import os,sys
import time,json
import asyncio
import aiohttp
import time
import traceback
import argparse

config = {
    "url":"",
    "num":0,
    "concurrent_num":0,
    "data":{},
    "header":{},
    "method":"GET",
    "timeout":2000
}


class Presstest(object):
    def __init__(self,config):
        self.states={
            'request_num':0
        }
        self.req_status={}
        self.loop = asyncio.get_event_loop()
        self.config=config

    async def send_req(self):
        async with aiohttp.ClientSession() as session:
            args_arr={}
            if self.config['header'] is not None:
                args_arr['headers']=self.config['header']

            if self.config['data'] is not None:
                args_arr['data']=self.config['data']
            async with session.request(self.config['method'],self.config['url'], timeout=self.config['timeout'], **args_arr) as req:
                self.states['request_num']+=1
                if req.status in self.req_status:
                    self.req_status[req.status]+=1
                else:
                    self.req_status[req.status]=1
            print("\r请求总数量：",self.states['request_num'],"   状态统计：",self.req_status, end= "",flush=True)

    async def http_parameter(self):
        if self.config['num']>0:

            for index in range(0,self.config['num']):
                await self.send_req()
                del index
        else:
            while True:
                await self.send_req()

    def concurrent_start(self):
        try:
            tasks=[]
            for x in range(self.config['concurrent_num']):
                tasks.append(self.http_parameter())
                del x

            self.loop.run_until_complete(asyncio.wait(tasks))

        except Exception as e:

            self.loop.stop()
            self.loop.run_forever()

            del e

        finally:
            self.loop.close()

    def run(self):
        self.concurrent_start()

def command():

    args_parser = argparse.ArgumentParser(description="Web CC 压力测试", prog=__package__, usage='%(prog)s [options]')
    args_parser.add_argument('-u', '--u', type=str, nargs='?', required=True, help='HTTP请求地址,格式(http://xxx.xxx.xxx...)')
    args_parser.add_argument('-m', '--m', type=str, nargs='?', help='发起请求方法类型：GET,POST,OPTIONS,PUT,DELETE... 默认：GET',default="GET")
    args_parser.add_argument('-n', '--n', type=int, nargs='?', help='发起请求次数,与并发度与之关联,最后总数量等于(并发度*数量) 0代表一直循环发起请求, 默认：1',default=1)
    args_parser.add_argument('-c', '--c', type=int, nargs='?', help='并发度,int类型,协程并发的数量,默认是: 1',default=1)
    args_parser.add_argument('-t', '--t', type=int, nargs='?', help='每个请求的超时时间 默认2000 (单位:毫秒)',default=2000)
    args_parser.add_argument('-d', '--d', type=str, nargs='?', help='设置每个请求的请求体数据,格式: {"xxx":"xxx"}')
    args_parser.add_argument('-fd', '--fd', type=str, nargs='?', help='设置每个请求的请求体数据(表单提交请设置)')
    args_parser.add_argument('-H', '--H', type=str, nargs='?', help='设置每个请求的请求头,格式：{"xxx":"xxx"}')
    if 1==len(sys.argv):
        args_parser.print_help()
    else:
        args = args_parser.parse_args()
        config['url']=args.u
        config['method']=args.m
        config['num']=args.n
        config['concurrent_num']=args.c
        config['header']=None if not args.H else json.loads(json.dumps(args.H))
        config['data']=None if not args.d else json.loads(json.dumps(args.d))
        config['timeout']=args.t

if __name__== '__main__':
    try:
        command()
        obj = Presstest(config)
        obj.run()
    except Exception as e:
        traceback.print_exc()
        exit

        

