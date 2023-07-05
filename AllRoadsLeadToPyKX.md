# All Roads Lead to Kdb: a PyKX tale

Introducing Emma Monad, the main character of our story and CTO of Mad Flow, a
large and fictional company dedicated to improving the quality of life in
Madrid. Emma was facing the real-world challenge of tackling the issue of heavy
traffic in the city. However, she found herself grappling with an unfortunate
hurdle —an outdated and inflexible legacy data infrastructure within Mad Flow.
This rigid and sluggish platform was hindering the practical analysis of traffic
data, making it difficult to derive meaningful insights and develop effective
solutions. Emma had to navigate this obstacle to unlock the true potential of
Mad Flow and fulfill its mission of transforming Madrid into a more livable and
efficient city.


Emma had heard about the advantages of Q/Kdb by KX: an extremely fast and
flexible platform. Nevertheless, she had serious concerns about taking the leap.
Firstly, she was aware that Q had a reputation for having a steep learning
curve. Secondly, Mad Flow was heavily reliant on the Python environment, making
it impractical to migrate the entire existing codebase. After several months of
internal struggles, she came across PyKX, an open-source library that was
designed to facilitate the integration between Q and Python. Having this option
was crucial in making the decision to adopt Kdb. As time proved, PyKX became
indispensable in guiding the team through every stage of the migration process.
The rest of this story tells you why.

## Chapter 1: Any Q Programmer in the Room?

Setting up the Kdb platform and ingesting the traffic data required several
weeks. Emma wished this process could have taken forever, as she was
apprehensive about the moment of starting. However, there she was, with a
skilled Python team that had no prior experience in writing even a simple "Hello
World" in Q (which, by the way, is `0N!"Hello World!"`), and a Python REPL
waiting for instructions. She tried to conceal her fear, and she typed the very
first line of PyKX code in:
```python
>>> import pykx as kx
```
A sense of calm washed over her as she saw that everything was going well.

Madrid has many traffic devices scattered throughout the city, so the first task
was to retrieve their information from the new platform. According to the
documentation, this information was stored in the `tdevice` q table. She could
also see the instruction that created the table from a _CSV_ file:
```q
tdevice:("SII**FFFF";enlist";")0:`$":pmed_ubicacion_04-2023.csv"
```
"What the hell?" she thought, and she decided to return to the Python shell
where she felt safe once again.

As mentioned in the PyKX user guide, `kx.q` was all she needed to execute
commands against the unfamiliar _q_ world. With little confidence, she decided
to do the obvious:
```python
>>> tdevice = kx.q('tdevice')
```
To her surprise, a collection of familiar data appeared on the screen:
```q
pykx.Table(pykx.q('
tipo_elem distrito id    cod_cent nombre                                     ..
-----------------------------------------------------------------------------..
URB       4        3840  "01001"  "Jose Ortega y Gasset E-O - P\302\272 Caste..
URB       4        3841  "01002"  "Jose Ortega y Gasset O-E - Serrano-P\302\2..
URB       1        3842  "01003"  "P\302\272 Recoletos N-S - Almirante-Prim" ..
URB       4        3843  "01004"  "P\302\272 Recoletos S-N - Pl. Cibeles- Rec..
URB       4        3844  "01005"  "(AFOROS) P\302\272 Castellana S-N  - Eduar..
..
'))
```
Taking advantage of her lucky streak, she set out to play again, this time using
the pandas notation to retrieve a few columns from the table:
```python
>>> tdevice[['distrito', 'id', 'latitud', 'longitud']]
pykx.List(pykx.q('
4         4         1         4         4        4         1         7       ..
3840      3841      3842      3843      3844     3845      3846      3847    ..
40.4305   40.43052  40.42213  40.42143  40.43378 40.42351  40.42816  40.42879..
-3.688323 -3.687256 -3.691727 -3.691929 -3.68847 -3.690991 -3.698403 -3.69455..
'))
```
"Yikes!" It was so close, but "Where are my columns?" she thought. It no longer
looked like a dataframe.

Unfortunately, she didn't have the time to comprehend what was happening as she
had confidently asserted that she could run any given analytics algorithm on the
new platform from day one, despite skepticism from many. Why was Emma so
certain? Because she knew she could seamlessly adapt any q-world dataframe-like
object into Python by transforming it into pandas by means of `pd`:
```python
>>> tdevice.pd()[['distrito', 'id', 'longitud', 'latitud']]
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
Et voilà! Emma simply had to repeat the process to load the remaining dataframes
used by the algorithm, and she was able to execute the program smoothly. She had
intentionally selected an algorithm that produced output in the form of CSV
files because she knew she wasn't ready to reintegrate the results into the q
world just yet. Nonetheless, this marked a significant milestone. Emma saved the
day! However, she was well aware that there was still a long road ahead of her.

## Chapter 2: From Zero to Hero

Several weeks had passed since day zero, and she finally found time to conduct 
more research on PyKX. "Do as little work as necessary," she murmured. "Let q do 
the heavy lifting!" Emma repeated these mantras from the PyKX user guide to herself 
whenever she was tempted to use `pd`. She was now well aware that in order to fully 
harness the platform's potential, she should minimize data transfers between the 
realms of Q and Python, and delegate as much work as possible to the kdb infrastructure.

The key to achieving these goals was closely related to harnessing the full potential 
of the PyKX object API, which served as the foundation of the Python-first approach 
promoted by PyKX. This API facilitated a seamless embedding of q/kdb within Python, 
enabling direct usage of Q operators in Python code. This enhanced the development 
experience and minimized the chances of errors. 

Emma issued her first `qsql` query in a full-blown Pythonic style through the 
PyKX qSQL API:

```python
>>> kx.q.qsql.select(tdevice, columns = ['distrito', 'id', 'longitud', 'latitud'])
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

By pushing the query down into the q realm in this manner, she effectively circumvented 
the need to convert the entire data from the q table into pandas. "Do as little work 
as necessary?" Nailed it!

She also found this mantra quite useful not only for reading from existing tables but 
also for creating new ones. In fact, she soon encountered the need to import a CSV file 
containing static data. Rather than importing it into a Pandas dataframe and then 
converting it into a q table, she efficiently handled the task using the readily 
available `pykx.read` attribute. This function seamlessly brings the functionality of 
the corresponding q keyword into Python, thus avoiding any kind of conversion altogether:

```python
distrito = kx.q.read.csv("Distritos.csv", types = "JFFJJSSS", delimiter=";", as_table=True)
```

However, Emma eventually faced a seemingly significant challenge, as she progressed in her
desire to fully leverage the power of q from within Python: the absence of equivalent 
attributes for operators like `cast`, `drop`, and `exec`, among others. She soon recognized that the 
Pythonic style was mainly geared towards q keyword functions. As `cast`, `drop`, and 
`exec` were operators rather than q functions of its standard library, she needed 
to explore alternative methods for incorporating q code within Python. 

To her surprise, she discovered that a remarkably straightforward solution existed!

```python
>>> kx.q('select distrito,id,longitud,latitud from tdevice')
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

As an experienced programmer, she was well aware that using strings to represent
expressions might not be the most optimal approach. It could lead to errors,
vulnerabilities, and a lack of support from the IDE. So, she would recommend to her teams
the Pythonic style whenever possible.

## Chapter 3: Putting the World Upside Down

Eventually, Emma's growing appreciation for and learning of the kdb/q language naturally led her
to leverage the kdb/q environment directly, rather than relying on Python. However, she didn't want 
to forget about Python either, since her codebase contained many useful Python functions that were 
worth reusing. Fortunately, the PyKX environment provided just this very same functionality, allowing
to execute and eval Python code from within a q session. 

Emma started to think of PyKX as a gift specially made for her by the Three Wise Men.

She decided to make her first attempt using a custom-made Python function called `cdist`, which she was 
too lazy to migrate to q at the moment. Without any trouble, she opened a q console and typed the 
expected commands to import the necessary libraries:

```q
q) system"l pykx.q";
q) .pykx.pyexec"import numpy as np";
q) .pykx.pyexec"from scipy.spatial.distance import cdist";
```

The function `cdist` required several arguments, and Emma opted for a straightforward approach by 
creating new Python variables that referenced q native tables `a` and `b`:

```python
.pykx.set[`xa1;a[`longitud]];
.pykx.set[`xa2;a[`latitud]];
.pykx.set[`yb1;b[`LONGITUD]];
.pykx.set[`yb2;b[`LATITUD]];
```

Calling the function now simply involved evaluating the corresponding Python code and converting 
the resulting data back to q (using the backtick `):

```python
distance_matrix:flip(.pykx.eval"cdist(np.dstack((yb1,yb2))[0], np.dstack((xa1,xa2))[0])")`;
```

Alongside her own Python codebase, MadFlow leveraged highly valuable libraries from the Python 
ecosystem, such as `sklearn`. "I'm confident that the q ecosystem also offers similar ML libraries," 
she thought. And she was correct! However, she was also aware that her teams were already familiar 
with sklearn and would greatly appreciate the ability to reuse existing Python scripts, like the 
following one, without modifications:

```python
from sklearn.linear_model import LinearRegression


def modelo(tabla):
    X = tabla[["direccion", "humedad", "precipitacion", "presion", "solar", "temperatura", "viento" ]].to_numpy()
    y = tabla["carga"].to_numpy().ravel()
    reg = LinearRegression().fit(X, y)

    return reg.score(X, y)
```

This time, she took a different approach to invoke the `model` function. She retrieved it into a 
PyKX object within the q space using `pykx.get` and utilized the PyKX function-call interface:

```q
modelfunc:.pykx.get`model;
res:modelfunc[data];
print res`;
``` 

## Conclusions

As an experienced CTO, Emma was particularly aware of the trade-offs that new technologies pose to complex
organizations like MadFlow. On one hand, state-of-the-art technologies like kdb/q promise enormous 
benefits in terms of performance, efficiency, and the accompanying cost reductions in modern cloud-based
infrastructures. On the other hand, team culture could hinder these advantages if technologists are unable
to adopt the new technology at the same pace. Emma specially appreciated PyKX in this regard: as a
Python-driven organization, her teams couldn't be happier with the opportunity to maintain their
programming environment of choice. Moreover, PyKX simplifies the process of transitioning to kdb/q, 
making it easier for teams to embrace the new technology.

Furthermore, PyKX enabled Emma to avoid the "with me or against me" mentality. She wasn't compelled to 
completely abandon Python but rather gradually replace and deploy critical components that required better
performance into the new kdb/q environment. In fact, she soon appointed three of their top architects,
Félix, Jesús, and Eloy, as team leads for three different teams responsible for various roles within the
MadFlow ecosystem utilizing the new kdb/q infrastructure. These appointments align with the three different
use cases for the PyKX library described in this post.

Stay tuned for the follow-up to this post, where Félix, Jesús, and Eloy will elaborate on the use case 
of heavy traffic and the utilization of PyKX!"

