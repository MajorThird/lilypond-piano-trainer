import create_options
import staff
import misc_helpers
import chords


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
    options = create_options.get_options()
    misc_helpers.delete_and_create_folder(options["output_folder_complete"])
    staffs = staff.get_staffs(options["lily_file"])
    misc_helpers.write_debug_file(staffs, options["output_folder_complete"])
    all_chord_symbols = chords.get_chords(options["lily_file"])


    index_containing_meta = 0 # changes of measures and keys
    ref_staff = staffs[index_containing_meta]


    actions = get_actions(staffs, options["staff_activations"])


if __name__ == '__main__':
    main()
