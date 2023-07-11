# t2distribuida
t2distribuida

## Some considerations: ##

- ptime + adelay must be < 10s

- Discard value on the average if the value differs 10 from the last average calculated.

## How to run: ##

### run Master ###
python node.py id{0} host{127.0.0.1} port{1024} hh:mm:ss.ms{22:00:00} ptime<ms> adelay<ms> OPTIONAL:ticking<ms, default = 1000> OPTIONAL:timeDisplay<{0,1} = {off, on}, default = 1>

### run Slaves ###
python node.py id{1} host{127.0.0.1} port{1025} hh:mm:ss.ms{22:12:30} ptime<ms> adelay<ms> OPTIONAL:ticking<ms, default = 1000> OPTIONAL:timeDisplay<{0,1} = {off, on}, default = 1>

python node.py id{2} host{127.0.0.1} port{1026} hh:mm:ss.ms{22:01:00} ptime<ms> adelay<ms> OPTIONAL:ticking<ms, default = 1000> OPTIONAL:timeDisplay<{0,1} = {off, on}, default = 1>

python node.py id{3} host{127.0.0.1} port{1027} hh:mm:ss.ms{22:04:00} ptime<ms> adelay<ms> OPTIONAL:ticking<ms, default = 1000> OPTIONAL:timeDisplay<{0,1} = {off, on}, default = 1>