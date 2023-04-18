### Pulse Blaster

laser = [6, 20]
mw = [5,1]
read = [[6.3, 1], [16.3, 1]]

## get total number of events over all channels
## 

events:
mw on: 5
mw off, laser on: 6
mw off, laser on, read on: 6.3
mw off, laser on, read off: 7.3
mw off, laser on, read on: 16.3
mw off, laser on, read off: 17.3

event list = [5, 6, 6.3, 7.3, 16.3 17.3]

## Use swabian style?
total = 26 ## max of sum of each chan
laser = [[6,0], [20,1], [0,0]]
mw = [[5, 0], [1,1], [20, 0], [0,0]] 
read = [[6.3, 0], [1,1], [9, 0], [1,1], [0,0]]

edges = []
for idx, _ in enumerate(read[2:]):
    ## read[idx]  = [time, status]
    if read[idx][1] == 1:
        edges.extend([read[idx -1][0], 
                      read[idx -1][0] + read[idx][1]
                      ])
channels = [0,0,0,0,0]  
pb_seq = []
for e in event_list:
    toggle = []
    for chan in sequence:
        for pulse in chan:
            if e == pulse[0][0]:
                toggle.append(1)
            else:
                toggle.append(0)
    pb_seq.append(toggle)