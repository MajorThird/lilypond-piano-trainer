from fractions import Fraction
import staff_helpers

class Staff(object):
    def __init__(self):
        pass

class NoteContainer(object):
    def __init__(self, start_time=None, notes=None, hold_info=[]):
        self.start_time = start_time
        self.notes = notes
        self.hold_info = hold_info

    def __str__(self):
        ret_str = str(float(self.start_time))
        ret_str += ": " + str(self.notes).replace("[","").replace("]", "").replace(", ", "+")
        hold_characters = [str(b)[0] for b in self.hold_info]
        ret_str += ": " + str(hold_characters).replace("'","").replace("[","").replace("]", "").replace(", ", "-")
        # print("test", self.start_time, ret_str)
        return ret_str



def get_staffs(filename="test.ly"):
    with open(filename) as infile:
        content = infile.read()
        content = staff_helpers.remove_comments(content)
        # print(content)
        content = content.replace("{", "{ ")
        content = content.replace("}", " }")
        content = content.replace("\n", " ")
        content = " ".join(content.split())

    staff_strings = staff_helpers.get_staff_strings(content)
    staff_strings = staff_helpers.get_normalized_staff_strings(staff_strings)
    staffs = []
    for s in staff_strings:
        st = get_staff(s)
        staffs.append(st)
    return staffs



def get_total_stream(content):
    total_stream = []
    current_stream = total_stream

    fragments = content.split(" ")
    i = 0
    while i < len(fragments):
        f = fragments[i]
        if f == "<<":
            total_stream.append([ [] ])
            current_stream = total_stream[-1][0]
        elif f == "\\\\":
            total_stream[-1].append( [] )
            current_stream = total_stream[-1][-1]
            # print(total_stream[-1])
        elif f == ">>":
            current_stream = total_stream
        else:
            current_stream.append(f)
        i += 1
    return total_stream


def get_staff(
        content,
        start_time=Fraction(0),
        initial_note_length=Fraction(1,4)):

    res_staff = Staff()

    total_stream = get_total_stream(content)


    res_is_note = iterate_over_stream(total_stream, is_note)
    res_is_pause = iterate_over_stream(total_stream, is_pause)
    res_dot_factors = iterate_over_stream(total_stream, get_dot_factor)
    res_digits = iterate_over_stream(total_stream, get_digits)
    res_is_chord_start = iterate_over_stream(total_stream, is_chord_start)
    res_is_chord_end = iterate_over_stream(total_stream, is_chord_end)
    res_tuplet_tag = iterate_over_stream(total_stream, containts_tuplet_tag)
    res_tuplet_factor_tag = iterate_over_stream(total_stream, get_tuplet_factor_tag)

    # init grace note stream
    grace_note_stream = get_initial_stream_with_equal_values(total_stream, False)
    modify_grace_note_stream(total_stream, grace_note_stream)

    calculated_note_lengths, _ = calculate_for_stream([res_digits, res_is_note, res_is_pause], get_note_length, Fraction(1,4))
    calculated_belongs_to_chord_without_end, _ = calculate_for_stream([res_is_chord_start, res_is_chord_end], get_belongs_to_chord_without_end, False)
    calculated_belongs_to_tuplet, _ = calculate_for_stream([total_stream], get_belongs_to_tuplet, False)
    calculated_tuplet_factors, _ = calculate_for_stream([calculated_belongs_to_tuplet, res_tuplet_factor_tag], get_tuplet_factor, Fraction(1,1))
    calculated_total_note_lengths, _ = calculate_for_stream([calculated_note_lengths, calculated_tuplet_factors, res_dot_factors], get_total_note_length, Fraction(1,4))
    correct_note_lengths_in_chords(calculated_total_note_lengths, calculated_belongs_to_chord_without_end)

    calculated_does_advance_time, _ = calculate_for_stream([res_is_note, res_is_pause, calculated_belongs_to_chord_without_end, grace_note_stream], get_advance_time, True)
    calculated_start_times = calculate_start_times(calculated_does_advance_time, calculated_total_note_lengths, res_is_note, res_is_pause, total_stream)

    correct_start_times_tuples(calculated_start_times, res_tuplet_tag)
    correct_start_times_octave_marks(calculated_start_times, total_stream)

    time_signature_changes, time_signature_changes_strings = find_time_signature_changes(total_stream, calculated_start_times)
    max_event_time = get_max_event_time(calculated_start_times)
    bar_starts, bar_endings = determine_bars(time_signature_changes, max_time=max_event_time)
    key_changes = find_key_changes(total_stream, calculated_start_times)
    clef_changes = find_clef_changes(total_stream, calculated_start_times)

    add_note_lengths(total_stream, calculated_note_lengths, calculated_belongs_to_chord_without_end, res_is_chord_end, res_is_note, res_is_pause)
    note_stream = get_note_stream(total_stream, res_is_note, res_is_chord_end, calculated_start_times, grace_note_stream)
    note_stream_without_holds = get_note_stream_without_holds(note_stream)

    # add things to staff
    res_staff.note_stream_without_holds = note_stream_without_holds
    res_staff.total_stream = total_stream
    res_staff.bar_starts = bar_starts
    res_staff.bar_endings = bar_endings
    res_staff.key_changes = key_changes
    res_staff.clef_changes = clef_changes
    res_staff.calculated_start_times = calculated_start_times
    res_staff.res_is_note = res_is_note
    res_staff.time_signature_changes_strings = time_signature_changes_strings
    res_staff.calculated_belongs_to_chord_without_end = calculated_belongs_to_chord_without_end
    res_staff.grace_note_stream = grace_note_stream
    res_staff.complete_lily_string = content
    correct_start_times_grace_commands(calculated_start_times, total_stream)

    #debug_list(note_stream_without_holds, to_float=False)
    #debug_list(calculated_does_advance_time, to_float=False)
    #debug_list(grace_note_stream, to_float=False)
    #debug_list(calculated_start_times, to_float=True)
    #print("time_signature_changes", time_signature_changes_strings)

    return res_staff


def correct_start_times_grace_commands(calculated_start_times, total_stream):
    for index, elem in enumerate(total_stream):
        if type(elem) != list:
            if total_stream[index] == "\\grace":
                if total_stream[index + 1] == "{":
                    calculated_start_times[index] = calculated_start_times[index + 2]
                    calculated_start_times[index + 1] = calculated_start_times[index + 2]
                else:
                    calculated_start_times[index] = calculated_start_times[index + 1]
        else:
            for sub_index, sub_stream in enumerate(elem):
                correct_start_times_grace_commands(calculated_start_times[index][sub_index], sub_stream)



def get_initial_stream_with_equal_values(total_stream, initial_value):
    initial_stream = []
    for index, elem in enumerate(total_stream):
        if type(elem) != list:
            initial_stream.append(initial_value)
        else:
            initial_stream.append([])
            for sub_stream in elem:
                initial_stream[-1].append(get_initial_stream_with_equal_values(sub_stream, initial_value))
    return initial_stream

def modify_grace_note_stream(total_stream, grace_note_stream):
    for index, elem in enumerate(total_stream):
        if type(elem) != list:
            if elem == "\\grace":
                grace_note_stream[index] = True
                # print("Hallo")
                if total_stream[index + 1] == "{":
                    # print("Klammer")
                    grace_note_stream[index + 1] = True
                    add_index = 2
                    bracket_closed = False
                    while not bracket_closed:
                        next_elem = total_stream[index + add_index]
                        if next_elem == "}":
                            grace_note_stream[index + add_index] = True
                            bracket_closed = True
                            # print("klammer zu")
                        else:
                            grace_note_stream[index + add_index] = True
                            # print(next_elem)
                            add_index += 1
                else:
                    grace_note_stream[index + 1] = True

        else:
            for sub_index, sub_stream in enumerate(elem):
                modify_grace_note_stream(sub_stream, grace_note_stream[index][sub_index])



def get_note_stream_without_holds(note_stream):
    # nc = NoteContainer(start_time=note_stream[0].start_time, notes=note_stream[0].notes)
    # note_stream_without_holds = [nc]
    note_stream_without_holds = []
    for index, elem in enumerate(note_stream):
        if type(elem) != list:
            current_notes = elem.notes
            # get info about previous holds
            if index == 0:
                actually_played = [n for n in elem.notes]
            elif type(note_stream[index-1]) == list:
                hold = []
                for sub_stream in note_stream[index-1]:
                    if len(sub_stream) > 0:
                        prev_notes = sub_stream[-1].notes
                        prev_hold = sub_stream[-1].hold_info
                        hold += [n for i, n in enumerate(prev_notes) if prev_hold[i] == True]
                actually_played = [n for n in elem.notes if not n in hold]
            else:
                prev_notes = note_stream[index-1].notes
                prev_hold = note_stream[index-1].hold_info
                hold = [n for i, n in enumerate(prev_notes) if prev_hold[i] == True]
                actually_played = [n for n in elem.notes if not n in hold]
            # if len(actually_played) > 0:
            nc = NoteContainer(start_time=elem.start_time, notes=actually_played)
            note_stream_without_holds.append(nc)
                # print("prev", nc.notes, hold)
        else:
            if index == 0:
                hold_before_first = []
            elif type(note_stream[index-1]) != list:
                hold_before_first = []
            else:
                hold_before_first = []
                for sub_stream in note_stream[index-1]:
                    if len(sub_stream) > 0:
                        prev_notes = sub_stream[-1].notes
                        prev_hold = sub_stream[-1].hold_info
                        hold_before_first += [n for i, n in enumerate(prev_notes) if prev_hold[i] == True]

            note_stream_without_holds_sub = [[] for k in range(len(note_stream[index]))]
            for sub_index, sub_stream in enumerate(note_stream[index]):
                if len(sub_stream) > 0:
                    for sub_elem_index, sub_elem in enumerate(sub_stream):
                        notes = sub_stream[sub_elem_index].notes
                        time = sub_stream[sub_elem_index].start_time
                        if sub_elem_index == 0:
                            #print("hold", hold_before_first, index)
                            hold = hold_before_first
                        else:
                            prev_notes = sub_stream[sub_elem_index-1].notes
                            prev_hold = sub_stream[sub_elem_index-1].hold_info
                            hold = [n for i, n in enumerate(prev_notes) if prev_hold[i] == True]

                        actually_played = [n for n in notes if not n in hold]
                        nc = NoteContainer(start_time=time, notes=actually_played)
                        # if len(actually_played) > 0:
                        note_stream_without_holds_sub[sub_index].append(nc)
            note_stream_without_holds.append(note_stream_without_holds_sub)


    return note_stream_without_holds

def get_note_stream(total_stream, res_is_note, res_is_chord_end, calculated_start_times, grace_note_stream):
    note_stream = []
    for index, elem in enumerate(total_stream):
        if type(elem) != list:
            # not "\\rest" in elem denn auch pausen mit rest werden als note gezaehlt
            if res_is_note[index] and not grace_note_stream[index] and not "\\rest" in elem:
                isolated = get_isolated_fragment(elem, remove_octave_characters=False)
                hold = True if "~" in elem else False
                if note_stream == []:
                    notes = NoteContainer(start_time=calculated_start_times[index], notes=[isolated], hold_info=[hold])
                    note_stream.append(notes)
                elif type(note_stream[-1]) == list:
                    notes = NoteContainer(start_time=calculated_start_times[index], notes=[isolated], hold_info=[hold])
                    note_stream.append(notes)
                else:
                    if note_stream[-1].start_time == calculated_start_times[index]:
                        note_stream[-1].notes.append(isolated)
                        if hold:
                            note_stream[-1].hold_info.append(True)
                            if res_is_chord_end[index] and "~" in elem.split(">")[1]:
                                note_stream[-1].hold_info = [True for i in range(len(note_stream[-1].hold_info))] # akkordende: alle sind hold notes
                        else:
                            note_stream[-1].hold_info.append(False)

                    else:
                        notes = NoteContainer(start_time=calculated_start_times[index], notes=[isolated], hold_info=[hold])
                        note_stream.append(notes)
        else:
            note_stream.append([])
            for sub_index, sub_stream in enumerate(elem):
                note_stream[-1].append( get_note_stream(sub_stream, res_is_note[index][sub_index], res_is_chord_end[index][sub_index], calculated_start_times[index][sub_index], grace_note_stream[index][sub_index] ) )

    return note_stream

# einige noten enthalten keine zahlen. fuege sie hinzu.
def add_note_lengths(total_stream, calculated_note_lengths, calculated_belongs_to_chord_without_end, res_is_chord_end, res_is_note, res_is_pause):
    for index, elem in enumerate(total_stream):
        if type(elem) != list:
            elem_digits = get_digits(total_stream, index)   #''.join([c for c in elem if c.isdigit()])
            note_value = str(calculated_note_lengths[index].denominator)
            isolated = get_isolated_fragment(elem, remove_octave_characters=False)
            if len(elem_digits) == 0:
                if res_is_note[index]:
                    if not calculated_belongs_to_chord_without_end[index] and not res_is_chord_end[index]:
                            total_stream[index] = total_stream[index].replace(isolated, isolated + note_value)
                    elif res_is_chord_end[index]:
                        total_stream[index] = total_stream[index].replace(">", ">" + note_value)
                elif res_is_pause[index]:
                    if "\\rest" in elem:
                        total_stream[index] = total_stream[index].replace("\\rest", note_value + "\\rest")
                    else:
                        for c in ["R", "r"]:
                            total_stream[index] = total_stream[index].replace(c, c + note_value)
        else:
            for sub_index, sub_stream in enumerate(elem):
                add_note_lengths(total_stream[index][sub_index], calculated_note_lengths[index][sub_index], calculated_belongs_to_chord_without_end[index][sub_index], res_is_chord_end[index][sub_index], res_is_note[index][sub_index], res_is_pause[index][sub_index])



def get_max_event_time(calculated_start_times):
    if type(calculated_start_times[-1]) == list:
        times = [l[-1] for l in calculated_start_times[-1]]
        return max(times)
    else:
        return calculated_start_times[-1]

def determine_bars(time_signature_changes, max_time):
    time = Fraction(0)
    bar_length = Fraction(1)
    bar_endings = []
    bar_starts = [Fraction(0)]
    while time < max_time:
        next_ending = bar_starts[-1] + bar_length
        for t in time_signature_changes:
            change_time = t[0]
            if change_time < next_ending:
                bar_length = t[1]
                next_ending = bar_starts[-1] + bar_length
        bar_endings.append(next_ending)
        bar_starts.append(next_ending)
        time = next_ending

    return bar_starts, bar_endings


def find_key_changes(total_stream, calculated_start_times):
    #key_changes = [(Fraction(-9999999,1), "c \\major")]
    key_changes = []
    for index, elem in enumerate(total_stream):
        if type(elem) == list:
            for sub_index, sub_stream in enumerate(elem):
                key_changes += find_key_changes(sub_stream, calculated_start_times[index][sub_index])
        else:
            if elem == "\\key":
                start_time = calculated_start_times[index]
                key = total_stream[index + 1] + " " + total_stream[index + 2]
                key_changes.append((start_time, key))
    #print("keys", key_changes)
    return key_changes

def find_clef_changes(total_stream, calculated_start_times):
    #clef_changes = [(Fraction(-9999999,1), "bass")]
    clef_changes = []
    for index, elem in enumerate(total_stream):
        if type(elem) == list:
            for sub_index, sub_stream in enumerate(elem):
                clef_changes += find_clef_changes(sub_stream, calculated_start_times[index][sub_index])
        else:
            if elem == "\\clef":
                start_time = calculated_start_times[index]
                clef = total_stream[index + 1]
                clef_changes.append((start_time, clef))
    return clef_changes

def find_time_signature_changes(total_stream, calculated_start_times):
    time_signature_changes = []
    time_signature_changes_strings = []
    for index, elem in enumerate(total_stream):
        if type(elem) == list:
            for sub_index, sub_stream in enumerate(elem):
                res_a, res_b = find_time_signature_changes(sub_stream, calculated_start_times[index][sub_index])
                time_signature_changes += res_a
                time_signature_changes_strings += res_b
        else:
            if elem == "\\time":
                start_time = calculated_start_times[index]
                signature_str = total_stream[index + 1]
                denominator = int(signature_str.split("/")[1])
                numerator = int(signature_str.split("/")[0])
                signature = Fraction(numerator, denominator)
                time_signature_changes.append((start_time, signature))
                time_signature_changes_strings.append((start_time, signature_str))
    return time_signature_changes, time_signature_changes_strings

#
# def correct_start_times_time_changes(calculated_start_times, total_stream):
#     for index, time in enumerate(calculated_start_times):
#         if type(time) == list:
#             for sub_index, sub_times in enumerate(time):
#                 correct_start_times_time_changes(sub_times, total_stream[index][sub_index])
#         else:
#             if total_stream[index] == "\\time":
#                 delta_index = 2
#                 for i in range(delta_index):
#                     calculated_start_times[index + i] = calculated_start_times[index + delta_index]

def correct_start_times_octave_marks(calculated_start_times, total_stream):
    for index, elem in enumerate(total_stream):
        if type(elem) == list:
            for sub_index, sub_stream in enumerate(elem):
                correct_start_times_octave_marks(calculated_start_times[index][sub_index], sub_stream)
        else:
            if elem == "\\ottava":
                # find next note
                add_index = 0
                found = False
                while not found:
                    next_index = index + add_index
                    # next_elem = total_stream[next_index]
                    if type(total_stream[next_index]) == list:
                        next_start_times = [l[0] for l in calculated_start_times[next_index]]
                        next_start_time = min(next_start_times)
                        found = True
                    elif is_note(total_stream, next_index) or is_pause(total_stream, next_index):
                        #print("Testtest")
                        next_start_time = calculated_start_times[next_index]
                        found = True
                    add_index += 1
                calculated_start_times[index] = next_start_time
                calculated_start_times[index + 1] = next_start_time



def correct_start_times_tuples(calculated_start_times, res_tuplet_tag):
    for index, time in enumerate(calculated_start_times):
        if type(time) == list:
            for sub_index, sub_times in enumerate(time):
                correct_start_times_tuples(sub_times, res_tuplet_tag[index][sub_index])
        else:
            if res_tuplet_tag[index] == True:
                delta_index = 3
                for i in range(delta_index):
                    calculated_start_times[index + i] = calculated_start_times[index + delta_index]
                    # print(calculated_start_times[index + i])


# die anfaenge von akkorden haben falsche notenlaengen (noch die von den noten davor).
# deshalb werden die dann auf den wert gesetzt, den das akkordende hat.
# evtl braucht man das nicht, weil gar nicht die zeit proceedet wird an dieser stelle
def correct_note_lengths_in_chords(stream_for_correction, calculated_belongs_to_chord_without_end):
    for index, elem in enumerate(stream_for_correction):
        if type(elem) == list:
            for sub_index, sub_elem in enumerate(elem):
                correct_note_lengths_in_chords(sub_elem, calculated_belongs_to_chord_without_end[index][sub_index])
        else:
            if calculated_belongs_to_chord_without_end[index] == True:
                found = False
                add_index = 1
                while not found:
                    if calculated_belongs_to_chord_without_end[index + add_index]:
                        add_index += 1
                    else:
                        stream_for_correction[index] = stream_for_correction[index + add_index]
                        found = True


def calculate_start_times(calculated_does_advance_time, calculated_total_note_lengths, res_is_note, res_is_pause, total_stream):
    start_times = []
    previous_time = Fraction(0)
    next_time = Fraction(0)
    for index, length in enumerate(calculated_total_note_lengths):
        if type(length) == list:
            start_times.append([])
            for l_index, l in enumerate(length):
                sub_next_time = next_time
                sub_previous_time = next_time
                start_times[-1].append([])
                for sub_index, sub_length in enumerate(l):
                    if res_is_note[index][l_index][sub_index] or res_is_pause[index][l_index][sub_index]:
                        start_times[-1][-1].append(sub_next_time)
                    else:
                        start_times[-1][-1].append(sub_previous_time)
                    sub_previous_time = start_times[-1][-1][-1]
                    if calculated_does_advance_time[index][l_index][sub_index]:
                        sub_next_time += calculated_total_note_lengths[index][l_index][sub_index]
            previous_time = sub_next_time
            next_time = sub_next_time
        else:
            if res_is_note[index] or res_is_pause[index]:
                start_times.append(next_time)
            elif total_stream[index] == "\\time":
                start_times.append(next_time)
            elif index > 0 and total_stream[index - 1] == "\\time":
                start_times.append(next_time)
            elif total_stream[index] == "\\clef":
                start_times.append(next_time)
            elif index > 0 and total_stream[index - 1] == "\\clef":
                start_times.append(next_time)
            else:
                start_times.append(previous_time)
            previous_time = start_times[-1]

            if calculated_does_advance_time[index]:
                next_time = next_time + length
    return start_times

# def get_previous_end_time(index, calculated_end_times):
#     if index == 0:
#         return Fraction(0)
#     elif type(calculated_end_times[index-1]) == list:
#         return calculated_end_times[index-1][-1][-1]
#     else:
#         return calculated_end_times[index-1]
#
# def calculate_start_times(calculated_end_times):
#     start_times = []
#     for index, end_time in enumerate(calculated_end_times):
#         if type(end_time) == list:
#             start_times.append([])
#             for l_index, l in enumerate(end_time):
#                 start_times[-1].append([])
#                 for sub_index, sub_end_time in enumerate(l):
#                     if sub_index > 0:
#                         start_times[-1][-1].append(calculated_end_times[index][l_index][sub_index-1])
#                         # start_times[-1][-1].append(777)
#                     else:
#                         if type(calculated_end_times[index-1]) != list:
#                             start_times[-1][-1].append(calculated_end_times[index-1])
#                         else:
#                             start_times[-1][-1].append(calculated_end_times[index-1][-1][-1])
#
#         else:
#             start_times.append(get_previous_end_time(index, calculated_end_times))
#     return start_times



def calculate_for_stream(value_streams, f, prev_res_init, previous_res_mode="chronological"):
    result = []
    prev_result = prev_res_init
    for i in range(len(value_streams[0])):
        if type(value_streams[0][i]) == list:
            number_of_sub_streams = len(value_streams[0][i])
            sub_results = []
            for sub_index in range(number_of_sub_streams):
                sub_value_streams = [ value_streams[k][i][sub_index] for k in range(len(value_streams)) ]
                if previous_res_mode == "chronological":
                    result_sub, prev_result = calculate_for_stream(sub_value_streams, f, prev_result)
                elif previous_res_mode == "time_calc":
                    if sub_index == number_of_sub_streams - 1:
                        result_sub, prev_result = calculate_for_stream(sub_value_streams, f, prev_result)
                    else:
                        result_sub, _ = calculate_for_stream(sub_value_streams, f, prev_result)

                sub_results.append(result_sub)
            result.append(sub_results)
        else:
            values = [stream[i] for stream in value_streams]
            res = f(prev_result, *values)
            result.append(res)
            prev_result = res
        #print("res", result)
    return result, prev_result

    # prev_result = prev_res_init
    # for index, elem in enumerate(stream):
    #     if type(elem) == list:
    #         for sub_index, s in enumerate(elem):
    #             value_sub = [vs[sub_index] for vs in value_streams]
    #             res = calculate_for_stream(s, value_sub, f, prev_result)
    #             # fehlt noch was
    #     else:
    #         res = f(stream, index, prev_result, *value_streams)
    #         result.append(res)
    #         prev_result = res
    # return result, prev_result

def get_end_times(prev_result, does_advance_time, note_length):
    if does_advance_time:
        return prev_result + note_length
    else:
        return prev_result


def get_advance_time(prev_result, is_note, is_pause, belongs_to_chord_without_end, grace_note):
    if (is_note or is_pause) and not belongs_to_chord_without_end and not grace_note:
        return True
    else:
        return False



def get_tuplet_factor(prev_result, belongs_to_tuplet, tuplet_factor_tag):
    if belongs_to_tuplet:
        if tuplet_factor_tag != "":
            denominator = int(tuplet_factor_tag.split("/")[0])
            numerator = int(tuplet_factor_tag.split("/")[1])
            tuplet_factor = Fraction(numerator, denominator)
            return tuplet_factor
        else:
            return prev_result
    else:
        return Fraction(1,1)

def get_belongs_to_tuplet(prev_result, total_stream_elem):
    if prev_result == True:
        if not "}" in total_stream_elem :
            return True
        else:
            return False
    else:
        if "\\tuplet" in total_stream_elem:
            return True
        else:
            return False

def get_belongs_to_chord_without_end(prev_result, is_chord_start, is_chord_end):
    if prev_result == True:
        if not is_chord_end:
            return True
        else:
            return False
    else:
        if is_chord_start:
            return True
        else:
            return False


def get_note_length(prev_result, digits, is_note, is_pause):
    if is_note or is_pause:
        if digits != "":
            return Fraction(1,int(digits))
        else:
            return prev_result
    else:
        return prev_result

def get_total_note_length(prev_result, note_length, tuplet_factor, dot_factor):
    return note_length * tuplet_factor * dot_factor


def iterate_over_stream(stream, f):
    result = []
    for index, elem in enumerate(stream):
        if type(elem) == list:
            result.append([iterate_over_stream(st, f) for st in elem])
        else:
            res = f(stream, index)
            result.append(res)
    return result


def debug_list(lst, to_float=True):
    outstr = ""
    for l in lst:
        if type(l) != list:
            if to_float:
                out = str(float(l))
            else:
                out = str(l)
            line = " " * 20 + "{:40s}\n".format(out)
        else:
            number_of_threads = len(l)
            max_length = max([len(s) for s in l])
            line = ""
            for i in range(max_length):
                for thread_index, thread in enumerate(l):
                    if i >= len(thread):
                        line += "---" + " " * 37
                    else:
                        if to_float:
                            out = str(float(thread[i]))
                        else:
                            out = str(thread[i])
                        line += "{:40s}".format(out)
                line += "\n"
        outstr += line
    print("\n" * 4 + "DEBUG\n" + outstr)




#########################################################
#########################################################
#########################################################
#########################################################
#########################################################
#########################################################
#########################################################
#########################################################
#########################################################
#########################################################

def get_digits(stream, i):
    if "-" in  stream[i]:
        element = stream[i].split("-")[0]
    else:
        element = stream[i]
    elem_digits = ''.join([c for c in element if c.isdigit()])
    return elem_digits


def get_note_names():
    roots = list("cdefgab")
    endings = ["", "is", "isis", "es", "eses"]
    note_names = []
    for r in roots:
        for e in endings:
            note_names.append(r + e)
    return note_names



def is_note(stream, i):
    # if is_pause(stream, i):
    #     return False
    # else:
    element = stream[i]
    isolated = get_isolated_fragment(element)
    note_names = get_note_names()
    if i > 0:
        additional_check = "\\key" != stream[i-1]
    else:
        additional_check = True
    if isolated in note_names and additional_check:
        return True
    else:
        return False

def is_chord_start(stream, i):
    element = stream[i]
    return "<" in element

def is_chord_end(stream, i):
    element = stream[i]
    return ">" in element


def containts_tuplet_tag(stream, i):
    element = stream[i]
    return "\\tuplet" in element


def get_dot_factor(stream, index):
    e = stream[index]
    if "...." in e:
        n = 4
    elif "..." in e:
        n = 3
    elif ".." in e:
        n = 2
    elif "." in e:
        n = 1
    else:
        n = 0
    tmp = Fraction(1,2**n)
    factor = Fraction(2,1) - tmp
    #print(factor)
    return factor



def get_tuplet_factor_tag(stream, index):
    e = stream[index]
    if "\\tuplet" == e:
        return stream[index + 1]
    else:
        return ""





def is_pause(stream, index):
    element = stream[index]
    isolated = get_isolated_fragment(element)
    if isolated.endswith("\\rest") or isolated in ["R", "r", "s"]:
        return True
    else:
        return False

# remove all stuff that prevents us from recognizing notes
def get_isolated_fragment(f, remove_octave_characters=True):
    split_characters = ["_", "^", "\\", "-"]
    for c in split_characters:
        f = f.split(c)[0]
    remove_characters = ["(", ")", "[", "]", ".", "<", ">", "~"]
    if remove_octave_characters:
        for i in range(1,10):
            remove_characters.append("'" * i)
            remove_characters.append("," * i)
    for c in remove_characters:
        f = f.replace(c, "")

    f = ''.join([c for c in f if not c.isdigit()]) # remove digits
    return f
