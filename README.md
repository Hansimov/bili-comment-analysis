---

该脚本用于分析哔站视频评论。

---

## 思路

* 评论 API：
  * https://api.bilibili.com/x/v2/reply?pn=1&type=1&oid=22755224
  * type=1
  * pn：页数
  * oid：视频av号
  * sort
  * nohot：默认为0，收录热门评论，值为1时不收录热门评论

* 首先通过接口获得每一页的内容，保存到本地
  * 格式为 Json
  * 需要获得当前的总页数
  * 保存路径为：./comments/%04d.json
  * 如果是热门视频，评论增加得很快，怎么办？

* 然后分析所得的 json 文件，将所需的内容筛选出来
  * 一级评论：对一级评论的回复暂不收录
  * 评论的赞数和回复数：这两个指标可以衡量该评论是否热门
    * 当然第一页也有热门评论，可以根据 json 中的 key 来判断
  * 评论的楼层和用户名：便于后续其他操作定位

* 将所得内容整理成新的 json 文件

* 可视化

---

## Json 格式分析

链接：https://api.bilibili.com/x/v2/reply?pn=1&type=1&oid=22755224&nohot=1

获得的 Json 格式如下：

```
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

```
"config":{
            "showadmin":1,
            "showentry":1
}
```
</ol> </p>

* `"hots"` 里记录了热门评论。

<p> <ol>

```
"hots":Array[0]
```

这里由于使用了 nohot=1，因此为空。
无论 pn 值是多少，如果 nohot=0，都会将热门评论记录下来。

</ol> <p>


* `"notice"` 暂时无用。

<p> <ol>

```
"notice":null
```

</ol> </p>

* `"page"` 里保存了每一页的信息

<ol>

```
"page":{
    "acount":1274,
    "count":684,
    "num":1,
    "size":20
}
```

</ol>

<ol>

`"acount"`：总的评论数，应该是包括了评论和回复。

`"count"`：可能是一级评论数。存疑。该值与最高楼层不符，可能是因为有些楼层被删除了？

`"num"`：当前页号。从 1 到 最大页数。

`"size"`：该页一级评论数目。应该是固定 20。

</ol>


* `"replies"` 里保存了该页的一级评论及其回复。

<ol>

```
"replies":Array[20]
```

每页有 20 条一级评论。Array 中的每个元素都是 Object 类型。

<ol>

典型的 Object 格式为：

```
{
    "rpid":761233844,           // ？？？
    "oid":22755224,             // 视频av号
    "type":1,                   
    "mid":229564109,            // 用户 mid
    "root":0,
    "parent":0,
    "count":1,
    "rcount":1,
    "floor":702,                // 楼数
    "state":0,
    "fansgrade":0,
    "attr":0,
    "ctime":1525191553,         // 评论时间
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
        "plat":2,                           // ？？？
        "device":"",
        "members":[
        ]
    },
    "replies":[                 // 这里保存了对一级评论的回复
        Object{...}             // 二级三级评论的格式和一级评论类似
    ],
    "assist":0
},

```
</ol>
</ol>

* `"upper"` 里保存了置顶评论的信息。

<ol>

```
"upper":{
            "mid":299999920,
            "top":Object{...}
}
```

这里 `"top"` 的格式和上面的一级评论是一样的。

只不过里面的 `"replies"` 最多只有3个，这是因为网页版默认只展示最多3条对置顶评论的回复。只有点击“点击查看”，才会加载所有的评论。

</ol>



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