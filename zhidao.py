#-*- coding: UTF-8 -*-


import json

# httpx module from https://github.com/thisforeda/socket-http
from httpx import urlopen
from definitions import safe_decoder

# jsnparsers module from https://github.com/thisforeda/Json-Parsers
from jsnparsers import BaiDuZhiDaoParser as parser

result_list_url = 'http://zhidao.baidu.com/msearch/ajax/getsearchlist?word=%s&pn=%d'
full_result_url = 'http://zhidao.baidu.com/msearch/ajax/getsearchqb?qid=%s&rid=%d'

# 关键字例如:
#   "PYTHON" , "PYTHON PIP",不支持其他高级搜索关键字

class ZhiDaoSearch(object):
    def __init__(self,
                        skip_mismatch_results = True, # 当获取问题不符合关键字的时候终止执行
                                 max_gain_results = 10  # 获取的最大数量(10的倍数)
                                                        ):
        self.keyword = None
        self.skip_mismatch_results = skip_mismatch_results
        self.max_gain_results = max_gain_results
        self.last_gain_position = 0
        self.results = parser()
    
    def search(self,kword,start = 0,new = True):
        if new == True:
            self.reset()
        is_first_search = True
        self.keyword = ZhiDaoSearch.KeyWordFmt(kword)
        for pn in range(start ,self.max_gain_results ,10):
            response  = urlopen(result_list_url % (self.keyword[0],pn))
            if hasattr(response,'header')\
                       and response.header['status'] == '200':
                self.results.append(safe_decoder(response.data))
                self.last_gain_position = pn
                if is_first_search and len(self.results) > 0:
                    is_first_search = False
                    for word in self.keyword[1]:
                        if word.upper() in self.results[0]['title'].upper():
                            print('$key word %s found.'%word)
                            break
                    if  word == self.keyword[-1]:
                        return
    @staticmethod
    def full_results(elem):
        if elem['aid'] and elem['moreInfo']:
            response  = urlopen(full_result_url % (elem['id'],elem['aid']))
            if hasattr(response,'header')\
                           and response.header['status'] == '200':
                jsn = json.loads((safe_decoder(response.data)))
                if jsn.get('data'):
                    elem.update({'content':jsn['data']['content']})
                return elem
        return None

            
    def reset(self,skip_mismatch_results = True,max_gain_results = 10):
        self.skip_mismatch_results = skip_mismatch_results
        self.max_gain_results = max_gain_results
        self.results = parser()
        
    @staticmethod
    def KeyWordFmt(kword):
        return (
            '+'.join('%2B'.join(kword.split('+')).split(' ')),
            kword.split(' ') )
                
if __name__ == '__main__':
    zhi = ZhiDaoSearch()
    zhi.search('PYTHON')
    for ques in zhi.results :
        print(ques['time'] +'  '+ ques['title'])






        
