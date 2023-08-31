# All Roads Lead To Kdb

This repository contains the source code for the posts on PyKX published on Habla Computings's blog: 

* [All Roads Lead to Kdb](https://www.habla.dev/blog/2023/07/31/all-roads-lead-to-pykx.html). An introduction to the PyKX library narrated by Emma Monad, a fictional character who plays the role of CTO at the equally fictional company Mad Flow.
* [All Roads Lead to Kdb: the technical counterpart](https://www.habla.dev/blog/2023/07/31/all-roads-lead-to-pykx.html). An in-depth technical description of the use case and PyKX code introduced in the last post. It's intended to serve as a PyKX migration guide for programmers. 

## Content

* `posts/AllRoadsLeadToKdb.md`.  Markdown source of Emma Monad's blog post. 

* `posts/AllRoadsLeadToKdbTechnical.ipynb`. Literate Python/PyKX code for the technical blog post.

* `src/pandas`, `src/pykx`, `src/pykx.q`. The three versions of the implementation of the Mad Flow use case: the original and inefficient Pandas version; its migration into PyKX/Python; and its migration into PyKX/q.

## Running code

* To execute the Python code, you need [PyKX 1.6](https://code.kx.com/pykx/1.6/getting-started/installing.html) installed. Additionally, for running the q code, you'll need [pykx.q](https://code.kx.com/pykx/1.6/api/pykx_under_q.html) as well as [q](https://code.kx.com/q/learn/install/) installed.
- To obtain the source data files in CSV format, which are essential for running the notebook and the Python/q files, please follow the instructions provided in the technical post. Ensure to place these files in the `./data` directory.
