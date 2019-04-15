#
# Monero NODEJS POOL Daemon/API Monitor
#
# This script compares pool API and Monero Daemon height with other pools and nodes in the network to monitor sync
#
# Thanks to bitmoeda for the help!
#
import requests
from time import sleep
from time import time
from time import strftime

pools = [
  {'name': 'minexmr.com', 'url' : 'http://stats.minexmr.com/stats', 'refresh': 5},
  {'name': 'moneropool.com', 'url' : 'https://api.moneropool.com/stats', 'refresh': 5},
  {'name': 'supportxmr.com', 'url' : 'https://supportxmr.com/api/network/stats', 'refresh': 5},
  {'name': 'node.supportxmr.com', 'url' : 'https://node.supportxmr.com:18081/getinfo', 'refresh': 5},
  {'name': 'xmrpool.net', 'url' : 'http://xmrpool.net:18081/getinfo', 'refresh': 5},
  {'name': 'node.xmr.pt', 'url' : 'http://node.xmr.pt:18081/getinfo', 'refresh': 1},
  {'name': 'localpool', 'url' : 'https://pool.xmr.pt/api/network/stats', 'refresh': 1},
  {'name': 'localnode', 'url' : 'http://127.0.0.1:18081/getinfo', 'refresh': 1},
]

def get_height(url):
  try:
    r=requests.get(url, timeout=0.5)
    j=r.json()
    if 'network' in j.keys():
      p=j['network']['height']
    else:
      p=j['height']
      if 'incoming_connections_count' in j.keys():
        #Tries to detect if it's a pool or a monerod that we are connecting to.
        #Nodes return the height of the block beeing mined while pool's return
        #the last block already mined, so we need to subtract one.
        p = p-1 
  except Exception,e:
    p = None
  return p

last_height = 0
max_height = 0
for p in pools:
  p['last_update'] = 0
while True:
  for p in pools:
    name = p['name']
    url = p['url']
    refresh = p['refresh']
    last_update = p['last_update']
    now = time()
    if refresh < (now - last_update):
      h = get_height(url)
      p['last_update'] = now
    if h is not None:
      height = h
    else:
      #print "ERROR getting height from %s" % name
      height = 0
    #print name, height
    if name == 'localpool':
      pool_height = height
    elif name == 'localnode':
      node_height = height
    if height > max_height:
      max_height = height
  dt = strftime("%Y-%m-%d %H:%M:%S")
  if pool_height < max_height or node_height < max_height:
    print dt, max_height, 'BLOCKS BEHIND:',
    if pool_height < max_height:
      print 'POOL API:', (max_height - pool_height),
    if node_height < max_height:
      print 'NODE:', (max_height - node_height),
    print
  elif last_height < max_height:
    print dt, max_height, "OK"
    last_height = max_height
  sleep(1)

