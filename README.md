# Python Web Graph
Wraps over graphviz, uses bs4 to parse and httpx for requests. Takes advantage of Pythons built in robots.txt parser. Very respectful to servers by default. Main file can easily be modified for experimentation.

![image (1)](https://github.com/user-attachments/assets/708b2630-2f47-4bc9-8dc3-43de175790d2)

## How to Run
### Clone repo into new folder:
```bash
git clone https://github.com/zachjesus/web-graph.git .
```

### Set up virtual environment:
```bash
python3 -m venv venv
```

### Active venv
```bash
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
```

### Install requirements
```bash
 pip install -r requirements.txt
```

### Configure main.py, settings are graphviz's, [see docs](https://graphviz.org/documentation/) (or use default):
```bash
python3 main.py
```
Result will be placed in a folder called directory named "output" in the folder where the code is installed. By default, the web graph made graph is an svg image like the one above.
