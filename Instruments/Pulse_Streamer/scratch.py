
# # # laser = [[6,0], [20,1], [0,0]]
# # # mw = [[5, 0], [1,1], [20, 0]] 
# # # read = [[6.3, 0], [1,1], [9, 0], [1,1], [0,0]]

# # # ## also have types in Swabian Style
# # # laser_type_swab = [None, 'laser', None]
# # # mw_type_swab = [None, 'mw', None]
# # # read_type_swab = [None, 'read', None, 'read', None]


# # # pulses = [laser, mw, read]
# # # names = [laser_type_swab, mw_type_swab, read_type_swab]

# # # shift_value = 1.5
# # # scan_name = 'mw'
# # # for channel_idx, chan in enumerate(names):
# # #     for name_idx, name in enumerate(chan):
# # #         if name == scan_name:
# # #             pulse = pulses[channel_idx][name_idx]
# # #             start = pulse[0]
# # #             pulses[channel_idx][name_idx] = [pulse[0]+shift_value, pulse[1]]
# # #             for chan_pulse in pulses[channel_idx]:
# # #                 if chan_pulse[0]>start:
# # #                     chan_pulse[0] = chan_pulse[0]+shift_value
                    
# # # print(pulses)


# # # ## pulse streamer format

# # # laser_type_swab = [None, 'laser', None]
# # # mw_type_swab = [None, 'mw', None]
# # # read_type_swab = [None, 'read', None, 'read', None]

# # # laser = [[6,0], [20,1], [0,0]]
# # # mw = [[5, 0], [1,1], [20, 0]] 
# # # read = [[6.3, 0], [1,1], [9, 0], [1,1], [0,0]]

# # # ## Scanning MW pulse duration

# # # ## No shift of other at all
# # # laser = [[6,0], [20,1], [0,0]]
# # # mw = [[5, 0], [1+t,1], [20-t, 0]] 
# # # read = [[6.3, 0], [1,1], [9, 0], [1,1], [0,0]]

# # # ## shift in channel
# # # laser = [[6,0], [20,1], [0,0]]
# # # mw = [[5, 0], [1+t,1], [20, 0]] 
# # # read = [[6.3, 0], [1,1], [9, 0], [1,1], [0,0]]

# # # ##shift all chanenls
# # # laser = [[6+t,0], [20,1], [0,0]]
# # # mw = [[5, 0], [1+t,1], [20, 0]] 
# # # read = [[6.3+t, 0], [1,1], [9, 0], [1,1], [0,0]]

# # # def update_sequence():
# # #     shift_value = 1.5
# # #     scan_name = 'mw'
# # #     for channel_idx, chan in enumerate(names):
# # #         for name_idx, name in enumerate(chan):
# # #             if name == scan_name:
# # #                 shift_pulses(scan_type, names, pulses, 
# # #                    channel_idx, name_idx, shift_value)
# # #     return
    
# # # #duration_change()
# # # pulse = pulses[channel_idx][name_idx] 
# # # start = pulse[0]
# # # def shift_pulses():
# # #     if no_shift:
# # #         scan_no_shift(scan_type, names, pulses, 
# # #                    channel_idx, name_idx, shift_value)
# # #     elif shift_channel:
# # #         scan_shift_channel(scan_type, names, pulses, 
# # #                    channel_idx, name_idx, shift_value)
# # #     else shift_all:
# # #         scan_shift_all(scan_type, names, pulses, 
# # #                    channel_idx, name_idx, shift_value)
# # #     return

# # # def scan_shift_all(scan_type, names, pulses, 
# # #                    channel_idx, name_idx, shift_value):
# # #     if scan_type=='duration':
# # #         if add_time:
# # #             pulses[channel_idx][name_idx][0] += shift_value
# # #         else:
# # #             original_dur = pulses[channel_idx][name_idx-1][0]
# # #             pulses[channel_idx][name_idx-1][0] = shift_value
# # #         ## if sweept pulse is the first in the sequence, 
# # #         ## shift the index 1 to use it to check other pulse start
# # #         if pulses[channel_idx][name_idx-1:name_idx] == []:
# # #             name_idx += 1
# # #     elif scan_type == 'start':
# # #         if add_time:
# # #             pulses[channel_idx][name_idx][0] += shift_value
# # #             shift_for_other_pulses = shift_value
# # #         else:
# # #             original_start = pulses[channel_idx][name_idx][0]
# # #             pulses[channel_idx][name_idx][0] = shift_value
# # #             shift_for_other_pulses = original_start - shift_value
# # #     else:
# # #         print(f'{scan_type} not recognized, us "start" or "duration"')
# # #     ## looking at the other channels to shift the pulse that occurs 
# # #     ## before the scanned pulse, then break since only one shift per 
# # #     ## channel is need
# # #     for other_chan in names: 
# # #         if not other_chan==channel_idx:
# # #             for other_pulse in other_chan:
# # #                 if other_pulse[0] > pulses[channel_idx][name_idx]:
# # #                     other_pulse[0] += shift_for_other_pulses
# # #                     break
# # #     return
    
# # # def scan_shift_channel(scan_type, names, pulses, 
# # #                        channel_idx, name_idx, shift_value):
# # #     if add_time:
# # #         pulses[channel_idx][name_idx][0] += shift_value
# # #     else:
# # #         pulses[channel_idx][name_idx][0] = shift_value
# # #     return
    
# # # def scan_no_shift(scan_type, names, pulses, 
# # #                   channel_idx, name_idx, shift_value):
# # #     if scan_type == 'duration':
# # #         if add_time:
# # #             pulses[channel_idx][name_idx][0] += shift_value
# # #         else:
# # #             original_dur = pulses[channel_idx][name_idx][0]
# # #             pulses[channel_idx][name_idx][0] = shift_value
# # #         if not pulses[channel_idx][name_idx:name_idx+1] in [[], [0,0]]:
# # #             pulses[channel_idx][name_idx+1] += original_dur - shift_value
    
# # #     elif scan_type == 'start':
# # #         if add_time:
# # #             if pulses[channel_idx][name_idx-1:name_idx] in [[],[0,0]]:
# # #                 print(f'Pulse {pulses[channel_idx][name_idx]} in channel {channel_idx} cannot shift start time without a pulse before it.')
# # #                 ## if not prior pulse, do nothing
# # #             else:
# # #                 original_start = pulses[channel_idx][name_idx-1][0]
# # #                 pulses[channel_idx][name_idx-1][0] = shift_value
# # #         if not pulses[channel_idx][name_idx:name_idx+1] in [[], [0,0]]:
# # #             pulses[channel_idx][name_idx+1] =+ original_start - shift_value
# # #     else:
# # #         print(f'{scan_type} not recognized, us "start" or "duration"')
        
# # #     return


                    
# # # ## Scanning MW pulse start

# # # ## No shift of other at all
# # # laser = [[6,0], [20,1], [0,0]]
# # # mw = [[5+t, 0], [1,1], [20-t, 0]] 
# # # read = [[6.3, 0], [1,1], [9, 0], [1,1], [0,0]]

# # # ## shift in channel
# # # laser = [[6,0], [20,1], [0,0]]
# # # mw = [[5+t, 0], [1,1], [20, 0]] 
# # # read = [[6.3, 0], [1,1], [9, 0], [1,1], [0,0]]

# # # ##shift all chanenls
# # # laser = [[6+t,0], [20,1], [0,0]]
# # # mw = [[5+t, 0], [1,1], [20, 0]] 
# # # read = [[6.3+t, 0], [1,1], [9, 0], [1,1], [0,0]]

# import plotly.graph_objects as go

# import numpy as np
# from nicegui import ui

# def convert_to_swab(sequence):
#     new_sequence = []
#     for pattern in sequence:
#         new_pattern = []
#         duration_counter = 0
#         for pulse in pattern:
#             start, length = pulse
#             start = start-duration_counter
#             p1 = (start, 0)
#             p2 = (length, 1)
#             duration_counter = start+length
#             new_pattern.extend([p1, p2])
#         if not new_pattern[-1][1] == 0:
#             new_pattern.append((0,0))
#         new_sequence.append(new_pattern)
#     return new_sequence
    
    
# laser = [[6, 20]]
# mw = [[5,1]]
# read = [[6.3, 1], [16.3, 1]]

# pulses = [laser, mw, read]
# sequence = pulses #convert_to_swab(pulses)
# print(pulses)

# def sequence_duration(sequence):
#     durations = []
#     for chan in sequence:
#         for pulse in chan:
#             t=pulse[0] + pulse[1]
#             durations.append(t)
#     return max(durations)
    
# seq_duration = sequence_duration(sequence)

# plot_seq = np.zeros((len(sequence), seq_duration*1000))
# seq_points = np.arange(0, seq_duration, 0.001)

# # for c_idx, chan in enumerate(sequence):
# #     for p_idx, pulse in enumerate(chan):
# #         plot_seq[c_idx, 
# #                 int(pulse[0]*1000):int((pulse[0]+pulse[1])*1000)] = 1
# #         plot_seq[c_idx] = plot_seq[c_idx] + c_idx*1.1
# #         fig.add_trace(go.Scatter(x=seq_points, y=plot_seq))




# for c_idx, chan in enumerate(sequence):
#     for p_idx, pulse in enumerate(chan):
#         start = int(pulse[0])*1000
#         dur   = int(pulse[1])*1000
#         plot_seq[c_idx, start:start+dur] = 1*0.75
#     plot_seq[c_idx] += 1.15*c_idx
        
        
# fig_data =[]
# for idx, seq in enumerate(plot_seq):
#     fig_data.append({'type': 'scatter', 'name': f'Chan-{idx}', 
#                      'x': seq_points, 'y': seq})

# annotes = {
# 'x':5.0, 'y':1.15, 'xref':'x', 'yref':'x', 'text': 'rabi<br>duration', 
# 'showarrow':False,'ax':0, 'ay':0, 'align':'left', 'font': {'size':14, 'color':'#000000'},
# 'bgcolor': '#ffffff90', 'xanchor': 'right', 'yanchor':'bottom'
# }

# fig = {
#     'data': fig_data,
#     'layout': {
#         'margin': {'l': 30, 'r': 0, 't': 0, 'b': 30},
#         'plot_bgcolor': '#E5ECF6',
#         'xaxis': {'gridcolor': 'white'},
#         'yaxis': {'visible':False, 'gridcolor': 'white'},
#         'annotations': [annotes],
#     },
# }
# plot = ui.plotly(fig).classes('w-full h-full')

# def update_plot():
#     read = [[np.random.randint(0,20),3]]
#     pulses = [laser, mw, read]
#     sequence = pulses
#     seq_duration = sequence_duration(sequence)

#     plot_seq = np.zeros((len(sequence), seq_duration*1000))
#     seq_points = np.arange(0, seq_duration, 0.001)
    
#     for c_idx, chan in enumerate(sequence):
#         for p_idx, pulse in enumerate(chan):
#             start = int(pulse[0])*1000
#             dur   = int(pulse[1])*1000
#             plot_seq[c_idx, start:start+dur] = 1*0.75
#     plot_seq[c_idx] += 1.15*c_idx
            
#     fig_data =[]
#     for idx, seq in enumerate(plot_seq):
#         fig_data.append({'type': 'scatter', 'name': f'Chan-{idx}', 
#                         'x': seq_points, 'y': seq})
    
#     fig = {
#     'data': fig_data,
#     'layout': {
#         'margin': {'l': 30, 'r': 0, 't': 0, 'b': 30},
#         'plot_bgcolor': '#E5ECF6',
#         'xaxis': {'gridcolor': 'white'},
#         'yaxis': {'visible':False, 'gridcolor': 'white'},
#     },
#     }
#     plot.figure['data'] = []
#     plot.figure['annotaionts'] = [{}]
#     ui.update(plot)
#     print(seq)
#     return

# ui.button('add data', on_click = update_plot)

# # import numpy as np
# # from matplotlib import pyplot as plt
# # from nicegui import ui

# # with ui.pyplot(figsize=(6, 6)):
# #     x = seq_points
# #     plt.plot(x, plot_seq[0], '-')
# #     plt.plot(x, plot_seq[1], '-')
# #     plt.plot(x, plot_seq[2], '-')

# # from nicegui import ui
# # from dataclasses import dataclass, field

# # @dataclass
# # class dropdown:
# #     vals: list = field(default_factory=list)

# # @dataclass
# # class new_val:
# #     num: int = 0

# # a = dropdown()
# # b = new_val()

# # def add():
# #     a.vals.append(b.num)
# #     b.num+=1
# #     sel._update_options()
# #     print([i for i in range(len(a.vals))])
# #     return


# # sel = ui.select('')
# # ui.button('add', on_click=add)



# ui.run(port=8666)

# class Test:
#     """This is the doc string
#     """        
#     def __init__(self):

#         print('hello')

def convert_to_swab(sequence, names):
    new_sequence = []
    new_names = []
    for ch_idx, chan in enumerate(sequence):
        new_pattern = []
        names_holder = []
        duration_counter = 0
        for p_idx, pulse in enumerate(chan):
            start, length = pulse
            start = start-duration_counter
            p1 = (start, 0)
            p2 = (length, 1)
            duration_counter = start+length
            new_pattern.extend([p1, p2])
            names_holder.extend(('Zero', names[ch_idx][p_idx]))
        if not new_pattern[-1][1] == 0:
            ## capping all patterns with (0,0) will pad anything that is 
            ## shorter than the longest pulse pattern
            new_pattern.append((0,0))
            names_holder.append('Zero')
        new_sequence.append(new_pattern)
        new_names.append(names_holder)
    return new_sequence, new_names

laser = [[6, 20]]
mw = [[5,1]]
read = [[6.3, 1], [16.3, 1]]

ln = ['None']
mn = ['mw']
rn = ['None', 'None']

pulses = [laser, mw, read]
names = [ln, mn, rn]
sequence, new_names = convert_to_swab(pulses, names)
print(sequence, new_names)
