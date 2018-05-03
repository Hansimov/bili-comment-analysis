import requests
import json
import math
import glob

# https://api.bilibili.com/x/v2/reply?oid=22755224&type=1&sort=0&nohot=1&pn=1

url_head = 'https://api.bilibili.com/x/v2/reply?'
# headers = {
#         'Referer':'https://www.bilibili.com/video'
#         }

def getCommentPage(oid=22755224, xtype=1, sort=0, nohot=1, pn=1, is_get_page_num=0, is_get_req_json=0):
    url_full = url_head \
               + '&oid='   + str(oid) \
               + '&type='  + str(xtype) \
               + '&sort='  + str(sort) \
               + '&nohot=' + str(nohot) \
               + '&pn='    + str(pn)

    print('> Getting comment page: {:0>4d}'.format(pn))
    req_info = requests.get(url_full)
    req_json = req_info.json()
    with open('./comments/{:0>4d}.json'.format(pn),'w',encoding='utf-8') as jsonfile:
        json.dump(req_json, jsonfile)

    if is_get_page_num == 1:
        page_num = getPageNum(req_json)
    else:
        page_num = -1

    if is_get_req_json == 1:
        pass
    else:
        req_json = ''

    return page_num, req_json


def getPageNum(req_json):
    comment_count = req_json['data']['page']['count']
    page_size = req_json['data']['page']['size']
    page_num = math.ceil(comment_count/page_size)
    # print(page_num)
    return page_num


def getAllComments(oid=22755224, xtype=1, sort=0, nohot=1, pn=1):
    page_num, _ = getCommentPage(oid=oid, xtype=xtype, sort=sort, nohot=nohot, pn=pn, is_get_page_num=1)
    for i in range(2, page_num + 1):
        getCommentPage(oid=oid, xtype=xtype, sort=sort, nohot=nohot, pn=i)

def combineJsonFiles(combined_jsonfile_name='allcomments.json'):
    # Issue with merging multiple JSON files in Python:
    #   https://stackoverflow.com/a/23520673/8328786
    combined_jsonfile = []
    page_num = 0
    for jsonfile in glob.glob("./comments/*.json"):
        page_num += 1
        with open(jsonfile, 'r') as infile:
            combined_jsonfile.append(json.load(infile))

    print('+ Number of combined json files: {}'.format(page_num))
    with open(combined_jsonfile_name, 'w') as outfile:
         json.dump(combined_jsonfile, outfile)

'''

`data` -> `replies` -> `[i=0:19]` ->

|        内容        | 点赞数 |     回复数     | 楼层  |      用户       | mid |     时间     | 时间戳 |
|        :-:         |  :-:   |      :-:       |  :-:  |       :-:       | :-: |     :-:      |  :-:   |
| content -> message |  like  | replies.length | floor | member -> uname | mid | ctime.toTime | ctime  |

'''

def processCombinedJsonFile(combined_jsonfile_name):
    with open(combined_jsonfile_name, 'r') as combined_jsonfile:
        combined_data = json.load(combined_jsonfile)
        # print(len(data))
        print(combined_data[0]['data']['replies'][0]['content']['message'])
        print(combined_data[0]['data']['replies'][0]['floor'])

if __name__ == '__main__':
    # getAllComments()
    combined_jsonfile_name = 'allcomments.json'
    # combineJsonFiles(combined_jsonfile_name)
    processCombinedJsonFile(combined_jsonfile_name)

