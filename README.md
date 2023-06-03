# t2distribuida
t2distribuida

run Master
python node.py 0 127.0.0.1 1024 12:32:55.2 ptime adelay

run Slaves
python node.py 1 127.0.0.1 1025 00:00:05 ptime delay
python node.py 2 127.0.0.1 1026 00:00:05 ptime delay
python node.py 3 127.0.0.1 1027 00:00:05 ptime delay