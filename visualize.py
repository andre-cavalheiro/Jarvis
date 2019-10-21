from utils import *
import time
from visualization.app import visualization

print('Rendering...')
df = unifyOutpus(join('src', 'output'))
# print(df.head())

vis = visualization()
app = vis.render(df)
app.run_server(debug=True)
