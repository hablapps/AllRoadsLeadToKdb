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
waiting for instructions. She tried to conceal her fear and she typed the very
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

"Do as little work as possible," she murmured. "Let q do the heavy lifting!"
Emma repeated these mantras from the PyKX user guide to herself whenever she was
tempted to use `pd`. Several weeks had passed since day zero, and she finally
found time to conduct more research on PyKX. In fact, she discovered that
executing `kx.q` returns PyKX objects, which are references that point at
objects living in the q memory space. She also recognized that to fully harness
the platform's potential, she should stick to them as glue, minimizing data
transfers between the realms of Q and Python and leveraging the PyKX object API
extensively.

### Taking Baby Steps

Her team had also started learning Q. Emma could see that they were quite
pleased when they discovered the familiar qsql notation. It provided a haven of
peace amidst the overwhelming overload of symbolic operators and the challenging
task of adapting even the simplest for-loop using _iterators_. That's why she
thought that migrating pandas queries into qsql could be a great task to begin
with:
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
vulnerabilities, and the lack of support from the IDE. Fortunately, she knew
that PyKX adopted a Python-first approach, which meant that Q operators were
embedded within the library. It provided a more seamless integration and
eliminated the need for string representations. In other words, she could work
with Q operators directly in Python code, enhancing the development experience
and reducing the risk of errors:
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
"Do as little work as possible? Nailed it!".

### May the Odds Be Ever in Your Favor

### Stormy Weather

### 

## Chapter 3: Putting the World Upside Down

## Conclusions

