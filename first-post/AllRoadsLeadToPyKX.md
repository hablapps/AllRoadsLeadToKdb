---
layout: post
title: "All roads lead to PyKX"
author: Jesús López-González
image: /img/destino.jpg
toc: true
---

# All Roads Lead to Kdb: A Python to Production tale

Introducing Emma Monad, the main character of our story and CTO of Mad Flow, a large and fictional company dedicated to improving the quality of life in Madrid. Emma was facing the real-world challenge of tackling the issue of heavy traffic in the city. However, she found herself grappling with an outdated, ad-hoc constructed, somewhat
inflexible, Mad Flow infrastructure stack. It was a code base that incorporated various modules developed over time, by in-house data science, engineering and developer teams with the help of occasional interns from the nearby university. The application was predominantly built in Python, the most popular programming language of data science over the last decade.

However, there were problems with the infrastructure. While open and customizable, it suffered with chaotic organization and frequent performance issues, meaning it was slow and unwieldy when incorporating new traffic data-sets or building new insights quickly. This combined to hinder their ability to define and progress effective transport solutions for the city. Emma wanted to take the greatness of the Mad Flow code base, unlock its true potential, and help fulfil its and their mission of transforming Madrid into a more pleasant, efficient and environmentally friendly city.

Emma thus wanted more agile data management and effective production-ready analytics easily deployed. She had heard, via some occasional consultants to her organization, about a popular and seemingly blindingly fast time-series database and analytics platform called kdb. Nevertheless, that was not for her she felt. Her team’s
comfort was in Python, the language that Mad Flow was predominantly written in, and it was simply impractical to build in anything else, so Python it was. However, at a local PyData Meetup Emma attended, a data scientist acquaintance told her over drinks about PyKX, an open-source library allowing Python to remain the guiding language, but harnessing the power of kdb at runtime. She decided to give it a try, and as time proved, PyKX just worked, and was indispensable in guiding the team from taking a predominantly ad-hoc research data and analytics codebase into a production powerhouse.

The rest of this story tells you how and why.

## Chapter 1: I just want to stay in Python

Setting up kdb to ingest the traffic data, Emma feared, might require several weeks. Somewhat apprehensively, Emma set expectations with her team accordingly. However, there she was, with a skilled Python team that had no prior experience in writing even a simple “Hello World” in Q (which, by the way, is 0N!"Hello World!"), and a Python REPL waiting for instructions. She tried to conceal her fear, and she typed the very first line of PyKX code in the Python shell:

```python
>>> import pykx as kx
```

A sense of calm washed over her as she saw that everything was going well.

Madrid has many traffic devices scattered throughout the city, so her first task was to retrieve their information, available in several .csv files, into the new platform. According to the PyKX documentation, the  `pykx.read` attribute seemed to be her best option:

```python
tdevices = kx.q.read.csv("devices.csv", types = "JFFJJSSS", delimiter=";", as_table=True)
```

Her team had extensive familiarity with Pandas notation, so she decided to try some Pandas instructions to retrieve a few columns from the table. It worked effortlessly, or at least it seemed so at first.

```python
>>> tdevices[['district', 'id', 'latitude', 'longitude']]
pykx.List(pykx.q('
4         4         1         4         4        4         1         7       ..
3840      3841      3842      3843      3844     3845      3846      3847    ..
40.4305   40.43052  40.42213  40.42143  40.43378 40.42351  40.42816  40.42879..
-3.688323 -3.687256 -3.691727 -3.691929 -3.68847 -3.690991 -3.698403 -3.69455..
'))
```

"Yikes!" It was so close, but it didn’t look like a dataframe. "Where are my columns?" she thought.

That wouldn’t impress her colleagues, for whom familiar columns mattered. If this was to be a barrier, then it would likely be even harder to run the required analytics algorithms on the proposed new platform. But the documentation suggested the `pd`command which just worked:

```python
>>> tdevices.pd()[['district', 'id', 'longitude', 'latitude']]
      district    id  longitude   latitude
0            4  3840  -3.688323  40.430502
1            4  3841  -3.687256  40.430524
2            1  3842  -3.691727  40.422132
...        ...   ...        ...        ...
4741        16  6933  -3.672497  40.484118
4742        16  7129  -3.672500  40.484181
4743        16  7015  -3.672308  40.485002
[4744 rows x 4 columns]
```

Et voilà! Emma simply had to repeat the process to load the remaining dataframes used by the selected algorithm, and she could execute the program smoothly, in its very original form. She had intentionally choose an algorithm that produced output in the form of familiar CSV file standards because that was what she and her team knew, but her PyData and kdb-knowledgeable fellow attendee had told her that kdb data stores were so much more efficient. For now, though, she’d stay with csv. Nonetheless, this marked a significant milestone. Emma had already felt that some of the initial promises were delivered!  However, she was well aware of the long road ahead of her if she was to bring along her team and make Mad Flow the agile production analytics platform she wanted it to be.

## Chapter 2: From Zero to Hero

Several weeks passed, and, having onboarded a couple of data scientist interns, she finally found time to work with them and conduct more research on PyKX. "Do as little work as necessary," she murmured. "I just want my team to work with what they’re comfortable with, but have kdb do the heavy lifting!" Emma repeated these mantras from the PyKX user guide to herself whenever she was tempted to use `pd`. Indeed, she was now well aware that in order to fully harness the platform's potential, she should minimize data transfers between the two realms, and delegate as much work as possible to the kdb infrastructure.

The key to achieving these goals lay in leveraging the PyKX object API, which allowed a Python-first approach. This API made it easy to embed q/kdb within Python, enabling the direct use of efficient q functions in Python code. Additionally, it provided convenient re-implementations of Pythonic APIs, like the Pandas APIs, eliminating the need for conversions to Pandas in many cases. If feasible, this would enhance the development experience, reduce the chances of errors, and, the team hoped, significantly improve performance.

She first tried with the PyKX Pandas API re-implementation, which could be actrivated through the following environment variable:

```python
>>> import os
>>> os.environ['PYKX_ENABLE_PANDAS_API'] = 'true' 
```

Then, she tried the exact same Pandas expression as in the previous section:

```python
>>> tdevices[['district', 'id', 'latitude', 'longitude']]
pykx.Table(pykx.q('
district id   latitude  longitude
--------------------------------
4        3840 40.4305  -3.688323
4        3841 40.43052 -3.687256
1        3842 40.42213 -3.691727
4        3843 40.42143 -3.691929
4        3844 40.43378 -3.68847 
...
'))
```

Et voilà! There were the columns, and she didn't need to convert q tables to Pandas dataframes! "Do as little work as necessary?" Nailed it! And this approach worked for many other methods of the Pandas API as well, such as filtering, dropping, and renaming columns.

```python
>>> tdevices = tdevices[tdevices["elem_type"] == "URB"]
>>> tdevices = tdevices.drop(["elem_type","district", "cod_cent", "name", "utm_x", "utm_y"], axis=1)
>>> tdevices = tdevices.rename(columns={"longitude":"long", "latitude":"lat","id":"traffic_station"})
```

While this approach allowed Emma to stay in her beloved Python and avoid costly conversions, the PyKX object API offered other alternatives to query q tables that were worth exploring. Firstly, she had heard that kdb supported querying through plain-old ANSI SQL, and this possibility was enabled through PyKX as well! This time, she decided to use the _weather_ dataset to test this feature:

```python
>>> weather = kx.q.read.csv('./abr_meteo23.csv', types='IIII****' + 'FS'*24, delimiter=';', as_table=True)
```

Once loaded, she issued a simple SQL query:

```python
>>> kx.q.sql('select STATION, count(distinct(MAGNITUDE)) from $1 group by STATION', weather) 
pykx.Table(pykx.q('
STATION  MAGNITUDE
------------------
4        1
8        2
16       2
...
```

That was nice, but she had also heard about qSQL, a collection of query templates resembling SQL, with enhanced expressiveness when dealing with ordered data. qSQL was also available through PyKX by means of a Pythonic interface:

```python
>>> kx.q.qsql.select(weather, columns = {'MAGNITUDE': 'count distinct MAGNITUDE'}, by=["STATION"])
pykx.KeyedTable(pykx.q('
STATION | MAGNITUDE
--------| --------
4       | 1
8       | 2
16      | 2
...
```

The pythonic interface proved quite convenient, and it was actually extended to many functions from the [q reference card](https://code.kx.com/pykx/1.6/api/q/q.html). However, she noticed the absence of equivalent attributes for operators like `cast`, `drop`, and `exec`, among others. So, she needed to explore alternative methods to be able to express arbitrary q expressions. Yet it proved remarkably straightforward! For instance, the previous qSQL query may also be implemented as follows:

```python
>>> kx.q("{select count distinct MAGNITUDE by STATION from x}", weather)
pykx.KeyedTable(pykx.q('
ESTACION| MAGNITUD
--------| --------
4       | 1
8       | 2
16      | 2
...
```

As an experienced programmer, she was well aware that using strings to represent expressions might not be the most optimal approach. It could lead to errors, vulnerabilities, and a lack of support from the IDE. So, she would recommend to her teams the Pythonic style of the Pandas, SQL and qSQL APIs whenever possible.

## Chapter 3: Putting the World Upside Down

Eventually, Emma's growing appreciation for and excitement in learning about the q/kdb language encouraged her to increasingly try to adopt it directly. However, her colleagues and new hires all knew – and loved – Python as did she, and her codebase contained many useful reusable Python functions. Fortunately, it was straightforward to execute and eval Python code from within her q session.

Emma started to think of PyKX as a gift specially made for her by the Three Wise Men. It truly offered the best of both worlds, the flexibility and familiarity of Python and the sheer power and efficiency of q/kdb.

She made her first attempt using a custom-made Python function called `cdist`, which she had no immediate need to migrate away from Python. From her q console, she typed the expected commands to import the necessary libraries:

```q
q) system"l pykx.q";
q) .pykx.pyexec"import numpy as np";
q) .pykx.pyexec"from scipy.spatial.distance import cdist";
```

The function `cdist` required several arguments, and Emma simply created new Python variables that referenced q native tables `a` and `b`:

```python
.pykx.set[`xa1;a[`longitude]];
.pykx.set[`xa2;a[`latitude]];
.pykx.set[`yb1;b[`LONGITUDE]];
.pykx.set[`yb2;b[`LATITUDE]];
```

Calling the function now simply involved evaluating the corresponding Python code and converting the resulting data back to q (using the backtick `):

```python
distance_matrix:flip(.pykx.eval"cdist(np.dstack((yb1,yb2))[0], np.dstack((xa1,xa2))[0])")`;
```

Alongside her own Python codebase, Mad Flow leveraged highly valuable and popular libraries from the Python ecosystem, such as sci-kit learn (`sklearn`) for statistical and machine learning. "Perhaps the q ecosystem also offers similar ML libraries?" she rightly thought. However, her teams familiarity with – and trust in - sklearn was irresistible, so they simply wanted to reuse their existing Python scripts, like the following, without modifications:

```python
from sklearn.linear_model import LinearRegression


def model(table):
    X = table[["address", "humidity", "precipitation", "pressure", "solar", "temperature", "wind" ]].to_numpy()
    y = table["load"].to_numpy().ravel()
    reg = LinearRegression().fit(X, y)

    return reg.score(X, y)
```

This time, though, she took a different approach to invoke the `model` function. She retrieved it into a PyKX object within the q space using `pykx.get` and utilized the PyKX function-call interface:

```q
modelfunc:.pykx.get`model;
res:modelfunc[data];
print res`;
```

## Conclusions

As a CTO managing a talented yet pressured team, Emma was particularly aware of the trade-offs that introducing new technologies posed to Mad Flow. On one hand, state-of-the-art technologies promise enormous performance, efficiency, and infrastructure cost reductions. On the other hand, team culture and the overwhelming comfort and appreciation of community tools, such as Python, could hinder these advantages if
technologists just want to stick with their preferred tools. Emma therefore especially appreciated PyKX as a vehicle to bring production capabilities into a Python-friendly organization, and those who influenced the codebase from the Python community at large. Her teams couldn't have been happier with the result. They could maintain and enhance their programming environment of choice, but swiftly transition onerous tasks to q/kdb.

Thus PyKX allowed Emma to avoid the "with me or against me" mentality that comes with change. There was no unpopular abandonment of Python, far from it. Instead Python took on new meaning as it became the vehicle to steer more analytics into production and make those already in production much more perform. In fact, she soon appointed three of their top architects, Félix, Jesús, and Eloy, as team leads for three different teams responsible for various roles within the Mad Flow ecosystem utilizing the new infrastructure. These appointments align with the three different use cases for the PyKX library described in this post.

Stay tuned for the follow-up to this post, where Félix, Jesús, and Eloy will elaborate on the use case of heavy traffic and the utilization of PyKX!

### Acknowledgments

This post was greatly enhanced thanks to the edits and comments from Steve Wilcokson and Conor McCarthy from KX. Óscar Nydza, Juan M. Serrano, and Marcos Vázquez from Habla Computing did their best to finalize the draft left by Jesús before he started to enjoy his paternity leave to take care of Félix, Jesús, and Eloy.

### Dedication

This post is dedicated to Eloy and the three newborns at Habla: Emma, Félix, and Jesús.

*Post Picture: Project for "Destino", Salvador Dalí (1946)*
