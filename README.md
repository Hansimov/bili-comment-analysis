---

该脚本用于分析哔站视频评论。

---

## 思路

* 评论 API：
  * https://api.bilibili.com/x/v2/reply?pn=1&oid=22755224&type=1&sort=0&nohot=1
  * type=1
  * pn：页数
  * oid：视频av号
  * sort：0表示按照楼层排序（默认），1含义不明，2表示按照热度排序（取决于点赞和回复）
  * nohot：默认为0，收录热门评论，值为1时不收录热门评论

* 首先通过接口获得每一页的内容，保存到本地
  * 格式为 Json
  * 需要获得当前的总页数
  * 保存路径为：./comments/%04d.json
  * 如果是热门视频，评论增加得很快，怎么办？

* 然后分析所得的 json 文件，将所需的内容筛选出来
  * 一级评论：对一级评论的回复暂不收录
  * 评论的赞数和回复数：这两个指标可以衡量该评论是否热门
    * 当然返回的每一页 json 中也有热门评论和置顶评论，可以根据 json 中的 key 来判断
  * 评论的楼层和用户名：便于后续其他操作定位
  * 评论时间

* 将所得内容整理成新的 json 文件

* 可视化

---

## 源 Json 格式

链接：https://api.bilibili.com/x/v2/reply?pn=1&type=1&oid=22755224&nohot=1

获得的 Json 格式如下：

```j
{
    "code":0,
    "data":{
        "config":Object{...},
        "hots":Array[0],
        "notice":null,
        "page":Object{...},
        "replies":Array[20],
        "top":null,
        "upper":Object{...}
    },
    "message":"0",
    "ttl":1
}
```


* 有用的数据都在 `"data"` 里。

* `"config"` 暂时无用。

<p> <ol>

```j
"config":{
            "showadmin":1,
            "showentry":1
}
```
</ol> </p>

* `"hots"` 里记录了热门评论。

<p> <ol>

```j
"hots":Array[0]
```

这里由于使用了 nohot=1，因此为空。
无论 pn 值是多少，如果 nohot=0，都会将热门评论记录下来。

</ol> <p>


* `"notice"` 暂时无用。

<p> <ol>

```j
"notice":null
```

</ol> </p>

* `"page"` 里保存了每一页的信息

<ol>

```j
"page":{
    "acount":1274,    // 总的评论数，应该是包括了一级评论和次级评论。
    "count":684,      // 一级评论数。该值与最高楼数不符，猜测是因为有些楼层被删除了。
    "num":1,          // 当前页号。从 1 到最大页数。
    "size":20         // 该页一级评论数目。应该是最大 20。
}
```
</ol>

* `"replies"` 里保存了该页的一级评论及其回复。

<ol>

```j
"replies":Array[20]
```

每页有 20 条一级评论。Array 中的每个元素都是 Object 类型。

<ol>

典型的 Object 格式为：

```j
{
    "rpid":761233844,           // 该评论的ID
    "oid":22755224,             // 视频av号
    "type":1,                   
    "mid":229564109,            // 用户 mid
    "root":0,                   // 该评论的根ID，即所在的一级评论，默认为0，表示该评论为一级评论
    "parent":0,                 // 该评论所回复的评论ID
    "count":1,                  // 可能是历史的回复数？
    "rcount":1,                 // 该楼下的现存回复数
    "floor":702,                // 楼层
    "state":0,
    "fansgrade":0,
    "attr":0,
    "ctime":1525191553,         // 评论的时间戳
    "rpid_str":"761233844",
    "root_str":"0",
    "parent_str":"0",
    "like":2,                   // 点赞数
    "action":0,
    "member":{                  // 这里保存了用户信息，详情可以参考：https://github.com/uupers/BiliSpider/wiki/Bilibili-API-%E7%94%A8%E6%88%B7%E4%BF%A1%E6%81%AF
        "mid":"229564109",      // mid
        "uname":"小白白白白j",  // 昵称
        "sex":"保密",           // 性别
        "sign":"",              // 签名
        "avatar":"http://i1.hdslb.com/bfs/face/d189dcf522fd0da08043895ca53b5bd8485a50d2.jpg",  // 头像图片地址
        "rank":"10000",
        "DisplayRank":"0",
        "level_info":Object{...},
        "pendant":Object{...},
        "nameplate":Object{...},
        "official_verify":Object{...},
        "vip":Object{...},
        "fans_detail":null,
        "following":0
    },
    "content":{                // 这里保存了评论的信息
        "message":"追番的人这么少吗",       // 评论内容
        "plat":2,                           // 可能是平台？（电脑，手机，Pad）
        "device":"",
        "members":[
        ]
    },
    "replies":[                 // 这里保存了对一级评论的回复，需要关注的是这里的回复数量
        Object{...}             // 二级三级评论的格式和一级评论类似
    ],
    "assist":0
}

```
</ol>
</ol>

* `"upper"` 里保存了置顶评论的信息。

<ol>

```j
"upper":{
            "mid":299999920,    // 该视频 UP 的 mid
            "top":Object{...}
}
```

这里 `"top"` 的格式和上面的一级评论是一样的。

只不过里面的 `"replies"` 最多只有3个，这是因为网页版默认只展示最多3条对置顶评论的回复。只有点击“点击查看”，才会加载所有的评论。

</ol>

---
## 目标 Json 格式

各参数在 Json 文件中的位置：

`data` -> `replies` -> `[i=0:19]` ->

| 楼层 | 时间 | 用户 | 消息 | 点赞数 | 回复数 |
| :-:  |  :-:   |  -   |   -  | :-:  | :-: |
| floor |  fromtimestamp(ctime)  | member -> uname | content -> message | like | rcount |


呈现效果：


| 楼层 | 时间 | 用户 | 消息 | 点赞数 | 回复数 |
| :-:  |  :-:   |  -   |   -  | :-:  | :-: |
| 53 | 2018-04-30 10:31:17 | 星之碎片灬 | B站不是以前那个只看番的B站了 | 1 | 7 |
| 52 | 2018-04-30 10:21:11 | オレンジの約束 | 哇，原来B站不是用来看番的 | 1 | 0 |
| 51 | 2018-04-30 10:17:39 | 哆啦有个梦 | 总结:从哔哩哔哩动画变成了哔哩哔哩 | 2001 | 44 |

这里暂时只考虑了一级评论。二级评论的影响体现在回复数上。


目标 Json 格式：

```j
[
    {
        "message":"追番的人这么少吗",
        "like":2,
        "replynum":1,
        "floor":702,
        "uname":"小白白白白j",
        "mid":"229564109",
        "time":"2018-05-02 00:19:13",
        "ctime":"1525191553"
    },
    {
        "message":"投一波硬币",
        "like":0,
        "reply":0,
        "floor":693,
        "uname":"堂主小黑",
        "mid":9388872,
        "time":"2018-05-01 23:59:13",
        "ctime":1525190353
    }
]
```



---
## 实现问题

* 如何获得总的页数？
  * （源 Json 中并没有记录相关的数据）
  * &#10004; 通过 json 文件中的 `"data"` -> `"page"` -> `"count"` + `"size"` 计算得到
    * 先获取第 1 页，然后解析出这几个值，再获取后续的页面
  * 解析网页中显示最大页码的对应元素，然后提取该数字
    * 优点：精度高
    * 缺点：
      * 效率较低：相比网络 IO，这点解析的时间可以忽略不计
      * 如果恰好后来的页数增加，则会漏爬：如果评论增长速度较低，可以忽略这个问题，或者可以定期重爬
      * 在 html 文件里是找不到这个内容的，因为这是前端实时计算出来的
  * 通过分析已有的 Json 是否采集到了 1 楼评论
    * 优点：可以避免漏爬和多爬
    * 缺点：
      * 效率较低，每爬一页都要解析
      * 如果 1 楼评论被用户或者 UP 主删除，则需要处理该异常情况

* 如何保证楼数不重叠？
  * （因为页面是动态加载的，如果爬取时出现新评论，会将该页最下面的评论顶到下一页）
  * 去重：如果发现该楼已经在数据库里了，就不再加入

* 以什么格式保存处理好的数据？
  * &#10004; json
    * 优点：
      * 结构化
      * 方便检索和处理
    * 缺点
      * 不方便直接查看
      * 只适合处理少量数据
  * csv：
    * 优点：
      * 便于直接查看和处理
    * 缺点：
      * 评论中有可能出现逗号：给该项加上引号（评论中又出现引号怎么办）
      * 只适合处理少量数据
      * 难以处理嵌套类型的数据：评论里还有评论
  * 数据库
    * 优点：
      * 支持更多更复杂的操作
      * 可以容纳大量数据
    * 缺点：
      * 配置较为复杂


---
## 参考链接

* 用python 抓取B站视频评论，制作词云
  * https://www.cnblogs.com/xsmile/p/8004433.html

* 爬虫如何抓取b站评论，弹幕等内容？ - 肥肥杨的回答 - 知乎
  * https://www.zhihu.com/question/56924570/answer/236892766

* Vespa314/bilibili-api：搜索“读取评论V2”
  * https://github.com/Vespa314/bilibili-api/blob/master/api.md

* PYTHON爬虫，获得动态加载的数据
  * http://www.lz1y.cn/archives/529.html