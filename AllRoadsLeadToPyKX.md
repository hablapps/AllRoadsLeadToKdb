# All Roads Lead to Kdb: A Python to Production tale

Introducing Emma Monad, the main character of our story and CTO of Mad Flow, a large and fictional company dedicated to improving the quality of life in Madrid. Emma was facing the real-world challenge of tackling the issue of heavy traffic in the city. However, she found herself grappling with an outdated, ad-hoc constructed, somewhat
inflexible, though open data and analytics Mad Flow infrastructure stack. It was a code base that incorporated various modules developed over time, by in-house data science, engineering and developer teams with the help of occasional interns from the nearby university. The application was predominantly built in Python, the most popular programming language of data science over the last decade.

However, there were problems with the infrastructure. While open and customizable, it suffered with chaotic organization and frequent performance issues, meaning it was slow and unwieldy when incorporating new traffic data-sets or building new insights
quickly. This combined to hinder their ability to define and progress effective transport solutions for the city. Emma wanted to take the greatness of the Mad Flow code base, unlock its true potential, and help fulfil its and their mission of transforming Madrid into a morepleasant, efficient and environmentally friendly city.

Emma thus wanted more agile data management and effective production-ready analytics easily deployed. She had heard, via some occasional consultants to her organization, about a popular and seemingly blindingly fast time-series database and analytics platform called kdb. Nevertheless, that was not for her she felt. Her team’s
comfort was in Python, the language that Mad Flow was predominantly written in, and it was simply impractical to build in anything else, so Python it was. However, at a local PyData Meetup Emma attended, a data scientist acquaintance told her over drinks about PyKX, an open-source library allowing Python to remain the guiding language, but harnessing the power of kdb at runtime. She decided to give it a try, and as time proved, PyKX just worked, and was indispensable in guiding the team from taking a predominantly ad-hoc research data and analytics codebase into a production powerhouse.

The rest of this story tells you how and why.

## Chapter 1: I just want to stay in Python

Setting up kdb to ingest and visualize the traffic data, Emma feared, might require several weeks. Somewhat apprehensively, Emma wished this process could take forever and set expectations with her team accordingly. However, she surprised everyone by quickly invoking a simple "Hello World" in the vector-based functional q language which underpins kdb (which, by the way, is `0N!"Hello World!"`), and get the
environment accessed from a Python REPL waiting for instructions. She typed the very first line of PyKX code in the Python shell:

```python
>>> import pykx as kx
```

A sense of calm washed over her as she saw that everything was going well. The hello world was very quickly achieved.

Madrid has many traffic devices scattered throughout the city, so her first task was to retrieve their information from the new platform. According to the documentation, this information was stored in the `tdevice` q table. She could also see the instruction that
created the table from a _CSV_ file:

```q
tdevice:("SII**FFFF";enlist";")0:`$":pmed_location_04-2023.csv"
```

"What the hell?" she thought, and she decided to return to the familiar Python shell.

But it was actually pretty simple. As the PyKX user guide made clear, `kx.q` was all she needed to execute commands, so she decided to try the obvious:

```python
>>> tdevice = kx.q('tdevice')
```

To her surprise and delight, a collection of familiar data appeared on the screen:

```q
pykx.Table(pykx.q('
elem_type district id    cod_dis name                                     ..
-----------------------------------------------------------------------------..
URB       4        3840  "01001"  "Jose Ortega y Gasset E-O - Pº Caste..
URB       4        3841  "01002"  "Jose Ortega y Gasset O-E - Serrano-Pº..
URB       1        3842  "01003"  "Pº Recoletos N-S - Almirante-Prim" ..
URB       4        3843  "01004"  "Pº Recoletos S-N - Pl. Cibeles- Rec..
URB       4        3844  "01005"  "(AFOROS) Pº Castellana S-N  - Eduar..
..
'))
```

Her team had long familiarity with Pandas notation, so she tried some pandas instructions to retrieve a few columns from the table. It worked, all really easily, or so it seemed:

```python
>>> tdevice[['district', 'id', 'latitude', 'longitude']]
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
>>> tdevice.pd()[['district', 'id', 'longitude', 'latitude']]
      distrito    id  longitud    latitud
0            4  3840 -3.688323  40.430502
1            4  3841 -3.687256  40.430524
2            1  3842 -3.691727  40.422132
...        ...   ...       ...        ...
4741        16  6933 -3.672497  40.484118
4742        16  7129 -3.672500  40.484181
4743        16  7015 -3.672308  40.485002
[4744 rows x 4 columns]
```

Et voilà! Emma simply had to repeat the process to load the remaining dataframes used by the algorithm, and she could execute the program smoothly. She had intentionally selected an algorithm that produced output in the form of familiar CSV file standards because that was what she and her team knew, but her PyData and kdb-knowledgeable fellow attendee had told her that kdb data stores were so much more
efficient. For now, though, she’d stay with csv. Nonetheless, this marked a significant milestone. Emma had already felt that some of the initial promises were delivered!  However, she was well aware of the long road ahead of her if she was to bring along her team and make Mad Flow the agile production analytics platform she wanted it to be.

## Chapter 2: From Zero to Hero

Several weeks passed, and, having onboarded a couple of data scientist interns, she finally found time to work with them and conduct more research on PyKX. "Do as little work as necessary," she murmured. "I just want my team to work with what they’re comfortable with, but have kdb do the heavy lifting!" Emma repeated these mantras from the PyKX user guide to herself whenever she was tempted to use `pd`. However,
she was now well aware that in order to fully harness the platform's potential, she should minimize data transfers between the two realms, and delegate as much work as possible to the kdb infrastructure.

The key to achieving these goals was in harnessing the full potential of the PyKX object API, allowing a Python-first approach. This API facilitated the seamless embedding of q/kdb within Python, enabling direct use of efficient q functions in Python code. If practical, this would enhance the development experience, minimize the chances of
errors and, the team hoped, dramatically improve performance.

Emma thus issued her first `qsql` query in a full-blown Pythonic style using the API:

```python
>>> kx.q.qsql.select(tdevice, columns = ['district', 'id', 'longitude', 'latitude'])
pykx.Table(pykx.q('
distrito id    longitud  latitud 
---------------------------------
4        3840  -3.688323 40.4305 
4        3841  -3.687256 40.43052
1        3842  -3.691727 40.42213
4        3843  -3.691929 40.42143
4        3844  -3.68847  40.43378
..
'))
```

By pushing the query straight down into the q realm, there was now no need to convert the entire data into Pandas. "Do as little work as necessary?" Nailed it!

She also found this mantra quite useful, not only for reading from existing tables but also when creating new ones. In fact, she soon encountered the need to import a CSV file containing static data. Rather than importing it into a Pandas dataframe and then
converting it into a q table, she simply used the `pykx.read` attribute which brings the functionality of the corresponding q keyword into Python, thus avoiding any kind of conversion altogether:

```python
distrito = kx.q.read.csv("Districts.csv", types = "JFFJJSSS", delimiter=";", as_table=True)
```

However, Emma faced challenges. She noticed the absence of equivalent attributes for operators like `cast`, `drop`, and `exec`, among others, appreciating that the Pythonic style was mainly geared towards q keyword functions. As `cast`, `drop`, and `exec` were operators rather than standard q functions, she needed to explore alternative
methods to maintain their Python familiarity.

Yet it proved remarkably straightforward!

```python
>>> kx.q('select district,id,longitude,latitude from tdevice')
pykx.Table(pykx.q('
distrito id    longitud  latitud 
---------------------------------
4        3840  -3.688323 40.4305 
4        3841  -3.687256 40.43052
1        3842  -3.691727 40.42213
4        3843  -3.691929 40.42143
4        3844  -3.68847  40.43378
..
'))
```

As an experienced programmer, she was well aware that using strings to represent expressions might not be the most optimal approach. It could lead to errors, vulnerabilities, and a lack of support from the IDE. So, she would recommend to her teams the Pythonic style whenever possible.

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
technologists just want to stick with their preferred tools. Emma therefore especially appreciated PyKX as a vehicle to bring production capabilities into a Python-friendly organization, and those who influenced the codebase from the Python community at large. Her teams couldn't have been happier with the result. They could maintain and
enhance their programming environment of choice, but swiftly transition onerous tasks to q/kdb.

Thus PyKX allowed Emma to avoid the "with me or against me" mentality that comes with change. There was no unpopular abandonment of Python, far from it. Instead Python took on new meaning as it became the vehicle to steer more analytics into production and make those already in production much more perform. In fact, she soon appointed three of their top architects, Félix, Jesús, and Eloy, as team leads for three different teams responsible for various roles within the Mad Flow ecosystem utilizing the new infrastructure. These appointments align with the three different use cases for the PyKX library described in this post.

Stay tuned for the follow-up to this post, where Félix, Jesús, and Eloy will elaborate on the use case of heavy traffic and the utilization of PyKX!
