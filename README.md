# t2distribuida
t2distribuida

run Master
python node.py 0 127.0.0.1 1024 time ptime adelay

run Slaves
python node.py 1 127.0.0.1 1025 time ptime delay