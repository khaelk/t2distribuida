import time
import datetime

i = datetime.datetime.timestamp(datetime.datetime.now())
start = time.time()
time.sleep(10)
end = time.time()
a = datetime.datetime.timestamp(datetime.datetime.now()) + 5
print(end-start)
print(datetime.datetime.fromtimestamp(a))
print(datetime.datetime.fromtimestamp(i))