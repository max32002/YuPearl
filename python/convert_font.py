#!/usr/bin/env python3
#encoding=utf-8

import os
import glob

# distance between two points
from math import hypot

def check_clockwise(poly):
    clockwise = True
    area_total=0
    poly_lengh = len(poly)
    #print('check poly: (%d,%d)' % (poly[0][0],poly[0][1]))
    for idx in range(poly_lengh):
        #item_sum = ((poly[(idx+1)%poly_lengh][0]-poly[(idx+0)%poly_lengh][0]) * (poly[(idx+1)%poly_lengh][1]-poly[(idx+0)%poly_lengh][1]))
        item_sum = ((poly[(idx+0)%poly_lengh][0]*poly[(idx+1)%poly_lengh][1]) - (poly[(idx+1)%poly_lengh][0]*poly[(idx+0)%poly_lengh][1]))
        #print(idx, poly[idx][0], poly[idx][1], item_sum)
        area_total += item_sum
    #print("area_total:",area_total)
    if area_total >= 0:
        clockwise = not clockwise
    return clockwise

def average(lst): 
    return sum(lst) / len(lst) 

def is_same_direction_list(args,deviation=0):
    ret = True
    args_average=average(args)
    #print("args_average:", args_average)

    direction = -1
    if args[0] <= args_average:
        direction = 1
    
    idx=0
    args_count = len(args)
    for item in args:
        idx+=1
        if idx == args_count:
            break

        if direction==1:
            if (args[idx]+deviation)<item and (args[idx]-deviation)<item:
                ret = False
                break
        else:
            if (args[idx]+deviation)>item and (args[idx]-deviation)>item:
                ret = False
                break
    return ret

def is_same_direction(*args,deviation=0):
    return is_same_direction_list(args,deviation=deviation)

# common functions.
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def field_right( s, first, is_include_symbol=False):
    try:
        start = s.index(first )
        if not is_include_symbol:
            start += len(first )
        return s[start:]
    except ValueError:
        return ""

def field_left( s, first, is_include_symbol=False):
    try:
        start = s.index(first )
        if is_include_symbol:
            start += len(first )
        return s[:start]
    except ValueError:
        return ""

def write_to_file(filename_input, stroke_dict, readonly):
    filename_input_new = filename_input + ".tmp"

    myfile = open(filename_input, 'r')
    myfile_new = open(filename_input_new, 'w')
    code_begin_string = 'SplineSet'
    code_begin_string_length = len(code_begin_string)
    code_end_string = 'EndSplineSet'
    code_end_string_length = len(code_end_string)

    is_code_flag=False

    stroke_index = 0
    for x_line in myfile:
        if not is_code_flag:
            # check begin.

            if code_begin_string == x_line[:code_begin_string_length]:
                is_code_flag = True

            myfile_new.write(x_line)

        else:
            # check end
            if code_end_string == x_line[:code_end_string_length]:

                is_code_flag = False

                #flush memory to disl
                for key in stroke_dict.keys():
                    for new_line in stroke_dict[key]['code']:
                        myfile_new.write(new_line)

                myfile_new.write(x_line)
                #break

    myfile.close()
    myfile_new.close()

    if not readonly:
        os.remove(filename_input)
        os.rename(filename_input_new, filename_input)

    return stroke_dict

# RULE # 5
# 向下的圓頭增加節點變平頭。
# PS: 因為 array size change, so need redo.
# PS: 這個要最後執行，不然會因此長角。
def travel_nodes_for_rule_5(stroke_dict,key,resume_idx):
    redo_travel=False

    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 5
    if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            if idx <= resume_idx:
                # skip traveled nodes.
                continue

            is_match_pattern = False

            #print(idx,"debug code5:",stroke_dict[key]['code'][idx])
            # 單一點的圓頭轉方頭。(向上/向下頭)
            # ? l c c l
            #if idx==18:
            if False:
                for t_idx in range(5):
                    print(t_idx, "t_idx:",stroke_dict[key]['t'][(idx+t_idx)%nodes_length])
                    print(t_idx, "code:",stroke_dict[key]['code'][(idx+t_idx)%nodes_length])

            if stroke_dict[key]['t'][(idx+1)%nodes_length] != 'c':
                if stroke_dict[key]['t'][(idx+2)%nodes_length] == 'c':
                    if stroke_dict[key]['t'][(idx+3)%nodes_length] == 'c' :
                        if stroke_dict[key]['t'][(idx+4)%nodes_length] != 'c':
                            is_match_pattern = True

            if is_match_pattern:
                #print(idx,"match ?lccl:",stroke_dict[key]['code'][idx])
                is_match_pattern=False
                if stroke_dict[key]['x'][idx+0] == stroke_dict[key]['x'][(idx+1)%nodes_length]:
                    if ' ' + str(stroke_dict[key]['x'][idx+0]) + ' ' in stroke_dict[key]['code'][(idx+2)%nodes_length]:
                        if stroke_dict[key]['x'][(idx+3)%nodes_length] == stroke_dict[key]['x'][(idx+4)%nodes_length]:
                            if ' ' + str(stroke_dict[key]['y'][(idx+2)%nodes_length]) + ' ' in stroke_dict[key]['code'][(idx+3)%nodes_length]:
                                is_match_pattern=True
                                #print("match rule #5")
                                #print(idx,"code:",stroke_dict[key]['code'][idx])

            if is_match_pattern:
                # from bottom to top
                direction = +1
                if stroke_dict[key]['y'][idx+0] > stroke_dict[key]['y'][(idx+1)%nodes_length]:
                    # 單一點，向下的圓頭轉方頭。
                    direction = -1

                old_code_array = stroke_dict[key]['code'][(idx+2)%nodes_length].split(' ')
                old_code_array[5] = str(stroke_dict[key]['x'][idx+0]+(16*direction))
                stroke_dict[key]['code'][(idx+2)%nodes_length] = ' '.join(old_code_array)
                stroke_dict[key]['x'][(idx+2)%nodes_length] = stroke_dict[key]['x'][idx+0]+16

                new_x = stroke_dict[key]['x'][(idx+4)%nodes_length]-(16*direction)
                new_y = stroke_dict[key]['y'][(idx+2)%nodes_length]
                new_code = " %d %d l 2\n" % (new_x, new_y)

                stroke_dict[key]['code'].insert((idx+3)%nodes_length,new_code)
                stroke_dict[key]['x'].insert((idx+3)%nodes_length,new_x)
                stroke_dict[key]['y'].insert((idx+3)%nodes_length,new_y)
                stroke_dict[key]['t'].insert((idx+3)%nodes_length,'l')

                redo_travel=True
                resume_idx = idx
                break

    return redo_travel, resume_idx, stroke_dict

# RULE # 8
# 右邊橫線，啟始點在右邊的中間點上。
# PS: 因為 array size change, so need redo.
# PS: #8 可以處理，右上＋左下長角的case.
def travel_nodes_for_rule_8(stroke_dict,key,resume_idx):
    redo_travel=False

    TOO_LONG_LENGTH = 190

    idx=0
    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 5
    if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            if idx <= resume_idx:
                # skip traveled nodes.
                continue

            is_match_pattern = False

            # match: lclc
            if stroke_dict[key]['t'][(idx+0)%nodes_length] != 'c':
                if stroke_dict[key]['t'][(idx+1)%nodes_length] == 'c':
                    if stroke_dict[key]['t'][(idx+2)%nodes_length] != 'c':
                        if stroke_dict[key]['t'][(idx+3)%nodes_length] == 'c':
                            is_match_pattern = True

            if is_match_pattern:
                is_match_pattern = False
                if ' ' + str(stroke_dict[key]['y'][idx+0]) + ' ' in stroke_dict[key]['code'][(idx+1)%nodes_length]:
                    if stroke_dict[key]['y'][(idx+1)%nodes_length] == stroke_dict[key]['y'][(idx+1)%nodes_length]:
                        if ' ' + str(stroke_dict[key]['x'][(idx+2)%nodes_length]) + ' ' in stroke_dict[key]['code'][(idx+1)%nodes_length]:
                            if ' ' + str(stroke_dict[key]['x'][(idx+2)%nodes_length]) + ' ' in stroke_dict[key]['code'][(idx+3)%nodes_length]:
                                if stroke_dict[key]['y'][(idx+4)%nodes_length] == stroke_dict[key]['y'][(idx+3)%nodes_length]:
                                    is_match_pattern = True

            if is_match_pattern:
                
                if abs(stroke_dict[key]['y'][(idx+0)%nodes_length] - stroke_dict[key]['y'][(idx+2)%nodes_length]) > TOO_LONG_LENGTH:
                    #too long, about.
                    #print("too far")
                    continue

                direction=1     # 向右上長。
                if stroke_dict[key]['y'][idx] < stroke_dict[key]['y'][(idx+1)%nodes_length]:
                    direction= -1   # 向左下長。

                #print("match rule #8")
                #print(idx,"code:",stroke_dict[key]['code'][idx])

                # match rule 1
                #print("match rule #1")
                #print(idx,"code:",stroke_dict[key]['code'][idx])
                
                #print(idx,"code before:",stroke_dict[key]['code'])
                #print("direction:", direction)
                if False:
                    for t_idx in range(5):
                        print(t_idx, "x_idx:",stroke_dict[key]['x'][(idx+t_idx)%nodes_length])
                        print(t_idx, "y_idx:",stroke_dict[key]['y'][(idx+t_idx)%nodes_length])
                        print(t_idx, "t_idx:",stroke_dict[key]['t'][(idx+t_idx)%nodes_length])
                        print(t_idx, "code:",stroke_dict[key]['code'][(idx+t_idx)%nodes_length])


                old_code_array = stroke_dict[key]['code'][(idx+1)%nodes_length].split(' ')

                new_x1 = int(old_code_array[1]) - (32 * direction)
                new_x2 = int(old_code_array[3]) - (32 * direction)
                new_x3 = int(old_code_array[5])
                
                new_y1 = int(old_code_array[2])
                new_y2 = int(old_code_array[4])
                new_y3 = int(old_code_array[6]) + (98 * direction)
                new_code = ' %d %d %d %d %d %d c 1\n' % (new_x1,new_y1,new_x2,new_y2,new_x3,new_y3)
                stroke_dict[key]['code'].insert((idx+1)%nodes_length,new_code)
                stroke_dict[key]['x'].insert((idx+1)%nodes_length,new_x3)
                stroke_dict[key]['y'].insert((idx+1)%nodes_length,new_y3)
                stroke_dict[key]['t'].insert((idx+1)%nodes_length,'c')
                #print(idx,"code after:",new_code)

                redo_travel=True
                resume_idx = idx
                break

    return redo_travel, resume_idx, stroke_dict

# RULE # 9
# 橫線右頭，要向下
# PS: 因為 array size change, so need redo.
# PS: #9 可以同時處理橫線的「向上＋向下」長角.
# PS: 我們目前的規則，是點的 y axis具同一個方向性，如果未來長出來的角會產生同一個方向，需要再加入更多例外，不然會互相沖突。
def travel_nodes_for_rule_9(stroke_dict,key,resume_idx):
    redo_travel=False

    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 5
    if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            if idx <= resume_idx:
                # skip traveled nodes.
                continue

            is_match_pattern = False

            # check ?-l-c-c-l
            #print(idx,"code1:",stroke_dict[key]['code'][idx])
            if stroke_dict[key]['t'][(idx+1) % nodes_length] != 'c':
                if stroke_dict[key]['t'][(idx+2) % nodes_length] == 'c':
                    if stroke_dict[key]['t'][(idx+3) % nodes_length] == 'c':
                        if stroke_dict[key]['t'][(idx+4) % nodes_length] != 'c':
                            is_match_pattern = True

            if is_match_pattern:
                is_match_pattern = False
                if stroke_dict[key]['y'][(idx+0) % nodes_length] == stroke_dict[key]['y'][(idx+1) % nodes_length]:
                    if ' ' + str(stroke_dict[key]['y'][(idx+0) % nodes_length]) + ' ' in stroke_dict[key]['code'][(idx+2) % nodes_length]:
                        if stroke_dict[key]['y'][(idx+4) % nodes_length] == stroke_dict[key]['y'][(idx+3) % nodes_length]:
                            if ' ' + str(stroke_dict[key]['x'][(idx+2) % nodes_length]) + ' ' in stroke_dict[key]['code'][(idx+3) % nodes_length]:
                                is_match_pattern = True

            if is_match_pattern:
                #print("match rule #9")
                #print(idx,"code:",stroke_dict[key]['code'][idx])
                y_array = []
                for t_idx in range(rule_need_lines):
                    y_array.append(stroke_dict[key]['y'][(idx+t_idx) % nodes_length])

                direction_flag = is_same_direction_list(y_array,deviation=5)
                is_match_pattern = direction_flag

            direction=1    # draw right up side
            if stroke_dict[key]['y'][(idx+2)%nodes_length] - stroke_dict[key]['y'][(idx+1)%nodes_length] > 0:
                # line is going to left top.
                direction=-1    # draw right up side

            # 解決非黑色區塊的「外部曲線」，不應自動畫線。
            if is_match_pattern:
                # check direction wrong.
                if direction==-1:
                    if stroke_dict[key]['x'][(idx+1) % nodes_length] > stroke_dict[key]['x'][(idx+0) % nodes_length]:
                        is_match_pattern = False
                        #print("catch wrong direction")

                if direction==1:
                    if stroke_dict[key]['x'][(idx+1) % nodes_length] < stroke_dict[key]['x'][(idx+0) % nodes_length]:
                        is_match_pattern = False
                        #print("catch wrong direction")

            if is_match_pattern:
                #print("match rule #9 (with same direction)")
                #print(idx,"code:",stroke_dict[key]['code'][idx])

                if False:
                    for t_idx in range(5):
                        print(t_idx, "x,y,t_idx:",stroke_dict[key]['x'][(idx+t_idx)%nodes_length],stroke_dict[key]['y'][(idx+t_idx)%nodes_length],stroke_dict[key]['t'][(idx+t_idx)%nodes_length])
                        print(t_idx, "code:",stroke_dict[key]['code'][(idx+t_idx)%nodes_length])

                # 由於會造成交叉影響，增加方向檢查。
                #print("direction:", direction)

                
                #(idx,"code before:",stroke_dict[key]['code'])
                new_x1 = stroke_dict[key]['x'][(idx+2)%nodes_length] - (32 * direction)
                new_x2 = new_x1
                new_x3 = stroke_dict[key]['x'][(idx+2)%nodes_length]
                
                new_y1 = stroke_dict[key]['y'][(idx+0)%nodes_length]
                new_y2 = new_y1
                new_y3 = stroke_dict[key]['y'][(idx+2)%nodes_length] + (98 * direction)
                new_code = ' %d %d %d %d %d %d c 1\n' % (new_x1,new_y1,new_x2,new_y2,new_x3,new_y3)
                stroke_dict[key]['code'].insert((idx+2)%nodes_length,new_code)
                stroke_dict[key]['x'].insert((idx+2)%nodes_length,new_x3)
                stroke_dict[key]['y'].insert((idx+2)%nodes_length,new_y3)
                stroke_dict[key]['t'].insert((idx+2)%nodes_length,'c')
                #print(idx,"new_code after:",new_code)

                redo_travel=True
                resume_idx = idx
                break

    return redo_travel, resume_idx, stroke_dict


# start to travel nodes for [RULE #10] 
# 斜線的圓頭改方頭。
# PS: 這個「問題」太多！暫不使用。
def travel_nodes_for_rule_10(stroke_dict,key,idx):
    idx=0
    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 5
    if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            is_match_pattern = False

            # 斜線
            # check ?-c-c-c or c-m-c-c-c
            #print(idx,"code1:",stroke_dict[key]['code'][idx])
            #if stroke_dict[key]['t'][(idx+0) % nodes_length] != 'c':
            #if True:

            # because first point on idx+1
            if stroke_dict[key]['t'][(idx+1) % nodes_length] == 'c':
                if stroke_dict[key]['t'][(idx+2) % nodes_length] == 'c':
                    if stroke_dict[key]['t'][(idx+3) % nodes_length] == 'c':
                        is_match_pattern = True

            if stroke_dict[key]['t'][(idx+0) % nodes_length] == 'c':
                if stroke_dict[key]['t'][(idx+1) % nodes_length] == 'm':
                    if stroke_dict[key]['t'][(idx+2) % nodes_length] == 'c':
                        if stroke_dict[key]['t'][(idx+3) % nodes_length] == 'c':
                            is_match_pattern = True

            if not is_match_pattern:
                continue

            code_node_2_array = stroke_dict[key]['code'][(idx+2) % nodes_length].split(' ')
            p2_x = stroke_dict[key]['x'][(idx+1) % nodes_length]
            p2_y = stroke_dict[key]['y'][(idx+1) % nodes_length]
            p5_x = stroke_dict[key]['x'][(idx+2) % nodes_length]
            p5_y = stroke_dict[key]['y'][(idx+2) % nodes_length]
            p6_x = stroke_dict[key]['x'][(idx+3) % nodes_length]
            p6_y = stroke_dict[key]['y'][(idx+3) % nodes_length]
            p3_x = int(code_node_2_array[1])
            p3_y = int(code_node_2_array[2])

            # two points must not too far.
            range_too_long = 180.0
            dist = hypot(p2_x - p5_x, p2_y - p5_y)
            #print("dist:", dist)
            if dist >= range_too_long:
                is_match_pattern = False
                continue

            # must match.
            if code_node_2_array[1] != code_node_2_array[3]:
                continue

            # must match
            if code_node_2_array[2] != code_node_2_array[4]:
                continue

            #print(idx,"code 10:",stroke_dict[key]['code'][idx])
            if False:
                for t_idx in range(5):
                    print(t_idx, "x,y,t_idx:",stroke_dict[key]['x'][(idx+t_idx)%nodes_length],stroke_dict[key]['y'][(idx+t_idx)%nodes_length],stroke_dict[key]['t'][(idx+t_idx)%nodes_length])
                    print(t_idx, "code:",stroke_dict[key]['code'][(idx+t_idx)%nodes_length])


            y_array = []
            x_array = []
            for t_idx in range(rule_need_lines):
                y_array.append(stroke_dict[key]['y'][(idx+t_idx) % nodes_length])
                x_array.append(stroke_dict[key]['x'][(idx+t_idx) % nodes_length])


            # to many points in line, if some point let rult not match, 
            # we use this variable to allow not excepted case.
            point_accuracy = 20  # unit
            y_direction_flag = is_same_direction_list(y_array,deviation=point_accuracy)
            x_direction_flag = is_same_direction_list(x_array,deviation=point_accuracy)


            match_p3_max = False

            # / 的線，y axis 會 on-line.
            #print('p3_x,p2_x,p6_x:',p3_x,p2_x,p6_x)
            #print('p3_y,p2_y,p6_y:',p3_y,p2_y,p6_y)
            if y_direction_flag:
                # match_shape=='/'
                #print("match share /")
                if p3_x >= p2_x:
                    if p3_x >= p6_x:
                        match_p3_max = True
                
                if p3_x <= p2_x:
                    if p3_x <= p6_x:
                        match_p3_max = True

            if x_direction_flag:
                #print("match share \\")
                # match_shape=='\\':
                if p3_y >= p2_y:
                    if p3_y >= p6_y:
                        match_p3_max = True
                
                if p3_y <= p2_y:
                    if p3_y <= p6_y:
                        match_p3_max = True
                        
            if match_p3_max:
                #print("match final rule #10")
                #print(idx,"match code:",stroke_dict[key]['code'][idx])
                new_p3_x = int((p2_x + p5_x) / 2)
                new_p3_y = int((p2_y + p5_y) / 2)

                old_code_array = stroke_dict[key]['code'][(idx+2)%nodes_length].split(' ')
                old_code_array[1] = str(new_p3_x)
                old_code_array[2] = str(new_p3_y)
                old_code_array[3] = str(new_p3_x)
                old_code_array[4] = str(new_p3_y)
                new_code = ' '.join(old_code_array)

                #print(idx,"old code:",stroke_dict[key]['code'][(idx+2)%nodes_length])
                #print(idx,"new code:",new_code)
                stroke_dict[key]['code'][(idx+2)%nodes_length] = new_code
    return stroke_dict


# RULE # 11
# 多角的橫線圓頭，正規化為「標準」圓頭。
# PS: 因為 array size change, so need redo.
def travel_nodes_for_rule_11(stroke_dict,key,resume_idx):
    redo_travel=False

    TOO_LONG_LENGTH = 190

    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 6
    if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            if idx <= resume_idx:
                # skip traveled nodes.
                continue

            is_match_pattern = False

            #print(idx,"debug code5:",stroke_dict[key]['code'][idx])
            # 單一點的圓頭轉方頭。(向上/向下頭)
            # ? l c c c l

            if stroke_dict[key]['t'][(idx+1)%nodes_length] != 'c':
                if stroke_dict[key]['t'][(idx+2)%nodes_length] == 'c':
                    if stroke_dict[key]['t'][(idx+3)%nodes_length] == 'c' :
                        if stroke_dict[key]['t'][(idx+4)%nodes_length] == 'c' :
                            if stroke_dict[key]['t'][(idx+5)%nodes_length] != 'c':
                              is_match_pattern = True

            if is_match_pattern:
                if(abs(stroke_dict[key]['y'][(idx+5)%nodes_length]-stroke_dict[key]['y'][(idx+0)%nodes_length]) > TOO_LONG_LENGTH):
                    is_match_pattern = False

            if is_match_pattern:
                #print(idx,"match ?lccl:",stroke_dict[key]['code'][idx])
                is_match_pattern=False
                if stroke_dict[key]['y'][idx+0] == stroke_dict[key]['y'][(idx+1)%nodes_length]:
                    if ' ' + str(stroke_dict[key]['y'][idx+0]) + ' ' in stroke_dict[key]['code'][(idx+2)%nodes_length]:
                        if stroke_dict[key]['y'][(idx+4)%nodes_length] == stroke_dict[key]['y'][(idx+5)%nodes_length]:
                            is_match_pattern=True

            if is_match_pattern:
                # sould not happen in same x axis.
                x_array = []
                y_array = []
                for t_idx in range(rule_need_lines):
                    y_array.append(stroke_dict[key]['y'][(idx+t_idx) % nodes_length])
                    x_array.append(stroke_dict[key]['x'][(idx+t_idx) % nodes_length])
                direction_flag = is_same_direction_list(x_array,deviation=10)
                if direction_flag:
                    is_match_pattern=False

            if is_match_pattern:
                # must '匚' shape only.
                if stroke_dict[key]['x'][(idx+1)%nodes_length] > stroke_dict[key]['x'][(idx+3)%nodes_length]:
                    if stroke_dict[key]['x'][(idx+1)%nodes_length] < stroke_dict[key]['x'][(idx+2)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+1)%nodes_length] < stroke_dict[key]['x'][(idx+4)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+5)%nodes_length] <= stroke_dict[key]['x'][(idx+3)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+5)%nodes_length] <= stroke_dict[key]['x'][(idx+2)%nodes_length]:
                        is_match_pattern = False

                if stroke_dict[key]['x'][(idx+1)%nodes_length] < stroke_dict[key]['x'][(idx+3)%nodes_length]:
                    if stroke_dict[key]['x'][(idx+1)%nodes_length] > stroke_dict[key]['x'][(idx+2)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+1)%nodes_length] > stroke_dict[key]['x'][(idx+4)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+5)%nodes_length] >= stroke_dict[key]['x'][(idx+3)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+5)%nodes_length] >= stroke_dict[key]['x'][(idx+2)%nodes_length]:
                        is_match_pattern = False

            # from top to bottom
            direction = +1
            if stroke_dict[key]['y'][idx+0] < stroke_dict[key]['y'][(idx+4)%nodes_length]:
                # from bottom to top
                direction = -1

            # 解決非黑色區塊的「外部曲線」，不應自動畫線。
            if is_match_pattern:
                # check direction wrong.
                if direction==-1:
                    if stroke_dict[key]['x'][(idx+1) % nodes_length] > stroke_dict[key]['x'][(idx+0) % nodes_length]:
                        is_match_pattern = False
                        #print("catch wrong direction")

                if direction==1:
                    if stroke_dict[key]['x'][(idx+1) % nodes_length] < stroke_dict[key]['x'][(idx+0) % nodes_length]:
                        is_match_pattern = False
                        #print("catch wrong direction")

            if is_match_pattern:
                if False:
                    for t_idx in range(6):
                        print(t_idx, "t_idx:",stroke_dict[key]['t'][(idx+t_idx)%nodes_length])
                        print(t_idx, "code:",stroke_dict[key]['code'][(idx+t_idx)%nodes_length])

            if is_match_pattern:
                #print("match rule #11")
                #print(idx,"code:",stroke_dict[key]['code'][idx])

                new_x = stroke_dict[key]['x'][(idx+1)%nodes_length]
                new_y = stroke_dict[key]['y'][(idx+1)%nodes_length]
                old_code_array = stroke_dict[key]['code'][(idx+2)%nodes_length].split(' ')
                old_code_array[1] = str(new_x+(66*direction))
                old_code_array[2] = str(new_y)
                old_code_array[3] = str(new_x+(66*direction))
                old_code_array[4] = str(new_y)
                old_code_array[5] = str(new_x+(66*direction))
                old_code_array[6] = str(new_y-(66*direction))
                stroke_dict[key]['code'][(idx+2)%nodes_length] = ' '.join(old_code_array)
                stroke_dict[key]['x'][(idx+2)%nodes_length] = new_x+(66*direction)
                stroke_dict[key]['y'][(idx+2)%nodes_length] = new_y-(66*direction)

                old_code_array = stroke_dict[key]['code'][(idx+4)%nodes_length].split(' ')
                old_code_array[1] = str(new_x+(66*direction))
                old_code_array[3] = str(new_x+(66*direction))
                old_code_array[5] = str(new_x)
                stroke_dict[key]['code'][(idx+4)%nodes_length] = ' '.join(old_code_array)
                stroke_dict[key]['x'][(idx+4)%nodes_length] = new_x

                # [BE CAREFUL!]
                nodes_length = len(stroke_dict[key]['code'])
                if stroke_dict[key]['t'][(idx+5)%nodes_length]=='m':
                    if not(old_code_array[5]==stroke_dict[key]['x'][(idx+5)%nodes_length] and old_code_array[6]==stroke_dict[key]['y'][(idx+5)%nodes_length]):
                        # cause not close spline!
                        old_code_array[5] = str(stroke_dict[key]['x'][(idx+5)%nodes_length])
                        old_code_array[6] = str(stroke_dict[key]['y'][(idx+5)%nodes_length])
                        stroke_dict[key]['code'][(idx+4)%nodes_length] = ' '.join(old_code_array)
                        stroke_dict[key]['x'][(idx+4)%nodes_length] = stroke_dict[key]['x'][(idx+5)%nodes_length]
                        stroke_dict[key]['y'][(idx+4)%nodes_length] = stroke_dict[key]['y'][(idx+5)%nodes_length]


                del stroke_dict[key]['code'][(idx+3)%nodes_length]
                del stroke_dict[key]['x'][(idx+3)%nodes_length]
                del stroke_dict[key]['y'][(idx+3)%nodes_length]
                del stroke_dict[key]['t'][(idx+3)%nodes_length]

                if False:
                    nodes_length = len(stroke_dict[key]['code'])
                    for t_idx in range(rule_need_lines):
                        print(t_idx, "x,y,t_idx:",stroke_dict[key]['x'][(idx+t_idx)%nodes_length],stroke_dict[key]['y'][(idx+t_idx)%nodes_length],stroke_dict[key]['t'][(idx+t_idx)%nodes_length])
                        print(t_idx, "code:",stroke_dict[key]['code'][(idx+t_idx)%nodes_length])

                redo_travel=True
                resume_idx = idx+1
                break

    return redo_travel, resume_idx, stroke_dict


# RULE # 12
# 多角的橫線圓頭，正規化為「標準」圓頭。
# PS: 因為 array size change, so need redo.
def travel_nodes_for_rule_12(stroke_dict,key,resume_idx):
    redo_travel=False

    TOO_LONG_LENGTH = 190

    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 7
    if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            if idx <= resume_idx:
                # skip traveled nodes.
                continue

            is_match_pattern = False

            #print(idx,"debug code5:",stroke_dict[key]['code'][idx])
            # 單一點的圓頭轉方頭。(向上/向下頭)
            # ? l c c c c l
            #if idx==18:
            if False:
                for t_idx in range(6):
                    print(t_idx, "x,y,t_idx:",stroke_dict[key]['x'][(idx+t_idx)%nodes_length],stroke_dict[key]['y'][(idx+t_idx)%nodes_length],stroke_dict[key]['t'][(idx+t_idx)%nodes_length])
                    print(t_idx, "code:",stroke_dict[key]['code'][(idx+t_idx)%nodes_length])

            if stroke_dict[key]['t'][(idx+1)%nodes_length] != 'c':
                if stroke_dict[key]['t'][(idx+2)%nodes_length] == 'c':
                    if stroke_dict[key]['t'][(idx+3)%nodes_length] == 'c' :
                        if stroke_dict[key]['t'][(idx+4)%nodes_length] == 'c' :
                            if stroke_dict[key]['t'][(idx+5)%nodes_length] == 'c' :
                                if stroke_dict[key]['t'][(idx+6)%nodes_length] != 'c':
                                  is_match_pattern = True

            if is_match_pattern:
                # sould not happen in same x axis.
                x_array = []
                y_array = []
                for t_idx in range(rule_need_lines):
                    y_array.append(stroke_dict[key]['y'][(idx+t_idx) % nodes_length])
                    x_array.append(stroke_dict[key]['x'][(idx+t_idx) % nodes_length])
                direction_flag = is_same_direction_list(x_array,deviation=10)
                if direction_flag:
                    is_match_pattern=False

            if is_match_pattern:
                if(abs(stroke_dict[key]['y'][(idx+6)%nodes_length]-stroke_dict[key]['y'][(idx+0)%nodes_length]) > TOO_LONG_LENGTH):
                    is_match_pattern = False

            if is_match_pattern:
                #print(idx,"match ?lccl:",stroke_dict[key]['code'][idx])
                is_match_pattern=False
                if stroke_dict[key]['y'][idx+0] == stroke_dict[key]['y'][(idx+1)%nodes_length]:
                    if ' ' + str(stroke_dict[key]['y'][idx+0]) + ' ' in stroke_dict[key]['code'][(idx+2)%nodes_length]:
                        if stroke_dict[key]['y'][(idx+5)%nodes_length] == stroke_dict[key]['y'][(idx+6)%nodes_length]:
                            is_match_pattern=True

            if is_match_pattern:
                # must '匚' shape only.
                if stroke_dict[key]['x'][(idx+1)%nodes_length] > stroke_dict[key]['x'][(idx+3)%nodes_length]:
                    if stroke_dict[key]['x'][(idx+1)%nodes_length] < stroke_dict[key]['x'][(idx+2)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+1)%nodes_length] < stroke_dict[key]['x'][(idx+4)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+6)%nodes_length] <= stroke_dict[key]['x'][(idx+3)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+6)%nodes_length] <= stroke_dict[key]['x'][(idx+2)%nodes_length]:
                        is_match_pattern = False

                if stroke_dict[key]['x'][(idx+1)%nodes_length] < stroke_dict[key]['x'][(idx+3)%nodes_length]:
                    if stroke_dict[key]['x'][(idx+1)%nodes_length] > stroke_dict[key]['x'][(idx+2)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+1)%nodes_length] > stroke_dict[key]['x'][(idx+4)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+6)%nodes_length] >= stroke_dict[key]['x'][(idx+3)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['x'][(idx+6)%nodes_length] >= stroke_dict[key]['x'][(idx+2)%nodes_length]:
                        is_match_pattern = False

            # from top to bottom
            direction = +1
            if stroke_dict[key]['y'][idx+0] < stroke_dict[key]['y'][(idx+5)%nodes_length]:
                # from bottom to top
                direction = -1

            # 解決非黑色區塊的「外部曲線」，不應自動畫線。
            if is_match_pattern:
                # check direction wrong.
                if direction==-1:
                    if stroke_dict[key]['x'][(idx+1) % nodes_length] > stroke_dict[key]['x'][(idx+0) % nodes_length]:
                        is_match_pattern = False
                        #print("catch wrong direction")

                if direction==1:
                    if stroke_dict[key]['x'][(idx+1) % nodes_length] < stroke_dict[key]['x'][(idx+0) % nodes_length]:
                        is_match_pattern = False
                        #print("catch wrong direction")

            if is_match_pattern:
                #print("match rule #12")
                #print(idx,"code:",stroke_dict[key]['code'][idx])

                new_x = stroke_dict[key]['x'][(idx+1)%nodes_length]
                new_y = stroke_dict[key]['y'][(idx+1)%nodes_length]
                old_code_array = stroke_dict[key]['code'][(idx+2)%nodes_length].split(' ')
                old_code_array[1] = str(new_x+(66*direction))
                old_code_array[2] = str(new_y)
                old_code_array[3] = str(new_x+(66*direction))
                old_code_array[4] = str(new_y)
                old_code_array[5] = str(new_x+(66*direction))
                old_code_array[6] = str(new_y-(66*direction))
                stroke_dict[key]['code'][(idx+2)%nodes_length] = ' '.join(old_code_array)
                stroke_dict[key]['x'][(idx+2)%nodes_length] = new_x+(66*direction)
                stroke_dict[key]['y'][(idx+2)%nodes_length] = new_y-(66*direction)


                old_code_array = stroke_dict[key]['code'][(idx+5)%nodes_length].split(' ')
                old_code_array[1] = str(new_x+(66*direction))
                old_code_array[3] = str(new_x+(66*direction))
                old_code_array[5] = str(new_x)
                stroke_dict[key]['code'][(idx+5)%nodes_length] = ' '.join(old_code_array)
                stroke_dict[key]['x'][(idx+5)%nodes_length] = new_x

                del stroke_dict[key]['code'][(idx+3)%nodes_length]
                del stroke_dict[key]['x'][(idx+3)%nodes_length]
                del stroke_dict[key]['y'][(idx+3)%nodes_length]
                del stroke_dict[key]['t'][(idx+3)%nodes_length]

                del stroke_dict[key]['code'][(idx+3)%nodes_length]
                del stroke_dict[key]['x'][(idx+3)%nodes_length]
                del stroke_dict[key]['y'][(idx+3)%nodes_length]
                del stroke_dict[key]['t'][(idx+3)%nodes_length]

                redo_travel=True
                resume_idx = idx+1
                break

    return redo_travel, resume_idx, stroke_dict


# RULE # 13
# 上下多角的直線圓頭，正規化為「標準」圓頭。
# PS: 因為 array size change, so need redo.
def travel_nodes_for_rule_13(stroke_dict,key,resume_idx):
    redo_travel=False

    TOO_LONG_LENGTH = 190

    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 6
    if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            if idx <= resume_idx:
                # skip traveled nodes.
                continue

            is_match_pattern = False

            #print(idx,"debug code5:",stroke_dict[key]['code'][idx])
            # 單一點的圓頭轉方頭。(向上/向下頭)
            # ? l c c c l
            #if idx==18:
            if False:
                for t_idx in range(6):
                    print(t_idx, "x,y,t_idx:",stroke_dict[key]['x'][(idx+t_idx)%nodes_length],stroke_dict[key]['y'][(idx+t_idx)%nodes_length],stroke_dict[key]['t'][(idx+t_idx)%nodes_length])
                    print(t_idx, "code:",stroke_dict[key]['code'][(idx+t_idx)%nodes_length])

            if stroke_dict[key]['t'][(idx+1)%nodes_length] != 'c':
                if stroke_dict[key]['t'][(idx+2)%nodes_length] == 'c':
                    if stroke_dict[key]['t'][(idx+3)%nodes_length] == 'c' :
                        if stroke_dict[key]['t'][(idx+4)%nodes_length] == 'c' :
                            if stroke_dict[key]['t'][(idx+5)%nodes_length] != 'c':
                              is_match_pattern = True

            if is_match_pattern:
                if(abs(stroke_dict[key]['x'][(idx+5)%nodes_length]-stroke_dict[key]['x'][(idx+0)%nodes_length]) > TOO_LONG_LENGTH):
                    is_match_pattern = False

            if is_match_pattern:
                # sould not happen in same y axis.
                x_array = []
                y_array = []
                for t_idx in range(rule_need_lines):
                    y_array.append(stroke_dict[key]['y'][(idx+t_idx) % nodes_length])
                    x_array.append(stroke_dict[key]['x'][(idx+t_idx) % nodes_length])
                direction_flag = is_same_direction_list(y_array,deviation=10)
                if direction_flag:
                    is_match_pattern=False

            if is_match_pattern:
                #print(idx,"match lcccl:",stroke_dict[key]['code'][idx])
                is_match_pattern=False
                if stroke_dict[key]['x'][idx+0] == stroke_dict[key]['x'][(idx+1)%nodes_length]:
                    if ' ' + str(stroke_dict[key]['x'][idx+0]) + ' ' in stroke_dict[key]['code'][(idx+2)%nodes_length]:
                        if stroke_dict[key]['x'][(idx+4)%nodes_length] == stroke_dict[key]['x'][(idx+5)%nodes_length]:
                            is_match_pattern=True

            if is_match_pattern:
                # must 'U' shape only.
                if stroke_dict[key]['y'][(idx+1)%nodes_length] > stroke_dict[key]['y'][(idx+3)%nodes_length]:
                    if stroke_dict[key]['y'][(idx+1)%nodes_length] < stroke_dict[key]['y'][(idx+2)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+1)%nodes_length] < stroke_dict[key]['y'][(idx+4)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+5)%nodes_length] <= stroke_dict[key]['y'][(idx+3)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+5)%nodes_length] <= stroke_dict[key]['y'][(idx+2)%nodes_length]:
                        is_match_pattern = False

                if stroke_dict[key]['y'][(idx+1)%nodes_length] < stroke_dict[key]['y'][(idx+3)%nodes_length]:
                    if stroke_dict[key]['y'][(idx+1)%nodes_length] > stroke_dict[key]['y'][(idx+2)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+1)%nodes_length] > stroke_dict[key]['y'][(idx+4)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+5)%nodes_length] >= stroke_dict[key]['y'][(idx+3)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+5)%nodes_length] >= stroke_dict[key]['y'][(idx+2)%nodes_length]:
                        is_match_pattern = False

            # from left to right
            direction = +1
            if stroke_dict[key]['x'][idx+0] < stroke_dict[key]['x'][(idx+4)%nodes_length]:
                # from right to left
                direction = -1

            if is_match_pattern:
                #print("match rule #13")
                #print(idx,"code:",stroke_dict[key]['code'][idx])

                new_x = stroke_dict[key]['x'][(idx+1)%nodes_length]
                new_y = stroke_dict[key]['y'][(idx+1)%nodes_length]
                old_code_array = stroke_dict[key]['code'][(idx+2)%nodes_length].split(' ')
                old_code_array[1] = str(new_x)
                old_code_array[2] = str(new_y-(66*direction))
                old_code_array[3] = str(new_x)
                old_code_array[4] = str(new_y-(66*direction))
                old_code_array[5] = str(new_x-(66*direction))
                old_code_array[6] = str(new_y-(66*direction))
                stroke_dict[key]['code'][(idx+2)%nodes_length] = ' '.join(old_code_array)
                stroke_dict[key]['x'][(idx+2)%nodes_length] = new_x-(66*direction)
                stroke_dict[key]['y'][(idx+2)%nodes_length] = new_y-(66*direction)


                old_code_array = stroke_dict[key]['code'][(idx+4)%nodes_length].split(' ')
                old_code_array[2] = str(new_y-(66*direction))
                old_code_array[4] = str(new_y-(66*direction))
                stroke_dict[key]['code'][(idx+4)%nodes_length] = ' '.join(old_code_array)

                del stroke_dict[key]['code'][(idx+3)%nodes_length]
                del stroke_dict[key]['x'][(idx+3)%nodes_length]
                del stroke_dict[key]['y'][(idx+3)%nodes_length]
                del stroke_dict[key]['t'][(idx+3)%nodes_length]

                redo_travel=True
                resume_idx = idx+1
                break

    return redo_travel, resume_idx, stroke_dict

# RULE # 14
# 多角的橫線圓頭，正規化為「標準」圓頭。
# PS: 因為 array size change, so need redo.
def travel_nodes_for_rule_14(stroke_dict,key,resume_idx):
    redo_travel=False

    TOO_LONG_LENGTH = 190

    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 7
    if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            if idx <= resume_idx:
                # skip traveled nodes.
                continue

            is_match_pattern = False

            #print(idx,"debug code14:",stroke_dict[key]['code'][idx])
            # 單一點的圓頭轉方頭。(向上/向下頭)
            # ? l c c c c l
            #if idx==18:

            if stroke_dict[key]['t'][(idx+1)%nodes_length] != 'c':
                if stroke_dict[key]['t'][(idx+2)%nodes_length] == 'c':
                    if stroke_dict[key]['t'][(idx+3)%nodes_length] == 'c' :
                        if stroke_dict[key]['t'][(idx+4)%nodes_length] == 'c' :
                            if stroke_dict[key]['t'][(idx+5)%nodes_length] == 'c' :
                                if stroke_dict[key]['t'][(idx+6)%nodes_length] != 'c':
                                  is_match_pattern = True

            if is_match_pattern:
                #print(idx,"debug code14:",stroke_dict[key]['code'][idx])
                if False:
                    for t_idx in range(7):
                        print(t_idx, "x,y,t_idx:",stroke_dict[key]['x'][(idx+t_idx)%nodes_length],stroke_dict[key]['y'][(idx+t_idx)%nodes_length],stroke_dict[key]['t'][(idx+t_idx)%nodes_length])
                        print(t_idx, "code:",stroke_dict[key]['code'][(idx+t_idx)%nodes_length])
                
                if(abs(stroke_dict[key]['x'][(idx+6)%nodes_length]-stroke_dict[key]['x'][(idx+0)%nodes_length]) > TOO_LONG_LENGTH):
                    is_match_pattern = False

            if is_match_pattern:
                # sould not happen in same y axis.
                x_array = []
                y_array = []
                for t_idx in range(rule_need_lines):
                    y_array.append(stroke_dict[key]['y'][(idx+t_idx) % nodes_length])
                    x_array.append(stroke_dict[key]['x'][(idx+t_idx) % nodes_length])
                direction_flag = is_same_direction_list(y_array,deviation=10)
                if direction_flag:
                    is_match_pattern=False

            if is_match_pattern:
                #print(idx,"match lcccl:",stroke_dict[key]['code'][idx])
                is_match_pattern=False
                if stroke_dict[key]['x'][idx+0] == stroke_dict[key]['x'][(idx+1)%nodes_length]:
                    if ' ' + str(stroke_dict[key]['x'][idx+0]) + ' ' in stroke_dict[key]['code'][(idx+2)%nodes_length]:
                        if stroke_dict[key]['x'][(idx+5)%nodes_length] == stroke_dict[key]['x'][(idx+6)%nodes_length]:
                            is_match_pattern=True

            if is_match_pattern:
                # must 'U' shape only.
                if stroke_dict[key]['y'][(idx+1)%nodes_length] > stroke_dict[key]['y'][(idx+3)%nodes_length]:
                    if stroke_dict[key]['y'][(idx+1)%nodes_length] < stroke_dict[key]['y'][(idx+2)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+1)%nodes_length] < stroke_dict[key]['y'][(idx+4)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+6)%nodes_length] <= stroke_dict[key]['y'][(idx+3)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+6)%nodes_length] <= stroke_dict[key]['y'][(idx+2)%nodes_length]:
                        is_match_pattern = False

                if stroke_dict[key]['y'][(idx+1)%nodes_length] < stroke_dict[key]['y'][(idx+3)%nodes_length]:
                    if stroke_dict[key]['y'][(idx+1)%nodes_length] > stroke_dict[key]['y'][(idx+2)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+1)%nodes_length] > stroke_dict[key]['y'][(idx+4)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+6)%nodes_length] >= stroke_dict[key]['y'][(idx+3)%nodes_length]:
                        is_match_pattern = False
                    if stroke_dict[key]['y'][(idx+6)%nodes_length] >= stroke_dict[key]['y'][(idx+2)%nodes_length]:
                        is_match_pattern = False


            # from left to right
            direction = +1
            if stroke_dict[key]['x'][idx+0] < stroke_dict[key]['x'][(idx+4)%nodes_length]:
                # from right to left
                direction = -1

            if is_match_pattern:
                #print("match rule #14")
                #print(idx,"code:",stroke_dict[key]['code'][idx])

                new_x = stroke_dict[key]['x'][(idx+1)%nodes_length]
                new_y = stroke_dict[key]['y'][(idx+1)%nodes_length]
                old_code_array = stroke_dict[key]['code'][(idx+2)%nodes_length].split(' ')
                old_code_array[1] = str(new_x)
                old_code_array[2] = str(new_y-(66*direction))
                old_code_array[3] = str(new_x)
                old_code_array[4] = str(new_y-(66*direction))
                old_code_array[5] = str(new_x-(66*direction))
                old_code_array[6] = str(new_y-(66*direction))
                stroke_dict[key]['code'][(idx+2)%nodes_length] = ' '.join(old_code_array)
                stroke_dict[key]['x'][(idx+2)%nodes_length] = new_x-(66*direction)
                stroke_dict[key]['y'][(idx+2)%nodes_length] = new_y-(66*direction)

                old_code_array = stroke_dict[key]['code'][(idx+5)%nodes_length].split(' ')
                old_code_array[2] = str(new_y-(66*direction))
                old_code_array[4] = str(new_y-(66*direction))
                stroke_dict[key]['code'][(idx+5)%nodes_length] = ' '.join(old_code_array)

                del stroke_dict[key]['code'][(idx+3)%nodes_length]
                del stroke_dict[key]['x'][(idx+3)%nodes_length]
                del stroke_dict[key]['y'][(idx+3)%nodes_length]
                del stroke_dict[key]['t'][(idx+3)%nodes_length]

                del stroke_dict[key]['code'][(idx+3)%nodes_length]
                del stroke_dict[key]['x'][(idx+3)%nodes_length]
                del stroke_dict[key]['y'][(idx+3)%nodes_length]
                del stroke_dict[key]['t'][(idx+3)%nodes_length]

                redo_travel=True
                resume_idx = idx+1
                break

    return redo_travel, resume_idx, stroke_dict

# RULE # 15
# 多角在橫線上的圓頭，正規化為「標準」圓頭。(通常會遇到啟始點)
# PS: 啟始點，可能不在預期(perfect)的位置上！
# PS: 因為 array size change, so need redo.
def travel_nodes_for_rule_15(stroke_dict,key,resume_idx):
    redo_travel=False

    TOO_LONG_LENGTH = 190

    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 6
    if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            if idx <= resume_idx:
                # skip traveled nodes.
                continue

            is_match_pattern = False

            #print(idx,"debug code5:",stroke_dict[key]['code'][idx])
            # ? c m c c l
            #if idx==18:
            if stroke_dict[key]['t'][(idx+1)%nodes_length] == 'c':
                if stroke_dict[key]['t'][(idx+2)%nodes_length] != 'c':
                    if stroke_dict[key]['t'][(idx+3)%nodes_length] == 'c' :
                        if stroke_dict[key]['t'][(idx+4)%nodes_length] == 'c' :
                            if stroke_dict[key]['t'][(idx+5)%nodes_length] != 'c':
                                is_match_pattern = True

            if is_match_pattern:
                #print("travel_nodes_for_rule_15:",idx)
                if(abs(stroke_dict[key]['y'][(idx+5)%nodes_length]-stroke_dict[key]['y'][(idx+0)%nodes_length]) > TOO_LONG_LENGTH):
                    is_match_pattern = False

                # 距離太遠的異常資料                    
                for t_idx in range(rule_need_lines-1):
                    if(abs(stroke_dict[key]['y'][(t_idx+1)%nodes_length]-stroke_dict[key]['y'][(t_idx+0)%nodes_length]) > TOO_LONG_LENGTH):
                        is_match_pattern = False

            if is_match_pattern:
                # sould not happen in same x axis.
                x_array = []
                y_array = []
                for t_idx in range(rule_need_lines):
                    y_array.append(stroke_dict[key]['y'][(idx+t_idx) % nodes_length])
                    x_array.append(stroke_dict[key]['x'][(idx+t_idx) % nodes_length])
                direction_flag = is_same_direction_list(x_array,deviation=10)
                if direction_flag:
                    is_match_pattern=False

            if is_match_pattern:
                #print(idx,"match ?lccl:",stroke_dict[key]['code'][idx])
                is_match_pattern=False
                if ' ' + str(stroke_dict[key]['y'][idx+0]) + ' ' in stroke_dict[key]['code'][(idx+1)%nodes_length]:
                    if stroke_dict[key]['y'][(idx+4)%nodes_length] == stroke_dict[key]['y'][(idx+5)%nodes_length]:
                        if stroke_dict[key]['x'][(idx+1)%nodes_length] == stroke_dict[key]['x'][(idx+2)%nodes_length]:
                            if stroke_dict[key]['y'][(idx+1)%nodes_length] == stroke_dict[key]['y'][(idx+2)%nodes_length]:
                                is_match_pattern=True

            # from left to right
            direction = +1
            if stroke_dict[key]['y'][idx+0] < stroke_dict[key]['y'][(idx+4)%nodes_length]:
                # from right to left
                direction = -1

            if is_match_pattern:
                #print("match rule #15")
                #print(idx,"code:",stroke_dict[key]['code'][idx])

                if False:
                    for t_idx in range(6):
                        print(t_idx, "x,y,t_idx:",stroke_dict[key]['x'][(idx+t_idx)%nodes_length],stroke_dict[key]['y'][(idx+t_idx)%nodes_length],stroke_dict[key]['t'][(idx+t_idx)%nodes_length])
                        print(t_idx, "code:",stroke_dict[key]['code'][(idx+t_idx)%nodes_length])

                #print('before:', stroke_dict[key])

                perfect_x = stroke_dict[key]['x'][(idx+0)%nodes_length] + (66 * direction)
                perfect_y = stroke_dict[key]['y'][(idx+0)%nodes_length] - (66 * direction)

                # make c on perfect coordinate.
                old_code_array = stroke_dict[key]['code'][(idx+1)%nodes_length].split(' ')
                old_code_array[1] = str(perfect_x)
                old_code_array[3] = str(perfect_x)
                old_code_array[5] = str(perfect_x)
                old_code_array[6] = str(perfect_y)
                new_code = ' '.join(old_code_array)
                #print('new perfect new_code:', new_code)
                stroke_dict[key]['code'][(idx+1)%nodes_length] = new_code
                stroke_dict[key]['x'][(idx+1)%nodes_length] = perfect_x
                stroke_dict[key]['y'][(idx+1)%nodes_length] = perfect_y

                # make l or m on perfect coordinate.
                old_code_array = stroke_dict[key]['code'][(idx+2)%nodes_length].split(' ')
                if stroke_dict[key]['t'][(idx+2)%nodes_length]=='m':
                    old_code_array[0] = str(perfect_x)
                    old_code_array[1] = str(perfect_y)
                else:
                    old_code_array[1] = str(perfect_x)
                    old_code_array[2] = str(perfect_y)
                new_code = ' '.join(old_code_array)
                #print('m new_code:', new_code)
                stroke_dict[key]['code'][(idx+2)%nodes_length] = new_code
                stroke_dict[key]['x'][(idx+2)%nodes_length] = perfect_x
                stroke_dict[key]['y'][(idx+2)%nodes_length] = perfect_y

                new_x = stroke_dict[key]['x'][(idx+2)%nodes_length]
                new_y = stroke_dict[key]['y'][(idx+5)%nodes_length]
                old_code_array = stroke_dict[key]['code'][(idx+3)%nodes_length].split(' ')
                old_code_array[1] = str(new_x)
                old_code_array[2] = str(new_y)
                old_code_array[3] = str(new_x)
                old_code_array[4] = str(new_y)
                old_code_array[5] = str(stroke_dict[key]['x'][(idx+0)%nodes_length])
                old_code_array[6] = str(new_y)
                new_code = ' '.join(old_code_array)
                stroke_dict[key]['code'][(idx+3)%nodes_length] = new_code
                stroke_dict[key]['x'][(idx+3)%nodes_length] = stroke_dict[key]['x'][(idx+0)%nodes_length]
                stroke_dict[key]['y'][(idx+3)%nodes_length] = new_y
                #print('new_code:', new_code)

                remove_index = (idx+4)%nodes_length
                #print('remove_index:', remove_index)
                del stroke_dict[key]['code'][remove_index]
                del stroke_dict[key]['x'][remove_index]
                del stroke_dict[key]['y'][remove_index]
                del stroke_dict[key]['t'][remove_index]

                #print('after:', stroke_dict[key])
                
                redo_travel=False
                resume_idx = idx+1
                break

    return redo_travel, resume_idx, stroke_dict


def load_to_memory(filename_input):
    stroke_dict = {}
    code_array=[]
    x_array=[]
    y_array=[]
    t_array=[]
    points_array = []
    default_int = -9999

    myfile = open(filename_input, 'r')
    code_begin_string = 'SplineSet'
    code_begin_string_length = len(code_begin_string)
    code_end_string = 'EndSplineSet'
    code_end_string_length = len(code_end_string)

    is_code_flag=False

    stroke_index = 0
    for x_line in myfile:
        if not is_code_flag:
            # check begin.

            if code_begin_string == x_line[:code_begin_string_length]:
                is_code_flag = True
        else:
            if x_line[:1] != ' ':
                if stroke_index >= 1:
                    stroke_dict[stroke_index]={}
                    stroke_dict[stroke_index]['code'] = code_array
                    stroke_dict[stroke_index]['x'] = x_array
                    stroke_dict[stroke_index]['y'] = y_array
                    stroke_dict[stroke_index]['t'] = t_array
                    stroke_dict[stroke_index]['points'] = points_array
                    
                    # reset new
                    code_array = []
                    x_array = []
                    y_array = []
                    t_array = []
                    points_array = []

                stroke_index += 1

            code_array.append(x_line)

            # type
            t=''
            if ' m ' in x_line:
                t='m'
            if ' l ' in x_line:
                t='l'
            if ' c ' in x_line:
                t='c'
            t_array.append(t)

            x=default_int
            y=default_int
            if ' ' in x_line:
                x_line_array = x_line.split(' ')
                if t=='m':
                    x=int(float(x_line_array[0]))
                    y=int(float(x_line_array[1]))

                if t=='l':
                    x=int(float(x_line_array[1]))
                    y=int(float(x_line_array[2]))

                if t=='c':
                    if len(x_line_array) >=7:
                        x=int(float(x_line_array[5]))
                        y=int(float(x_line_array[6]))
            x_array.append(x)
            y_array.append(y)
            points_array.append([x,y])

            # check end
            if code_end_string == x_line[:code_end_string_length]:
                #is_code_flag = False
                break

    myfile.close()
    return stroke_dict

def trace_nodes_in_strok(stroke_dict, key):
    default_int = -9999

    margin_top=default_int
    margin_bottom=default_int
    margin_left=default_int
    margin_right=default_int
    for x in stroke_dict[key]['x']:
        if x != default_int:
            if margin_right==default_int:
                # initail assign
                margin_right=x
            else:
                # compare top
                if x > margin_right:
                    margin_right = x

            if margin_left==default_int:
                # initail assign
                margin_left=x
            else:
                # compare bottom
                if x < margin_left:
                    margin_left = x

    for y in stroke_dict[key]['y']:
        if y !=default_int:
            if margin_top==default_int:
                # initail assign
                margin_top=y
            else:
                # compare top
                if y > margin_top:
                    margin_top = y

            if margin_bottom==default_int:
                # initail assign
                margin_bottom=y
            else:
                # compare bottom
                if y < margin_bottom:
                    margin_bottom = y

    stroke_dict[key]["top"]  = margin_top
    stroke_dict[key]["bottom"] = margin_bottom
    stroke_dict[key]["lef"] = margin_left
    stroke_dict[key]["right"] = margin_right

    #print(stroke_dict[key])

    # start to travel nodes for [RULE #11]
    # 多角的橫線圓頭，正規化為「標準」圓頭。
    idx=-1
    redo_travel=True
    #redo_travel=False
    while redo_travel:
        redo_travel,idx,stroke_dict=travel_nodes_for_rule_11(stroke_dict,key,idx)

    # start to travel nodes for [RULE #12]
    # 多角的橫線圓頭，正規化為「標準」圓頭。
    idx=-1
    redo_travel=True
    #redo_travel=False
    while redo_travel:
        redo_travel,idx,stroke_dict=travel_nodes_for_rule_12(stroke_dict,key,idx)

    # start to travel nodes for [RULE #13]
    # 上下的多角的圓頭，正規化為「標準」圓頭。
    idx=-1
    redo_travel=True
    #redo_travel=False
    while redo_travel:
        redo_travel,idx,stroke_dict=travel_nodes_for_rule_13(stroke_dict,key,idx)

    # start to travel nodes for [RULE #14]
    # 上下的多角的圓頭，正規化為「標準」圓頭。
    idx=-1
    redo_travel=True
    #redo_travel=False
    while redo_travel:
        redo_travel,idx,stroke_dict=travel_nodes_for_rule_14(stroke_dict,key,idx)

    # start to travel nodes for [RULE #15]
    # 多角的橫線圓頭，正規化為「標準」圓頭。(通常會遇到啟始點)
    idx=-1
    redo_travel=True
    #redo_travel=False
    while redo_travel:
        redo_travel,idx,stroke_dict=travel_nodes_for_rule_15(stroke_dict,key,idx)

    # start to travel nodes for [RULE #1] 
    # PS: 目前停用此做法，與其他 rule 合併了。
    # PS: 已停用。
    idx=0
    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 5
    #if nodes_length >= rule_need_lines:
    if False:
        for idx in range(nodes_length):
            is_match_pattern = False

            # 右邊橫線
            if stroke_dict[key]['y'][idx] == stroke_dict[key]['y'][(idx+1)%nodes_length]:
                if stroke_dict[key]['t'][(idx+1)%nodes_length] != 'c':
                    if stroke_dict[key]['t'][(idx+2)%nodes_length] == 'c':
                        if stroke_dict[key]['t'][(idx+3)%nodes_length] == 'c':
                            if stroke_dict[key]['t'][(idx+4)%nodes_length] != 'c':
                                if stroke_dict[key]['y'][(idx+3)%nodes_length] == stroke_dict[key]['y'][(idx+4)%nodes_length]:
                                    #if stroke_dict[key]['y'][idx] != stroke_dict[key]['y'][idx+4]:
                                    direction=-1
                                    if stroke_dict[key]['y'][idx] > stroke_dict[key]['y'][(idx+4)%nodes_length]:
                                        direction=+1
                                    # match rule 1
                                    #print("match rule #1")
                                    #print(idx,"code:",stroke_dict[key]['code'][idx])
                                    
                                    '''
                                    #print(idx,"code before:",stroke_dict[key]['code'])
                                    new_x1 = stroke_dict[key]['x'][(idx+2)%nodes_length] - (32 * direction)
                                    new_x2 = new_x1
                                    new_x3 = stroke_dict[key]['x'][(idx+2)%nodes_length]
                                    new_y1 = stroke_dict[key]['y'][(idx+1)%nodes_length]
                                    new_y2 = new_y1
                                    new_y3 = stroke_dict[key]['y'][(idx+2)%nodes_length] + (58 * direction)
                                    new_code = ' %d %d %d %d %d %d c 1\n' % (new_x1,new_y1,new_x2,new_y2,new_x3,new_y3)
                                    stroke_dict[key]['code'].insert((idx+2)%nodes_length,new_code)
                                    stroke_dict[key]['x'].insert((idx+2)%nodes_length,new_x3)
                                    stroke_dict[key]['y'].insert((idx+2)%nodes_length,new_y3)
                                    stroke_dict[key]['t'].insert((idx+2)%nodes_length,'c')
                                    #print(idx,"code after:",stroke_dict[key]['code'])
                                    '''

                                    break

    # start to travel nodes for [RULE #2]
    # PS: 這個解法，應該可以透過 travel nodes 來解決。
    # PS: 直處理「啟始點」
    # PS: 已停用。
    idx=0
    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 5
    #if nodes_length >= rule_need_lines:
    if False:
        idx = 0

        is_match_pattern = False
        
        # 啟始點在左下角解法
        if stroke_dict[key]['t'][idx+1] == 'c':
            if stroke_dict[key]['t'][(idx+2)%nodes_length] == 'c':
                if stroke_dict[key]['t'][-1] == 'c':
                    if stroke_dict[key]['t'][-2] == 'l':
                        is_match_pattern = True

        if is_match_pattern:
            is_match_pattern=False
            if stroke_dict[key]['y'][-2] == stroke_dict[key]['y'][-3]:
                if ' ' + str(stroke_dict[key]['y'][-2]) + ' ' in stroke_dict[key]['code'][-1]:
                    if stroke_dict[key]['y'][idx] == stroke_dict[key]['y'][-1]:
                        #if stroke_dict[key]['y'][idx] != stroke_dict[key]['y'][idx+4]:
                        if stroke_dict[key]['y'][-1] > stroke_dict[key]['y'][-2]:
                            is_match_pattern = True

        if is_match_pattern:
            # match rule 2
            #print("match rule #2")
            #print(idx,"code:",stroke_dict[key]['code'][idx])
            new_x = stroke_dict[key]['x'][idx+1]
            new_y = int((stroke_dict[key]['y'][1] + stroke_dict[key]['y'][-2]) / 2) - 66
            new_code = "%d %d m " % (new_x,new_y) + field_right(stroke_dict[key]['code'][idx], " m ")
            stroke_dict[key]['code'][idx] = new_code
            stroke_dict[key]['x'][idx] = new_x
            stroke_dict[key]['y'][idx] = new_y
            stroke_dict[key]['t'][idx] = 'm'

            old_code_array = stroke_dict[key]['code'][-1].split(' ')
            old_code_array[5] = str(new_x)
            old_code_array[6] = str(new_y)
            stroke_dict[key]['code'][-1] = ' '.join(old_code_array)
                                

    # start to travel nodes for [RULE #3]
    # PS: 目前沒有在使用了。
    idx=0
    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 5
    if False:
    #if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            is_match_pattern = False

            # 橫線右頭，要向下
            if stroke_dict[key]['t'][(idx+1)%nodes_length] == 'c':
                if stroke_dict[key]['t'][(idx+2)%nodes_length] != 'c':
                    if stroke_dict[key]['t'][(idx+nodes_length-1)%nodes_length] == 'c':
                        if stroke_dict[key]['t'][(idx+nodes_length-2)%nodes_length] == 'l':
                            is_match_pattern=True

            if is_match_pattern:
                is_match_pattern=False
                if stroke_dict[key]['y'][(idx+nodes_length-3)%nodes_length] == stroke_dict[key]['y'][(idx+nodes_length-3)%nodes_length]:
                    if ' ' + str(stroke_dict[key]['y'][(idx+nodes_length-2)%nodes_length]) + ' ' in stroke_dict[key]['code'][(idx+nodes_length-1)%nodes_length]:
                        if stroke_dict[key]['y'][idx] == stroke_dict[key]['y'][(idx+nodes_length-1)%nodes_length]:
                            #if stroke_dict[key]['y'][idx] != stroke_dict[key]['y'][idx+4]:
                            if stroke_dict[key]['y'][(idx+nodes_length-1)%nodes_length] > stroke_dict[key]['y'][(idx+nodes_length-1)%nodes_length]:
                                if stroke_dict[key]['y'][(idx+1)%nodes_length] == stroke_dict[key]['y'][(idx+2)%nodes_length]:
                                    is_match_pattern=True

            if is_match_pattern:
                # match rule 3
                #print("match rule #3")
                #print(idx,"code:",stroke_dict[key]['code'][idx])
                #print(idx,"code before:",stroke_dict[key]['code'])

                new_x1 = stroke_dict[key]['x'][idx]+32
                new_x2 = new_x1
                new_x3 = new_x1 - 32
                new_y1 = stroke_dict[key]['y'][(idx+nodes_length-2)%nodes_length]
                new_y2 = new_y1
                new_y3 = new_y1-32
                new_code = ' %d %d %d %d %d %d c 1\n' % (new_x1,new_y1,new_x2,new_y2,new_x3,new_y3)
                stroke_dict[key]['code'].insert((idx+nodes_length-1)%nodes_length,new_code)
                stroke_dict[key]['x'].insert((idx+nodes_length-1)%nodes_length,new_x3)
                stroke_dict[key]['y'].insert((idx+nodes_length-1)%nodes_length,new_y3)
                stroke_dict[key]['t'].insert((idx+nodes_length-1)%nodes_length,'c')
                #print(idx,"code after:",stroke_dict[key]['code'])


    # start to travel nodes for [RULE #4]
    # PS: 已停用。
    idx=0
    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 5
    #if nodes_length >= rule_need_lines:
    if False:
        for idx in range(nodes_length):
            is_match_pattern = False
            # 一般橫線，或勾，但左下角有3點
            if stroke_dict[key]['t'][idx+0] != 'c':
                if stroke_dict[key]['t'][(idx+1)%nodes_length] == 'c':
                    if stroke_dict[key]['t'][(idx+2)%nodes_length] == 'c':
                        if stroke_dict[key]['t'][(idx+3)%nodes_length] == 'c':
                            if stroke_dict[key]['t'][(idx+4)%nodes_length] != 'c':
                                is_match_pattern = True

            if is_match_pattern:
                is_match_pattern=False
                if ' ' + str(stroke_dict[key]['y'][idx]) + ' ' in stroke_dict[key]['code'][(idx+1)%nodes_length]:
                    if stroke_dict[key]['y'][(idx+3)%nodes_length] == stroke_dict[key]['y'][(idx+4)%nodes_length]:
                        if stroke_dict[key]['y'][idx] < stroke_dict[key]['y'][(idx+4)%nodes_length]:
                            is_match_pattern = True
                            #print("match rule #4")
                            #print(idx,"code:",stroke_dict[key]['code'][idx])

            if is_match_pattern:
                new_x = stroke_dict[key]['x'][(idx+2)%nodes_length]
                new_y = int((stroke_dict[key]['y'][idx+0] + stroke_dict[key]['y'][(idx+2)%nodes_length]) / 2) - 66
                
                old_code_array = stroke_dict[key]['code'][(idx+1)%nodes_length].split(' ')
                old_code_array[5] = str(new_x)
                old_code_array[6] = str(new_y)
                stroke_dict[key]['code'][(idx+1)%nodes_length] = ' '.join(old_code_array)
                break

    # start to travel nodes for [RULE #6]
    idx=0
    nodes_length = len(stroke_dict[key]['code'])
    rule_need_lines = 6
    if nodes_length >= rule_need_lines:
        for idx in range(nodes_length):
            is_match_pattern = False

            # 2點的圓頭轉方頭
            if stroke_dict[key]['t'][idx+0] != 'c':
                if stroke_dict[key]['t'][(idx+1)%nodes_length] != 'c':
                    if stroke_dict[key]['t'][(idx+2)%nodes_length] == 'c':
                        if stroke_dict[key]['t'][(idx+3)%nodes_length] == 'c':
                            if stroke_dict[key]['t'][(idx+4)%nodes_length] == 'c':
                                if stroke_dict[key]['t'][(idx+5)%nodes_length] != 'c':
                                    is_match_pattern=True

            if is_match_pattern:
                is_match_pattern=False
                if stroke_dict[key]['x'][idx+0] == stroke_dict[key]['x'][(idx+1)%nodes_length]:
                    if ' ' + str(stroke_dict[key]['x'][idx+0]) + ' ' in stroke_dict[key]['code'][(idx+2)%nodes_length]:
                        if stroke_dict[key]['x'][(idx+5)%nodes_length] == stroke_dict[key]['x'][(idx+4)%nodes_length]:
                            if ' ' + str(stroke_dict[key]['y'][(idx+3)%nodes_length]) + ' ' in stroke_dict[key]['code'][(idx+4)%nodes_length]:
                                if stroke_dict[key]['x'][(idx+2)%nodes_length] >= stroke_dict[key]['x'][(idx+1)%nodes_length] and stroke_dict[key]['y'][(idx+2)%nodes_length] >= stroke_dict[key]['y'][(idx+1)%nodes_length]:
                                    if stroke_dict[key]['x'][(idx+2)%nodes_length] <= stroke_dict[key]['x'][(idx+3)%nodes_length] and stroke_dict[key]['y'][(idx+2)%nodes_length] <= stroke_dict[key]['y'][(idx+3)%nodes_length]:
                                        is_match_pattern=True
                                        #print("match rule #6")
                                        #print(idx,"code:",stroke_dict[key]['code'][idx])
            if is_match_pattern:
                new_x2 = stroke_dict[key]['x'][idx+0]
                new_y2 = stroke_dict[key]['y'][(idx+3)%nodes_length]

                old_code_array = stroke_dict[key]['code'][(idx+2)%nodes_length].split(' ')
                old_code_array[1] = str(new_x2)
                old_code_array[2] = str(new_y2)
                old_code_array[3] = str(new_x2)
                old_code_array[4] = str(new_y2)
                old_code_array[5] = str(new_x2+16)
                old_code_array[6] = str(new_y2)
                stroke_dict[key]['code'][(idx+2)%nodes_length] = ' '.join(old_code_array)
                stroke_dict[key]['x'][(idx+2)%nodes_length]=new_x2+16
                stroke_dict[key]['x'][(idx+2)%nodes_length]=new_y2

                new_x = stroke_dict[key]['x'][(idx+4)%nodes_length]-16
                new_y = stroke_dict[key]['y'][(idx+3)%nodes_length]
                new_code = " %d %d l 2\n" % (new_x, new_y)

                stroke_dict[key]['code'][(idx+3)%nodes_length] = new_code
                stroke_dict[key]['x'][(idx+3)%nodes_length] = new_x
                stroke_dict[key]['y'][(idx+3)%nodes_length] = new_y
                stroke_dict[key]['t'][(idx+3)%nodes_length] = 'l'
                
                #break

    # start to travel nodes for [RULE #8]
    # 右邊橫線，啟始點在右邊的中間點上。
    idx=-1
    redo_travel=True
    #redo_travel=False
    while redo_travel:
        redo_travel,idx,stroke_dict=travel_nodes_for_rule_8(stroke_dict,key,idx)

    # start to travel nodes for [RULE #9]
    # 橫線右頭，要向下
    idx=-1
    redo_travel=True
    #redo_travel=False
    while redo_travel:
        redo_travel,idx,stroke_dict=travel_nodes_for_rule_9(stroke_dict,key,idx)


    # start to travel nodes for [RULE #10]
    # 斜線的圓頭改方頭。
    # PS: 「必需」先做，因為影響層面很廣！
    #stroke_dict=travel_nodes_for_rule_10(stroke_dict,key,idx)



    # start to travel nodes for [RULE #5]
    # 向下的圓頭轉方頭。
    # PS: 這個要最後執行，不然會因此長角。
    idx=-1
    redo_travel=True
    while redo_travel:
        redo_travel,idx,stroke_dict=travel_nodes_for_rule_5(stroke_dict,key,idx)


def convet_font(filename_input,readonly):
    ret = False
    stroke_dict = {}
    stroke_dict = load_to_memory(filename_input)
    #print(stroke_dict)
    for key in stroke_dict.keys():
        #print("key:", key, 'code:', stroke_dict[key]['code'][0])
        # for debug
        #if key==2:
        if True:
            clockwise = check_clockwise(stroke_dict[key]['points'])
            if clockwise:
                trace_nodes_in_strok(stroke_dict, key)
    
    write_to_file(filename_input,stroke_dict,readonly)

    return ret

readonly = True     #debug
readonly = False    #online

idx=0
convert_count=0
for name in glob.glob('./*.glyph'):
    idx+=1
    #print(name)

    if name != './uni9AD4.glyph':
        pass
        #continue

    is_convert = False
    is_convert = convet_font(name,readonly)
    if is_convert:
        convert_count+=1
        #print("convert list:", name)
    #break

print("Finish!\ncheck file count:%d\n" % (idx))

'''
for key in headitem_dict.keys():
    filename_output = "chars/info_%d.txt" % (key)
    if os.path.exists(filename_output):
        is_trash = is_trash_file(filename_output)
        if is_trash:
            print("trash list:", filename_output)
            if not readonly:
                os.remove(filename_output)
'''