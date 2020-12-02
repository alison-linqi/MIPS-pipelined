# On my honor, I have neither given nor received unauthorized aid on this assignment.
# Author: Lin Qi
import math
import sys
from queue import Queue
import linecache
# Initializing all queues
import numpy as np
import os

memory = dict()
reg = np.zeros(32, dtype=int)

opdict = dict(
    ADD="110000",
    SUB="110001",
    MUL="110010",
    AND="110011",
    OR="110100",
    XOR="110101",
    NOR="110110",
    SLT="110111",
    ADDI="111000",
    ANDI="111001",
    ORI="111010",
    XORI="111011",
    J="010000",
    JR="010001",
    BEQ="010010",
    BLTZ="010011",
    BGTZ="010100",
    BREAK="010101",
    SW="010110",
    LW="010111",
    SLL="011000",
    SRL="011001",
    SRA="011010",
    NOP="011011")

preissue_que = Queue(maxsize=4)
pre_alu1_que = Queue(maxsize=2)
pre_alu2_que = Queue(maxsize=2)
pre_mem_que = Queue(maxsize=1)
post_alu2_que = Queue(maxsize=1)
post_mem_que = Queue(maxsize=1)
PC = 252
Cycle = 1
brch_stl_flag = False

branch_set = {"BEQ", "BLTZ", "BGTZ", "J", "JR"}
bgltzset = {'BLTZ', 'BGTZ'}
regset = {'ADD', 'SUB', 'MUL', 'AND', 'OR', 'XOR', 'SLT', 'NOR'}
immeset = {'ADDI', 'ANDI', 'ORI', 'XORI'}
slw_set = {'SW', 'LW'}
trisset = {'SLL', 'SRL', 'SRA'}
alu2_set = {'ADD', 'SUB', 'MUL', 'AND', 'OR', 'XOR',
            'SLT', 'NOR', 'ADDI', 'ANDI', 'ORI', 'XORI',
            'SLL', 'SRL', 'SRA'}

Scoreboard_dict = dict()

def convert_list_to_string(org_list, seperator=''):
    return seperator.join(org_list)

def convert_list_to_string2(org_list, seperator=' '):
    return seperator.join(org_list)

def searchkey(binary_code):
    for i in opdict.keys():
        if binary_code == opdict.get(i):
            return i
    return "data"


def addi(s):
    global reg
    rt, rs, imme = getimme(s)
    # reg[int(rt)] = reg[int(rs)] + int(imme)
    rlt = reg[int(rs)] + int(imme)
    # return destination reg id and result
    return rt, rlt


def add(s):
    global reg
    rd, rs, rt = getreg(s)
    # reg[int(rd)] = reg[int(rt)] + reg[int(rs)]
    rlt = reg[int(rt)] + reg[int(rs)]
    return rd, rlt


def sub(s):
    global reg
    rd, rs, rt = getreg(s)
    # reg[int(rd)] = reg[int(rs)] - reg[int(rt)]
    rlt = reg[int(rs)] - reg[int(rt)]
    return rd, rlt


def mul(s):
    global reg
    rd, rs, rt = getreg(s)
    # reg[int(rd)] = reg[int(rs)] * reg[int(rt)]
    rlt = reg[int(rs)] * reg[int(rt)]
    return rd, rlt


def func_and(s):
    global reg
    rd, rs, rt = getreg(s)
    # reg[int(rd)] = reg[int(rs)] & reg[int(rt)]
    rlt = reg[int(rs)] & reg[int(rt)]
    return rd, rlt


def func_or(s):
    global reg
    rd, rs, rt = getreg(s)
    # reg[int(rd)] = reg[int(rs)] | reg[int(rt)]
    rlt = reg[int(rs)] | reg[int(rt)]
    return rd, rlt


def xor(s):
    global reg
    rd, rs, rt = getreg(s)
    # reg[int(rd)] = reg[int(rs)] ^ reg[int(rt)]
    rlt = reg[int(rs)] ^ reg[int(rt)]
    return rd, rlt


def nor(s):
    global reg
    rd, rs, rt = getreg(s)
    # reg[int(rd)] = -(reg[int(rs)] | reg[int(rt)])
    rlt = -(reg[int(rs)] | reg[int(rt)])
    return rd, rlt


def slt(s):
    global reg
    rd, rs, rt = getreg(s)
    if (reg[int(rs)] < reg[int(rt)]):
        # reg[int(rd)] = 1
        return rd, 1
    else:
        # reg[int(rd)] = 0
        return rd, 0


# 16 bit immediate is zero-extended to the left
def andi(s):
    global reg
    rt, rs, imme = getimme(s)
    imme = int(s[16:32], 2)
    # reg[int(rt)] = reg[int(rs)] & int(imme)
    rlt = reg[int(rs)] & int(imme)
    return rt, rlt


def get_bin(x, n=0):
    return format(x, 'b').zfill(n)


def ori(s):
    global reg
    rt, rs, imme = getimme(s)
    imme = int(s[16:32], 2)
    # reg[int(rt)] = reg[int(rs)] | int(imme)
    rlt = reg[int(rs)] | int(imme)
    return rt, rlt


def xori(s):
    global reg
    rt, rs, imme = getimme(s)
    imme = int(s[16:32], 2)
    # reg[int(rt)] = reg[int(rs)] ^ int(imme)
    rlt = reg[int(rs)] ^ int(imme)
    return rt, rlt


def sll(s):
    global reg
    rd, rt, sa = tris(s)
    # reg[int(rd)] = reg[int(rt)] << int(sa)
    rlt = reg[int(rt)] << int(sa)
    return rd, rlt


def srl(s):
    global reg
    rd, rt, sa = tris(s)
    rt_value = reg[int(rt)]
    if rt_value < 0:
        # digits = get_bin(-1 * rt_value, 0)
        bin = get_bin(-1 * rt_value, 31)
        # print(bin)

        arr_bin = np.array(list(bin))
        leng = len(arr_bin)
        for i in range(leng):
            if arr_bin[i] == '0':
                arr_bin[i] = '1'
            else:
                arr_bin[i] = '0'
        re = convert_list_to_string(arr_bin)
        # print(leng)
        # print(re)
        e = int(re, 2) + 1 + 2 ** leng
        # reg[int(rd)] = e >> int(sa)
        rlt = e >> int(sa)
        return rd, rlt
    else:
        # reg[int(rd)] = reg[int(rt)] >> int(sa)
        rlt = reg[int(rt)] >> int(sa)
        return rd, rlt


def sra(s):
    global reg
    rd, rt, sa = tris(s)
    # reg[int(rd)] = reg[int(rt)] >> int(sa)
    rlt = reg[int(rt)] >> int(sa)
    return rd, rlt


# to be continued
def bgltz(s):
    rs = int(s[6:11], 2)
    # shift left and get 18 bit signed value
    a = str(s[16: 32])
    # a = a[2: len(a) - 1]
    a = a + "00"
    offset = handledata(a)
    return str(rs), str(offset)


def beq_code(s):
    rs = int(s[6:11], 2)
    rt = int(s[11:16], 2)
    # shift left and get 18 bit signed value
    a = convert_list_to_string(s[16: 32], '')

    # a = a[2: len(a) - 1]
    a = a + "00"
    # print(a)

    offset = handledata(a)
    # print(offset)
    return str(rs), str(rt), str(offset)


def beq(s):
    global reg
    global Scoreboard_dict
    rs, rt, offset = beq_code(s)
    global PC
    stall_flg = False
    # two source regs
    sbd_regs = Scoreboard_dict.values()

    # include write, read regs in each scoreboard reg set
    for wt_rd_reg in sbd_regs:
        # compare the value of rs and wt_rd_reg[0], which is the write reg
        if wt_rd_reg[1] == rs or wt_rd_reg[1] == rt:
            stall_flg = True
            return stall_flg, -1

    if not stall_flg and reg[int(rs)] == reg[int(rt)]:
        PC = PC + 4 + int(offset)
        line = PC / 4 - 63
        return stall_flg, line, PC
    else:
        PC = PC + 4
        line = PC / 4 - 63
        return stall_flg, line, PC


def bltz(s):
    global reg
    global Scoreboard_dict
    rs, offset = bgltz(s)
    global PC
    stall_flag = False

    sbd_regs = Scoreboard_dict.values()
    # include write, read regs in each scoreboard reg set
    for wt_rd_reg in sbd_regs:
        # compare the value of rs and wt_rd_reg[0], which is the write reg
        if wt_rd_reg[1] == rs:
            stall_flg = True
            return stall_flg, -1

    if (reg[int(rs)] < 0):
        PC = PC + 4 + int(offset)
        line = PC / 4 - 63
    else:
        PC = PC + 4
        line = PC / 4 - 63
    return stall_flag, line


def bgtz(s):
    global reg
    global Scoreboard_dict
    rs, offset = bgltz(s)
    global PC
    stall_flag = False

    sbd_regs = Scoreboard_dict.values()
    # include write, read regs in each scoreboard reg set
    for wt_rd_reg in sbd_regs:
        # compare the value of rs and wt_rd_reg[0], which is the write reg
        if wt_rd_reg[1] == rs:
            stall_flg = True
            return stall_flg, -1

    if (reg[int(rs)] > 0):
        PC = PC + 4 + int(offset)
        line = PC / 4 - 63
    else:
        PC = PC + 4
        line = PC / 4 - 63
    return stall_flag, line


def jump_code(s):
    target = int(s[6:32], 2)
    target = target << 2
    return str(target)


def jr_code(s):
    rs = int(s[6:11], 2)
    return str(rs)


# immediate value
def jump(s):
    target = jump_code(s)
    target = int(target)
    global PC
    PC = target
    line = target / 4 - 63
    return line


def jr(s):
    global reg
    global PC
    global Scoreboard_dict
    stall_flg = False

    rs = jr_code(s)
    # rs, source register
    sbd_regs = Scoreboard_dict.values()
    # include write, read regs in each scoreboard reg set
    for wt_rd_reg in sbd_regs:
        # compare the value of rs and wt_rd_reg[0], which is the write reg
        if wt_rd_reg[1] == rs:
            stall_flg = True
            return stall_flg, -1
    # if not stalled, proceed
    if not stall_flg:
        target = reg[int(rs)]
        PC = target
        line = target / 4 - 63
        return stall_flg, line


def tris(s):
    rt = int(s[11:16], 2)
    rd = int(s[16:21], 2)
    sa = int(s[21:26], 2)
    return str(rd), str(rt), str(sa)


def swlw(s):
    base = int(s[6:11], 2)
    rt = int(s[11:16], 2)
    offset = str(s[16:32])
    offset = handledata(offset)
    return str(rt), str(offset), str(base)


def getreg(s):
    rs = int(s[6:11], 2)
    rt = int(s[11:16], 2)
    rd = int(s[16:21], 2)
    return str(rd), str(rs), str(rt)


def getimme(s):
    rs = int(s[6:11], 2)
    rt = int(s[11:16], 2)
    imme = str(s[16:32])
    # imme = imme[2: len(imme) - 1]
    imme = handledata(imme)
    # imme = int(s[16:32], 2)
    return str(rt), str(rs), str(imme)


# handle data
def handledata(s):
    if s[0] == "0":
        return int(s, 2)
    else:
        arr = np.array(list(s))
        for i in range(1, len(arr)):
            if arr[i] == '0':
                arr[i] = '1'
            else:
                arr[i] = '0'

        full_str = convert_list_to_string(arr[1:])
        # print(full_str)

        result = int(full_str, 2)
        # print(-1 * (result + 1))
        return -1 * (result + 1)


# IF
crt_stl_branch = list()
brk_stop_flag = False
preissue_full_brk = False
start_fetch_num = 0

def IF(input, f_simu):
    global PC
    global Cycle
    global reg
    global memory
    global preissue_que
    global brch_stl_flag
    global preissue_full_brk
    global start_fetch_num
    global crt_stl_branch
    global brk_stop_flag
    Repeat = False

    f_simu.write("IF Unit:" + "\n")
    line_num = PC / 4 - 63

    if brch_stl_flag is True and len(crt_stl_branch) != 0:
        line = crt_stl_branch.pop(0)
    else:
        line = linecache.getline(input, int(line_num))

    if start_fetch_num == 2:
        f_simu.write("\t" + "Waiting Instruction:" + "\n")
        f_simu.write("\t" + "Executed Instruction:" + "\n")

    for i in range(start_fetch_num, 2):

        if preissue_que.full():
            # print("preissue queue is full can not fetch more instrs")
            break
        if line:

            read_instr = line.strip()
            fetchcode = read_instr.split('\t')

            whole_instr = fetchcode[0]
            opcode = whole_instr[0:6]
            parsed_instr = searchkey(opcode)

            if parsed_instr == "NOP":
               pass

            elif parsed_instr != "BREAK" and parsed_instr not in branch_set:
                if Repeat is False:
                    f_simu.write("\t" + "Waiting Instruction:" + "\n")
                    f_simu.write("\t" + "Executed Instruction:" + "\n")
                    Repeat = True

            elif parsed_instr == "BREAK":
                f_simu.write("\t" + "Waiting Instruction:" + "\n")
                f_simu.write("\t" + "Executed Instruction: [BREAK]" + "\n")
                # print("break!")
                brk_stop_flag = True
                return



            elif parsed_instr in branch_set:
                if parsed_instr == "J":
                    # immediate value, not penalty
                    line_num = jump(whole_instr)
                    f_simu.write("\t" + "Waiting Instruction:" + "\n")
                    f_simu.write("\t" + "Executed Instruction: [" + fetchcode[2] + "]" + "\n")
                    break

                elif parsed_instr == "JR":
                    rlt = jr(whole_instr)
                    if rlt[0] is False:
                        line = linecache.getline(input, int(rlt[1]))
                        f_simu.write("\t" + "Waiting Instruction:" + "\n")
                        f_simu.write("\t" + "Executed Instruction: [" + fetchcode[2] + "]" + "\n")
                        if len(crt_stl_branch) != 0:
                            crt_stl_branch.clear()
                            brch_stl_flag = False
                            # scbd_put_list = line.split('\t')
                            # preissue_que.put(scbd_put_list[0])
                            break
                    else:
                        f_simu.write("\t" + "Waiting Instruction: [" + fetchcode[2] + "]" + "\n")
                        f_simu.write("\t" + "Executed Instruction:" + "\n")
                        if brch_stl_flag is False:
                            crt_stl_branch.append(read_instr)
                            brch_stl_flag = True
                        break

                elif parsed_instr == "BEQ":
                    # line_num, PC = beq(whole_instr)
                    rlt = beq(whole_instr)
                    if rlt[0] is False:
                        f_simu.write("\t" + "Waiting Instruction:" + "\n")
                        f_simu.write("\t" + "Executed Instruction: [" + fetchcode[2] + "]" + "\n")
                        line = linecache.getline(input, int(rlt[1]))

                        crt_stl_branch.clear()
                        brch_stl_flag = False
                        # scbd_put_list = line.split('\t')
                        # preissue_que.put(scbd_put_list[0])
                        break
                    elif rlt[0] is True:
                        f_simu.write("\t" + "Waiting Instruction: [" + fetchcode[2] + "]" + "\n")
                        f_simu.write("\t" + "Executed Instruction:" + "\n")
                        if brch_stl_flag is False:
                            crt_stl_branch.append(read_instr)
                            brch_stl_flag = True
                        break

                elif parsed_instr == "BLTZ":
                    rlt = bltz(whole_instr)
                    # line_num = bltz(whole_instr)
                    if rlt[0] is False:
                        f_simu.write("\t" + "Waiting Instruction:" + "\n")
                        f_simu.write("\t" + "Executed Instruction: [" + fetchcode[2] + "]" + "\n")
                        line = linecache.getline(input, int(rlt[1]))
                        if len(crt_stl_branch) != 0:
                            crt_stl_branch.clear()
                            brch_stl_flag = False
                            # scbd_put_list = line.split('\t')
                            # preissue_que.put(scbd_put_list[0])
                            break
                    else:
                        f_simu.write("\t" + "Waiting Instruction: [" + fetchcode[2] + "]" + "\n")
                        f_simu.write("\t" + "Executed Instruction:" + "\n")
                        if brch_stl_flag is False:
                            crt_stl_branch.append(read_instr)
                            brch_stl_flag = True
                        break

                elif parsed_instr == "BGTZ":
                    rlt = bgtz(whole_instr)
                    if rlt[0] is False:
                        f_simu.write("\t" + "Waiting Instruction:" + "\n")
                        f_simu.write("\t" + "Executed Instruction: [" + fetchcode[2] + "]" + "\n")
                        line = linecache.getline(input, int(rlt[1]))
                        if len(crt_stl_branch) != 0:
                            crt_stl_branch.clear()
                            brch_stl_flag = False
                            # scbd_put_list = line.split('\t')
                            # preissue_que.put(scbd_put_list[0])
                            break
                    else:
                        f_simu.write("\t" + "Waiting Instruction: [" + fetchcode[2] + "]" + "\n")
                        f_simu.write("\t" + "Executed Instruction:" + "\n")

                        if brch_stl_flag is False:
                            crt_stl_branch.append(read_instr)
                            brch_stl_flag = True
                        break

            scbd_put_list = line.split('\t')
            # preissue_que.put(scbd_put_list[0])
            if parsed_instr != "NOP":
                preissue_que.put(read_instr)
            # preissue_que.put(line)
            PC = PC + 4
            line_num = PC / 4 - 63
            line = linecache.getline(input, int(line_num))

    if preissue_que.full():
        start_fetch_num = 2
    elif preissue_que.qsize() == 3:
        start_fetch_num = 1
    else:
        start_fetch_num = 0

def find_sourcereg(instr):
    instr = instr.split('\t')
    binary_instr = instr[0]
    opcode = binary_instr[0:6]
    read_instr = searchkey(opcode)

    if read_instr in regset:
        # print("regset!")
        rd, rs, rt = getreg(binary_instr)
        return "reg", rd, rs, rt
    elif read_instr in immeset:
        rt, rs, imme = getimme(binary_instr)
        return "imme", rt, rs, imme
    elif read_instr in trisset:
        rd, rt, sa = tris(binary_instr)
        return "tris", rd, rt
    elif read_instr == "SW":
        rt, offset, base = swlw(binary_instr)
        # just 2 reads, no write to any registers
        return "SW", rt, base
    elif read_instr == "LW":
        rt, offset, base = swlw(binary_instr)
        return "LW", rt, base
    # data, return random unvalid number
    else:
        return -1, -1, -1
    # elif read_instr in bgltzset:
    #     rs, offset = bgltz(read_instr)
    # elif read_instr == "J":
    #     target = jump_code(read_instr)
    # elif read_instr == "JR":
    #     rs = jr_code(read_instr)
    # elif read_instr == "BEQ":
    #     rs, rt, offset = beq_code(read_instr)


def WAW_hazard(result, result2):
    hzd_WAW = False

    if (result[0] == "SW"):
        pass
    else:
        if (result2[0] == "SW"):
            pass
        else:
            if (result[1] == result2[1]):
                hzd_WAW = True
    return hzd_WAW


def RAW_hazard(result, result2):
    # we first check 1st write, 2nd read, RAW
    hzd_RAW = False
    read_set = set()
    # the first instr won't write
    if (result[0] == "SW"):
        return hzd_RAW
    else:
        # find 1st write
        # writereg = result[1]
        if (result2[0] == "SW"):
            for i in range(1, len(result2)):
                read_set.add(result2[i])
        else:
            for i in range(2, len(result2)):
                read_set.add(result2[i])

    if (result[1] in read_set):
        hzd_RAW = True
    return hzd_RAW


# wait to check if this is correct
def WAR_hazard(result, result2):
    hzd_WAR = False
    read_set = set()
    if (result[0] == "SW"):
        for i in range(1, len(result)):
            read_set.add(result[i])
        if result2[1] in read_set:
            hzd_WAR = True
    else:
        for i in range(2, len(result)):
            read_set.add(result[i])
        if (result2[0] == "SW"):
            pass
        else:
            if (result2[1] in read_set):
                hzd_WAR = True

    return hzd_WAR


def checkSLW(sour):
    # check if write WAW RAW
    for i2 in Scoreboard_dict.values():
        if (sour == i2[0]):
            return True
    return False


# issue hazard RAW ??
def issuehzd(instr1, instr2):
    result = find_sourcereg(instr1)
    result2 = find_sourcereg(instr2)
    return WAW_hazard(result, result2) or WAR_hazard(result, result2) or RAW_hazard(result, result2)


def scorehzd(instr1, instr2):
    result = find_sourcereg(instr1)
    result2 = find_sourcereg(instr2)
    return WAW_hazard(result, result2) or RAW_hazard(result, result2)


def ntissuehzd(instr1, instr2):
    result = find_sourcereg(instr1)
    result2 = find_sourcereg(instr2)
    return WAW_hazard(result, result2) or RAW_hazard(result, result2) or WAR_hazard(result, result2)


def Issue():
    global pre_alu1_que, pre_alu2_que, preissue_que

    if pre_alu1_que.full() and pre_alu2_que.full():
        # print("Structual hazard, both queue full!")
        return
    # check the num of store encountered and num of issued store
    num_store = 0
    store_issued = 0
    num = 0
    preissue_lookup_list = []

    # not sure
    if preissue_que.qsize() == 0:
        # print("preissue queue is empty")
        return

    for p in range(preissue_que.qsize()):
        preissue_lookup_list.append(preissue_que.get())

    len_preissue = len(preissue_lookup_list)
    start_len = 0

    alp_instr = preissue_lookup_list[start_len]
    score_instrs = list(Scoreboard_dict.keys())
    while start_len < len_preissue:
        alp_instr = preissue_lookup_list[start_len]

        f1 = False
        f2 = False
        f3 = True
        f4 = False

        # SW source operands available
        i1 = find_sourcereg(alp_instr)

        if i1[0] == "SW":
            num_store += 1
            sour = i1[1]
            if (num_store - 1) != store_issued or checkSLW(sour):
                start_len += 1
                # alp_instr = preissue_lookup_list[start_len]
                continue
            else:
                pass

            # store must be issued in order
        elif i1[0] == "LW":
            # print(i1)
            sour = i1[2]
            if (checkSLW(sour) or num_store != store_issued):
                start_len += 1
                # alp_instr = preissue_lookup_list[start_len]
                continue
            else:
                pass

        # search every issued but not finished instr in scoreboard
        for score_instr in score_instrs:

            if scorehzd(score_instr, alp_instr):
                start_len += 1
                # alp_instr = preissue_lookup_list[start_len]
                f1 = True
                break
        if f1:
            continue

        # still want to check if there are hzds with not issued instr
        # RAW, WAR, WAW
        for nissue_str in preissue_lookup_list[:start_len]:
            if issuehzd(nissue_str, alp_instr):
                start_len += 1
                f2 = True
                break

        if f2:
            continue

        if i1[0] == "SW":
            store_issued += 1

        # if there is only one in the preissue queue
        if not f1 and not f2 and len_preissue == 1:
            decide_issue1(alp_instr, preissue_lookup_list)
            # decide_alu_unit(alp_instr, "00000000000000000000000000000001", preissue_lookup_list)
            break

        # SLL LW
        # no hazard with scoreboard instr, check the pre-issue queue
        for otherstr in preissue_lookup_list[start_len + 1:]:
            # check for each instruction
            if not issuehzd(alp_instr, otherstr):
                # check for SWLW operations
                ck1 = find_sourcereg(otherstr)
                f4 = True
                if ck1[0] == "SW":
                    num_store += 1
                    source = ck1[1]
                    if checkSLW(source):
                        continue
                    else:
                        store_issued += 1
                        f4 = True

                elif ck1[0] == "LW":
                    source = ck1[2]
                    if checkSLW(source) or num_store != store_issued:
                        continue
                    else:
                        f4 = True

                else:
                    f4 = True

                get_rslt = decide_alu_unit(alp_instr, otherstr, preissue_lookup_list)
                num = get_rslt[1]

                # f3 = get_rslt[0]
                break
        # success
        if not f1 and not f2 and f4:
            break

        # f4 fail can not be issued in pair, also f1 and f2 return success. Issue one
        if not f1 and not f2 and (not f4):
            # issue one
            # get_rslt = decide_alu_unit(alp_instr, "00000000000000000000000000000001", preissue_lookup_list)
            get_rslt = decide_issue1(alp_instr, preissue_lookup_list)
            num = get_rslt[1]
            break
            # update the scoreboard

    # update the preissue queue
    for s in preissue_lookup_list:
        preissue_que.put(s)


# at most two instrs, one LW/SW and one non memory
# fighting!
def decide_issue1(instr, preissue_lookup_list):
    global pre_alu1_que, pre_alu2_que, Scoreboard_dict, preissue_que
    find = find_sourcereg(instr)
    num = 0
    suc_flag = False
    if find[0] in slw_set:
        if not pre_alu1_que.full():
            pre_alu1_que.put(instr)
            Scoreboard_dict[instr] = find
            preissue_lookup_list.remove(instr)
            num += 1
            suc_flag = True
    elif find[0] not in slw_set:
        if not pre_alu2_que.full():
            pre_alu2_que.put(instr)
            Scoreboard_dict[instr] = find
            preissue_lookup_list.remove(instr)
            num += 1
            suc_flag = True
    return suc_flag, num

def decide_alu_unit(instr1, instr2, preissue_lookup_list):
    global pre_alu1_que, pre_alu2_que, Scoreboard_dict, preissue_que
    # wrong
    find1 = find_sourcereg(instr1)
    find2 = find_sourcereg(instr2)
    num = 0
    # temp = find.split('\t')
    # opcode = temp[0]
    # opcode = opcode[0:6]
    # parsed_instr = searchkey(opcode)
    suc_flag = False
    # only care about the first one
    if find1[0] in slw_set and find2[0] in slw_set:
        if not pre_alu1_que.full():
            pre_alu1_que.put(instr1)
            Scoreboard_dict[instr1] = find1
            preissue_lookup_list.remove(instr1)
            num += 1
            suc_flag = True
    # both in alu2 set
    elif find1[0] not in slw_set and find2[0] not in slw_set:
        if not pre_alu2_que.full():
            pre_alu2_que.put(instr1)
            Scoreboard_dict[instr1] = find1
            preissue_lookup_list.remove(instr1)
            num += 1
            suc_flag = True

    elif find1[0] not in slw_set and find2[0] in slw_set:
        if not pre_alu2_que.full():
            pre_alu2_que.put(instr1)
            Scoreboard_dict[instr1] = find1
            preissue_lookup_list.remove(instr1)
            num += 1
            suc_flag = True
        if not pre_alu1_que.full():
            pre_alu1_que.put(instr2)
            Scoreboard_dict[instr2] = find2
            preissue_lookup_list.remove(instr2)
            num += 1
            suc_flag = True
    elif find2[0] not in slw_set and find1[0] in slw_set:
        if not pre_alu2_que.full():
            pre_alu2_que.put(instr2)
            Scoreboard_dict[instr2] = find2
            preissue_lookup_list.remove(instr2)
            num += 1
            suc_flag = True
        if not pre_alu1_que.full():
            pre_alu1_que.put(instr1)
            Scoreboard_dict[instr1] = find1
            preissue_lookup_list.remove(instr1)
            num += 1
            suc_flag = True
    return suc_flag, num


def alu1_unit():
    global reg
    global memory
    global pre_alu1_que

    if pre_alu1_que.empty():
        return
    # if we use get, the element is deleted from alu1 queue
    alu1_instr = pre_alu1_que.get()
    rt, offset, base = swlw(alu1_instr)
    # memory[reg[int(base)] + int(offset)] = reg[int(rt)]
    mem_adrs = reg[int(base)] + int(offset)
    reg_adrs = int(rt)
    # push the "SW" or "LW" to the queue
    instr_opcode = find_sourcereg(alu1_instr)
    # change here!
    alu7_instr = alu1_instr + " " + "\t" + " " + instr_opcode[0] + " " + str(mem_adrs) + " " + str(reg_adrs)
    pre_mem_que.put(alu7_instr)
    return

def alu2_unit():
    global post_alu2_que
    global pre_alu2_que

    if pre_alu2_que.empty():
        return
    alu2_instr = pre_alu2_que.get()

    fetchcode = alu2_instr.split('\t')
    bicode = fetchcode[0]
    opcode = bicode[0:6]
    fetchcode = fetchcode[1:]
    parsed_instr = searchkey(opcode)

    # fetch_part1 = convert_list_to_string(fetchcode[0], '')
    # fetch_part2 = convert_list_to_string(fetchcode[1], '')
    # print(fetch_part1)
    # print(fetch_part2)
    # print(fetchcode)
    dest_reg = 0
    value = 0
    if parsed_instr == "ADD":
        dest_reg, value = add(alu2_instr)
    elif parsed_instr == "MUL":
        dest_reg, value = mul(alu2_instr)
    elif parsed_instr == "SUB":
        dest_reg, value = sub(alu2_instr)
    elif parsed_instr == "AND":
        dest_reg, value = func_and(alu2_instr)
    elif parsed_instr == "OR":
        dest_reg, value = func_or(alu2_instr)
    elif parsed_instr == "XOR":
        dest_reg, value = xor(alu2_instr)
    elif parsed_instr == "NOR":
        dest_reg, value = nor(alu2_instr)
    elif parsed_instr == "SLT":
        dest_reg, value = slt(alu2_instr)
    elif parsed_instr == "ADDI":
        dest_reg, value = addi(alu2_instr)
    elif parsed_instr == "ANDI":
        dest_reg, value = andi(alu2_instr)
    elif parsed_instr == "ORI":
        dest_reg, value = ori(alu2_instr)
    elif parsed_instr == "XORI":
        dest_reg, value = xori(alu2_instr)
    elif parsed_instr == "SLL":
        dest_reg, value = sll(alu2_instr)
    elif parsed_instr == "SRL":
        dest_reg, value = srl(alu2_instr)
    elif parsed_instr == "SRA":
        dest_reg, value = sra(alu2_instr)
    # possible exception handling, stack overflow
    alu2_instr = alu2_instr + " " + str(dest_reg) + " " + str(value)
    post_alu2_que.put(alu2_instr)


def Mem_unit():
    global post_mem_que
    global pre_mem_que
    global memory
    global reg
    sw_delete_list = []
    # try to return a list
    if pre_mem_que.empty():
        return sw_delete_list
    mem_instr = pre_mem_que.get()
    # chedck here!
    op_array = mem_instr.split(' ')
    op_instr = op_array[len(op_array) -3]

    if op_instr == "LW":
        post_mem_que.put(mem_instr)
    if op_instr == "SW":
        mem_address = int(op_array[len(op_array) -2])
        reg_address = int(op_array[len(op_array) -1])
        memory[mem_address] = reg[reg_address]
        sodagreen3 = convert_list_to_string2(op_array[:3])
        sw_delete_list.append(sodagreen3.strip())
        # Scoreboard_dict.pop(op_array[0])
    return sw_delete_list

def WB_unit():
    global post_alu2_que
    global post_mem_que
    global memory
    global reg
    global Scoreboard_dict
    # return score board delete list, can not directly delete from scoreboard
    score_delete_list = []

    if not post_alu2_que.empty():
        alu2_instr = post_alu2_que.get()
        result = alu2_instr.split(' ')
        dst_reg = int(result[len(result) - 2])
        value = int(result[len(result) - 1])
        reg[dst_reg] = value
        # update the scoreboard and delete the finished instr
        # score_delete_list.append(result[0])
        sodagreen = convert_list_to_string2(result[:len(result) -2])
        score_delete_list.append(sodagreen.strip())
        # print(score_delete_list)
        # Scoreboard_dict.pop(result[0])

    if not post_mem_que.empty():
        LW_instr = post_mem_que.get()
        result2 = LW_instr.split(' ')
        reg_address = int(result2[len(result2) - 1])
        mem_address = int(result2[len(result2) - 2])
        reg[reg_address] = memory[mem_address]
        sodagreen2 = convert_list_to_string2(result2[:3])
        score_delete_list.append(sodagreen2.strip())
        # Scoreboard_dict.pop(result2[0])

    return score_delete_list


def disassembler(input):
    f_dis = open("disassembly2.txt", 'w')
    f_sample = open(input, "r")
    line = f_sample.readline()
    global PC

    while line:
        PC += 4
        inscode = line.strip()
        opcode = inscode[0:6]
        f_dis.write(inscode + '\t' + str(PC) + '\t')
        # f_dis.write('\t')
        # f_dis.write(str(PC) + '\t')
        # f_dis.write('\t')

        parsed_instr = searchkey(opcode)
        if parsed_instr in regset:
            rd, rs, rt = getreg(inscode)
            f_dis.write(parsed_instr + " R" + rd + ", R" + rs + ", R" + rt)
            f_dis.write('\n')
        elif parsed_instr in immeset:
            rt, rs, imme = getimme(inscode)
            f_dis.write(parsed_instr + " R" + rt + ", R" + rs + ", #" + imme)
            f_dis.write('\n')
        elif parsed_instr in trisset:
            rd, rt, sa = tris(inscode)
            f_dis.write(parsed_instr + " R" + rd + ", R" + rt + ", #" + sa)
            f_dis.write('\n')
        elif parsed_instr in bgltzset:
            rs, offset = bgltz(inscode)
            f_dis.write(parsed_instr + " R" + rs + ", " + "#" + offset)
            f_dis.write('\n')
        elif parsed_instr == "J":
            target = jump_code(inscode)
            f_dis.write(parsed_instr + " #" + target)
            f_dis.write('\n')
        elif parsed_instr == "JR":
            rs = jr_code(inscode)
            f_dis.write(parsed_instr + " R" + rs)
            f_dis.write('\n')
        elif parsed_instr == "BEQ":
            rs, rt, offset = beq_code(inscode)
            f_dis.write(parsed_instr + " R" + rs + ", R" + rt + ", #" + offset)
            f_dis.write('\n')
        elif parsed_instr == "BREAK":
            f_dis.write("BREAK")
            f_dis.write('\n')
        elif parsed_instr in slw_set:
            rt, offset, base = swlw(inscode)
            f_dis.write(parsed_instr + " R" + rt + ", " + offset + "(R" + base + ")")
            f_dis.write('\n')
        elif parsed_instr == "NOP":
            f_dis.write("NOP")
            f_dis.write('\n')
        else:
            re = handledata(inscode)
            memory[PC] = re
            f_dis.write(str(re))
            f_dis.write('\n')
        line = f_sample.readline()
    PC = 256
    f_sample.close()
    f_dis.close()


def printQueue(q, name, f_simu):
    queue_num = 0
    max_size = q.maxsize
    if name == "Pre-MEM Queue" or name == "Post-MEM Queue":
        if q.empty():
            f_simu.write(name + ":" + "\n")
            return
        for qq in q.queue:
            temp_qq = qq.split("\t")
            temp_qq = temp_qq[2]
            temp_qq = temp_qq.strip()
            f_simu.write(name + ": [" + temp_qq + "]" + "\n")
        return

    elif name == "Post-ALU2 Queue":
        if q.empty():
            f_simu.write(name + ":" + "\n")
            return
        for qq in q.queue:
            # temp_qq = qq
            temp_qq = qq.split("\t")
            temp_qq = temp_qq[2]
            temp_qq = temp_qq.strip()
            temp_qq = temp_qq.split(" ")
            temp_qq = convert_list_to_string2(temp_qq[:4])
            f_simu.write(name + ": [" + temp_qq + "]" + "\n")
        return
    else:
        f_simu.write(name + ":" + "\n")
        for qq in q.queue:
            # temp_qq = qq
            temp_qq = qq.split("\t")
            temp_qq = temp_qq[2]
            temp_qq = temp_qq.strip()
            f_simu.write("\t" + "Entry " + str(queue_num) + ": [" + temp_qq + "]" + "\n")
            queue_num += 1
        while queue_num < max_size:
            f_simu.write("\t" + "Entry " + str(queue_num) + ":" + "\n")
            queue_num += 1
        return

def printmemory(f):
    f.write('\n')
    f.write("Data" + '\n')
    keyset = list(memory.keys())
    length = len(keyset)
    # key = keyset[0]
    times = math.floor(length/8)
    timesplus = math.ceil(length/8)
    for i in range(0, times):

        f.write(str(keyset[8 * i]) + ':' + '\t')
        for j in keyset[8 * i :8 * (i + 1)]:
            if j == keyset[8 * i + 7]:
                f.write(str(memory[j]))
                break
            f.write(str(memory[j]) + '\t')
        f.write('\n')

    if(times != timesplus):
        start = times * 8
        f.write(str(keyset[start]) + ':' + '\t')
        for k in keyset[start, length]:
            if k == length -1:
                f.write(str(memory[k]))
                break
            f.write(str(memory[k]) + '\t')
        f.write('\n')
    return

def printRegister(f):
    global reg
    f.write('\n')
    f.write("Registers" + '\n')
    f.write("R00:" + '\t')
    for i in range(8):
        if i == 7:
            f.write(str(reg[i]))
            break
        f.write(str(reg[i]))
        f.write('\t')
    f.write('\n')
    f.write("R08:" + '\t')
    for i in range(8, 16):
        if i == 15:
            f.write(str(reg[i]))
            break
        f.write(str(reg[i]))
        f.write('\t')
    f.write('\n')
    f.write("R16:" + '\t')
    for i in range(16, 24):
        if i == 23:
            f.write(str(reg[i]))
            break
        f.write(str(reg[i]))
        f.write('\t')
    f.write('\n')
    f.write("R24:" + '\t')

    for i in range(24,32):
        if i == 31:
            f.write(str(reg[i]))
            break
        f.write(str(reg[i]))
        f.write('\t')
    f.write('\n')
    return

def main(argv):
    global Cycle

    file_name = argv
    disassembler(file_name)
    # disassembler("sample2.txt")

    f_simu = open("simulation.txt", "w")
    while not brk_stop_flag:
        f_simu.write("--------------------" + "\n")
        f_simu.write("Cycle " + str(Cycle) + ":" + "\n\n")

        scorebd_del_list = WB_unit()
        sw_del_list = Mem_unit()
        alu1_unit()
        alu2_unit()
        Issue()

        IF("disassembly2.txt", f_simu)

        for dlt in scorebd_del_list:
            Scoreboard_dict.pop(dlt)
        for dlt2 in sw_del_list:
            Scoreboard_dict.pop(dlt2)

        printQueue(preissue_que, "Pre-Issue Queue", f_simu)
        printQueue(pre_alu1_que, "Pre-ALU1 Queue", f_simu)
        printQueue(pre_mem_que, "Pre-MEM Queue", f_simu)
        printQueue(post_mem_que, "Post-MEM Queue", f_simu)
        printQueue(pre_alu2_que, "Pre-ALU2 Queue", f_simu)
        printQueue(post_alu2_que, "Post-ALU2 Queue", f_simu)

        printRegister(f_simu)
        printmemory(f_simu)

        Cycle += 1

    f_simu.close()


if __name__ == "__main__":
    # main("sample.txt")
    main(sys.argv[1])
    if os.path.exists("disassembly2.txt"):
        os.remove("disassembly2.txt")



