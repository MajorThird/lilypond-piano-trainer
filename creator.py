import options_creator
import staff
import misc_helpers
import staff_helpers
import chords
from fractions import Fraction
import os
import sys
import subprocess
import cv2



def print_progress(info, long=False):
    """
    This keeps the output on the same line.
    """
    text = "\r"
    for s, value in info:
        if long:
            text += s + ": {:40s}   ".format(str(value))
        else:
            text += s + ": {:10s}   ".format(str(value))
    sys.stdout.write(text)
    sys.stdout.flush()



def resize_images(output_folder, new_width, new_height):
    file_index = 0
    print("Resize images.")
    filenames = [output_folder + "presentation_mode_start.png"]

    while True:
        filename = output_folder + "%05i.png" % file_index
        if os.path.isfile(filename):
            filenames.append(filename)
            file_index += 1
        else:
            break

    for filename in filenames:
        print_progress([("file", filename.split("/")[-1])], long=True)
        img = cv2.imread(filename)
        height = img.shape[0]
        width = img.shape[1]
        if float(width) / float(height) > float(new_width)/new_height:
            scale = float(new_width) / width
            new_size = (int(round(scale * width)), int(round(scale * height)))
            img = cv2.resize(img, new_size)
        else:
            scale = float(new_height) / height
            new_size = (int(round(scale * width)), int(round(scale * height)))
            img = cv2.resize(img, new_size)
        cv2.imwrite(filename, img)

    print("") # new line



def clean_output_folder(output_folder, del_png=False, del_lily=False, del_txt=False):
    endings = ["count", "tex", "texi", "eps"]
    if del_png:
        endings.append("png")
    if del_lily:
        endings.append("ly")

    for ending in endings:
        os.system("rm " + output_folder + "*." + ending + " 2>/dev/null")

    if del_txt:
        os.system("rm " + output_folder + "*.txt 2>/dev/null")

    if del_png:
        os.system("rm " + output_folder + "cropped/*.png 2>/dev/null")


def create_lily_output(step, staff_strings, chord_symbols, output_folder, image_resolution, filename=None):
    if not filename:
        filename = "%05i" % step
    complete_lilypond_string = ""
    lily_front_filename = "lily_front.ly"

    with open(lily_front_filename) as infile:
        complete_lilypond_string += infile.read()

    if len(chord_symbols) > 0:
        complete_lilypond_string += "\\chords {"
        for s in [c.full_string for c in chord_symbols]:
            complete_lilypond_string += s + " "
        complete_lilypond_string += " }\n"

    for s in staff_strings:
        complete_lilypond_string += "\\new Staff {"
        complete_lilypond_string += s
        complete_lilypond_string += " }\n"

    with open("lily_back.ly") as infile:
        complete_lilypond_string += infile.read()

    with open(output_folder + filename + ".ly", "w") as outfile:
        outfile.write(complete_lilypond_string)


    with open(os.devnull, 'wb') as quiet_output:
        outfilename = output_folder + filename
        subprocess.call(["lilypond", "-dbackend=eps", "-dresolution=%i" % image_resolution,
                "--png", "-o", outfilename, output_folder + filename + ".ly"], stdout=quiet_output, stderr=quiet_output)
        if not os.path.isfile(outfilename + ".png"):
            print("ERROR: no PNG written!!!!!!!!!!!!!")

    clean_output_folder(output_folder, del_lily=True)



def resize_image_to_height(img, new_height):
    """
    This preserves the aspect ratio.
    """
    new_width = round(new_height * img.shape[1] / float(img.shape[0]))
    img_resized = cv2.resize(img, (int(new_width), new_height))
    return img_resized



def create_timing_info_output(time, output_folder):
    with open(output_folder + "timing.txt", "a") as outfile:
        outfile.write(str(float(time)) + "\n")


def create_midi_notes_output(mingus_notes, output_folder):
    with open(output_folder + "midi_notes.txt", "a") as outfile:
        midi_notes = sorted([str(int(n)) for n in mingus_notes])
        # remove duplicates
        midi_notes = sorted(list(set(midi_notes)))
        outfile.write(" ".join(midi_notes) + "\n")
    with open(output_folder + "mingus_notes.txt", "a") as outfile:
        mingus_notes = sorted([str(n).replace("'", "") for n in mingus_notes])
        outfile.write(" ".join(mingus_notes) + "\n")


def modify_staff_string_with_color(staff_string, staff_index, stream, index, elem, action_notes, chord_root, calculated_belongs_to_chord_without_end, color_mode):
    is_chord_note = calculated_belongs_to_chord_without_end[index] or ">" in elem
    is_first_chord_note = "<" in elem
    if is_chord_note:
        if is_first_chord_note:
            modify = True
        else:
            modify = False
    else:
        modify = True

    if modify:
        color_string = staff_helpers.create_color_string(action_notes, chord_root, staff_index, color_mode)
        staff_string += " " + color_string

    return staff_string



def get_chord_root(chord_symbols, elem_time):
    chord_root = None
    for c in chord_symbols:
        if elem_time >= c.time:
            chord_root = c.root
    return chord_root


def get_initial_clef(bar_start, clef_changes):
    clef_changes = [(Fraction(-999999999999,1), "treble")] + clef_changes
    for index, k in enumerate(clef_changes):
        if clef_changes[index][0] <= bar_start:
            if index == len(clef_changes) - 1:
                return k
            else:
                if clef_changes[index + 1][0] > bar_start:
                    return k
    print("initial clef ERROR: You should never see this.")

def get_initial_time_signature(bar_start, time_signature_changes):
    for index, k in enumerate(time_signature_changes):
        if time_signature_changes[index][0] <= bar_start:
            if index == len(time_signature_changes) - 1:
                return k
            else:
                if time_signature_changes[index + 1][0] > bar_start:
                    return k
    print("initial time_signature_changes ERROR: You should never see this.")


def get_initial_key(bar_start, key_changes):
    for index, k in enumerate(key_changes):
        if key_changes[index][0] <= bar_start:
            # print(index, k)
            if index == len(key_changes) - 1:
                return k
            else:
                if key_changes[index + 1][0] > bar_start:
                    return k
    print("initial key changes ERROR: You should never see this.")



def create_staff_string(bar_start, bar_end, time, action_notes, chord_symbols, staff, staff_index, active, key_changes, time_signature_changes, color_mode):
    initial_key = get_initial_key(bar_start, key_changes)
    initial_clef = get_initial_clef(bar_start, staff.clef_changes)
    initial_time_signature = get_initial_time_signature(bar_start, time_signature_changes)
    staff_string = ""
    staff_string += " \\key " + initial_key[1]
    staff_string += " \\clef " + initial_clef[1]
    staff_string += " \\time " + initial_time_signature[1]
    stream = staff.total_stream
    for index, elem in enumerate(stream):
        if type(elem) != list:
            elem_time = staff.calculated_start_times[index]
            if elem_time >= bar_start and elem_time < bar_end:
                if staff.res_is_note[index] and time == elem_time and not staff.grace_note_stream[index]:
                    chord_root = get_chord_root(chord_symbols, elem_time)
                    staff_string = modify_staff_string_with_color(staff_string, staff_index, stream, index, elem, action_notes, chord_root, staff.calculated_belongs_to_chord_without_end, color_mode)
                staff_string += " " + elem

        else:
            sub_staff_strings = []
            for sub_index, sub_stream in enumerate(elem):
                sub_staff_string = ""
                for sub_elem_index, sub_elem in enumerate(sub_stream):
                    elem_time = staff.calculated_start_times[index][sub_index][sub_elem_index]
                    if elem_time >= bar_start and elem_time < bar_end:
                        if staff.res_is_note[index][sub_index][sub_elem_index] and time == elem_time and not staff.grace_note_stream[index][sub_index][sub_elem_index]:
                            sub_stream = stream[index][sub_index]
                            sub_calculated_belongs_to_chord_without_end = staff.calculated_belongs_to_chord_without_end[index][sub_index]
                            chord_root = get_chord_root(chord_symbols, elem_time)
                            sub_staff_string = modify_staff_string_with_color(sub_staff_string, staff_index, sub_stream, sub_elem_index, sub_elem, action_notes, chord_root, sub_calculated_belongs_to_chord_without_end, color_mode)
                        sub_staff_string += " " + sub_elem
                if sub_staff_string != "":
                    sub_staff_strings.append(sub_staff_string)

            if len(sub_staff_strings) > 0:
                staff_string += " <<"
                for s_ind, s in enumerate(sub_staff_strings):
                    # first add brackets for the case that voices are longer than one measure, i.e.
                    # voices may be unfinished
                    if s[0:2] != " {":
                        s = " { " + s
                    if s.count("{") > s.count("}"):
                        s += " }"
                    staff_string += s
                    if s_ind < len(sub_staff_strings) - 1:
                        staff_string += " \\\\"
                staff_string += " >>"
    return staff_string




def get_bar_no_from_time(time, bar_starts):
    for index, bar in enumerate(bar_starts[:-1]):
        if time >= bar and time < bar_starts[index + 1]:
            return index
    return len(bar_starts) - 1



def get_actions_from_staff(s):
    actions = []
    times = []
    ns = s.note_stream_without_holds
    for elem in ns:
        if type(elem) != list:
            if elem.start_time in times:
                add_index = times.index(elem.start_time)
                actions[add_index] += elem.notes
            else:
                if len(elem.notes) > 0:
                    actions.append(elem.notes)
                    times.append(elem.start_time)
        else:
            for sub_stream in elem:
                for sub_elem in sub_stream:
                    if sub_elem.start_time in times:
                        add_index = times.index(sub_elem.start_time)
                        actions[add_index] += sub_elem.notes
                    else:
                        if len(sub_elem.notes) > 0:
                            actions.append(sub_elem.notes)
                            times.append(sub_elem.start_time)
    ret = zip(times, actions)
    ret = sorted(ret, key = lambda x : x[0])
    return ret


def get_actions(staffs, staff_activations):
    staff_actions = []
    for staff_index, s in enumerate(staffs):
        if staff_activations[staff_index]:
            actions = get_actions_from_staff(s)
        else:
            actions = []
        staff_actions.append(actions)
    all_times = []
    all_staff_actions = []
    for actions in staff_actions:
        for time, _ in actions:
            if not time in all_times:
                all_times.append(time)
                all_staff_actions.append( [time, [ [] for i in range(len(staffs))] ] )
    for actions_index, actions in enumerate(staff_actions):
        for time, a in actions:
            add_index = all_times.index(time)
            all_staff_actions[add_index][1][actions_index] = a
    all_staff_actions = sorted(all_staff_actions, key = lambda x : x[0])
    return all_staff_actions



def main():
    options = options_creator.get_options()
    misc_helpers.delete_and_create_folder(options["output_folder_complete"])
    staffs = staff.get_staffs(options["lily_file"])
    misc_helpers.write_debug_file(staffs, options["output_folder_complete"])
    all_chord_symbols = chords.get_chords(options["lily_file"])


    index_containing_meta = 0 # index of the staff containing changes of measures and keys
    ref_staff = staffs[index_containing_meta]

    actions = get_actions(staffs, options["staff_activations"])

    note_positions = []
    print("Create pngs in " + options["output_folder_complete"])
    for step, action in enumerate(actions[0:]):
        time = action[0]
        action_notes = action[1]
        bar_no = get_bar_no_from_time(time, ref_staff.bar_starts)
        bar_start = ref_staff.bar_starts[bar_no]
        bar_end = ref_staff.bar_starts[bar_no + 1] if bar_no < len(ref_staff.bar_starts) - 1 else Fraction(99999999,1)

        key_changes = []
        for st in staffs:
            for c in st.key_changes:
                if not c in key_changes:
                    key_changes.append(c)
        key_changes.append( (Fraction(-999999999999,1), "c \\major") )
        key_changes = sorted(key_changes, key = lambda x : x[0])

        time_signature_changes = []
        for st in staffs:
            for c in st.time_signature_changes_strings:
                if not c in time_signature_changes:
                    time_signature_changes.append(c)
        time_signature_changes.append( (Fraction(-999999999999,1), "4/4") )
        time_signature_changes = sorted(time_signature_changes, key = lambda x : x[0])



        print_progress([("file", str(step)), ("bar", str(bar_no)), ("time", str(float(time)))])
        staff_strings = []
        mingus_notes = []
        chord_symbols = [c for c in all_chord_symbols if (c.time >= bar_start and c.time < bar_end) ]
        color_mode = "chord_root"
        for st_index, st in enumerate(staffs):
            current_notes = action_notes[st_index]
            staff_string = create_staff_string(bar_start, bar_end, time, current_notes, chord_symbols, st, st_index, options["staff_activations"][st_index], key_changes, time_signature_changes, color_mode)

            show_staffs = [True, True]
            if show_staffs[st_index]:
                staff_strings.append(staff_string)
                mingus_notes += staff_helpers.get_mingus_notes(current_notes)


        create_midi_notes_output(mingus_notes, options["output_folder_complete"])
        create_lily_output(step, staff_strings, chord_symbols, options["output_folder_complete"], options["image_resolution"])
        create_timing_info_output(time, options["output_folder_complete"])

        # make first image for presentation mode (only black notes)
        if step == 0:
            staff_strings = []
            for st_index, st in enumerate(staffs):
                color_mode = "all_black"
                staff_string = create_staff_string(bar_start, bar_end, time,
                            current_notes, chord_symbols, st, st_index,
                            options["staff_activations"][st_index], key_changes,
                            time_signature_changes, color_mode)
                show_staffs = [True, True]
                if show_staffs[st_index]:
                    staff_strings.append(staff_string)
            create_lily_output(0, staff_strings, chord_symbols, options["output_folder_complete"], options["image_resolution"], filename="presentation_mode_start")


    print("") # new line
    resize_images(options["output_folder_complete"], options["image_width"], options["image_height"])




if __name__ == '__main__':
    main()
