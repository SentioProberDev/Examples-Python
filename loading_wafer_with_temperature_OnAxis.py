from sentio_prober_control.Sentio.ProberSentio import *
from sentio_prober_control.Communication.CommunicatorTcpIp import CommunicatorTcpIp
import threading

import datetime
import time
import csv

# this script will execute wafer transfer to chuck with Target temperature #

_prober = SentioProber(CommunicatorTcpIp.create("127.0.0.1:35555"))

_test_folder_path = "D:\\Temperature_test\\"
_interval_wait_target_temp = 10 # seconds
_temperatures = [25, 150, -40, 25]
_wafer_slot = [1]
_cassette = LoaderStation.Cassette1
_re_setting_interval_in_soaking = 10  # min.
_contact_time = 600 # sec.
_test_dies_seq = [0, 1, 2, 3, 4]
_focus_data_file = r'{}'.format(_test_folder_path)
_debug = False
_tip_offset = [0, 0, 0]
_project_path = ['celadon_probe_card']
#
# main function
#
def main():
    # prepare_wafer_from_cassette()

    # looping for temperature
    for target_temp in _temperatures:

        prepare_test_folder(target_temp)

        # looping for wafer slot
        for slot in _wafer_slot:
            load_project(slot)

            precondition_check()

            # load_wafer_to_chuck(slot)

            wafer_pre_setting(True)

            chang_to_target_temperature(target_temp)

            soaking_processing(target_temp)

            wafer_setting_after_soaking()

            stepping(target_temp, slot)

            # unload_wafer()

def load_project(slot_number):
    _prober.open_project(_project_path[slot_number - 1], True)

def precondition_check():
    # check if home and contact is set
    hasHome, hasContact, overtravelActive, vacuumOn = _prober.get_chuck_site_status(ChuckSite.Wafer)
    if not hasHome: raise Exception("Home position must be set to execute this script!")
    if not hasContact: raise Exception("Contact must be set for stepping!")

    if not len(_wafer_slot) == len(_project_path):
        raise Exception("Please make sure the Project number and Slot number is correct")

def prepare_wafer_from_cassette():
    print('prepare_wafer_from_cassette')
    if _debug == False:
        # Scan cassette and verify the slot data
        ret = _prober.loader.scan_station(_cassette)
        for slot in _wafer_slot:
            if ret[25-slot] != '1':
                raise Exception("Slot: {0} is incorrect!".format(slot))

def load_wafer_to_chuck(slot):
    print(f'load_wafer_to_chuck:{slot}')
    if _debug == True:
        return
    # load wafer
    ret = _prober.loader.load_wafer(_cassette, slot, 0)

def wafer_pre_setting(is_move_chuck = False, is_execute_find_tips = False ):
    print('wafer_pre_setting')
    if _debug == True:
        return
    # switch Vision
    _prober.select_module(Module.Vision)

    # separation
    if is_move_chuck :
        contact, _, _, _ = _prober.get_chuck_site_height(ChuckSite.Wafer)
        _prober.move_chuck_z(ChuckZReference.Zero, contact - 500)

    # Move to Home
    _prober.move_chuck_home()

    # Get to Focus
    _prober.comm.send('step_scope_site clear_area')
    _prober.comm.read_line()
    _prober.vision.auto_focus(AutoFocusCmd.GoTo)
    scope_z =_prober.vision.auto_focus(AutoFocusCmd.Focus)
    print(f'AF:{scope_z}')
    _prober.comm.send('step_scope_site home')
    _prober.comm.read_line()

    # Auto Align with update die size
    _prober.vision.align_wafer(AutoAlignCmd.UpdateDieSize)

    # Find Home
    _prober.vision.find_home()

    if is_execute_find_tips :
        _tip_offset[0], _tip_offset[1], _tip_offset[2] = _prober.vision.ptpa_find_tips(PTPA_Find_Tips_Mode.OnAxis)


def chang_to_target_temperature(target_temperature):
    print(f'chang_to_target_temperature:{target_temperature}')
    if _debug == True:
        return
    # go to target temperature
    _prober.status.set_chuck_temp(target_temperature)
    current_temp = _prober.status.get_chuck_temp()
    isCooling, isHeating, isControlling, isStandby, isError, isUncontrolled = _prober.status.get_chuck_thermo_state()
    time.sleep(_interval_wait_target_temp)
    # waiting system at target temperature
    while isHeating or isCooling:
        # print current temp and status
        current_temp = _prober.status.get_chuck_temp()
        print(f"Current Temperature = {current_temp:.2f}")
        # check status
        isCooling, isHeating, isControlling, isStandby, isError, isUncontrolled = _prober.status.get_chuck_thermo_state()
        time.sleep(_interval_wait_target_temp)

def soaking_processing(target_temp):
    print(f'soaking_processing:{target_temp}')
    if _debug == False:
        soaking_time = _prober.status.get_soaking_time(target_temp)
    else:
        soaking_time = 10
    print(f'Target Temperature:{target_temp}, Soaking time: {soaking_time}')

    if soaking_time == 0:
        return

    # waiting system soaking time
    soaking_time = int(soaking_time)
    while soaking_time:
        mins, secs = divmod(soaking_time, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(f'Elapsed time:{timer}')
        time.sleep(1)

        if soaking_time % (_re_setting_interval_in_soaking * 60) == 0:
            prepare_wafer_in_soaking()

        soaking_time -= 1

def prepare_wafer_in_soaking():
    print('execute prepare wafer!')

    if _debug == False :
        wafer_pre_setting(False, True)

    # save Chuck Scope pos
    save_temperature_data()


def wafer_setting_after_soaking():
    print('wafer_setting_after_soaking')
    if _debug == False:
        wafer_pre_setting()

        # Topography - Synchronize command
        _prober.comm.send('step_scope_site topo')
        _prober.comm.read_line()
        cmd_id = _prober.map.execute_topogrphy(ExecuteAction.Execute)
        _prober.wait_complete(cmd_id, 3600)
        _prober.comm.send('step_scope_site home')
        _prober.comm.read_line()

def stepping(target_temp, slot):
    print('Stepping for dies')
    # _prober.map.step_first_die()

    for die_sqe in _test_dies_seq:

        # col, row ,sub_index =_prober.map.step_die_seq(die_sqe, 0)
        # _prober.move_chuck_contact()

        # save image
        # now = datetime.datetime.now()
        # fn = f"{_test_folder}\Slot_{slot}_Die_Seq_{die_sqe}_col_{col}_row_{row} @ {target_temp}°C in {now.strftime('%Y-%m-%d %H-%M-%S')}.png"
        # _prober.vision.snap_image(fn)

        # Contact looping
        recoder_contact_separation_condition(target_temp, slot, die_sqe)

    _prober.move_chuck_home()

def unload_wafer():
    print('unload_wafer')
    if _debug == False:
        _prober.loader.unlaod_wafer()

def prepare_test_folder(target_temp):
    folder: str = r'{}'.format(_test_folder_path)
    if not os.path.exists(folder):
        os.mkdir(folder)

    global _test_folder
    _test_folder = r'{}\{}'.format(_test_folder_path, f'{target_temp}_degree_test')
    if os.path.isdir(_test_folder):
        _test_folder = r'{}\{}'.format(_test_folder_path, f'{target_temp}_1_degree_test')
        # shutil.rmtree(_test_folder)
        os.mkdir(_test_folder)
        time.sleep(1)
    else:
        os.mkdir(_test_folder)

    global _focus_data_csv_file
    _focus_data_csv_file = r'{}\{}.csv'.format(_test_folder, "Temperature Data")
    condition = ['Time', 'ScopePosX', 'ScopePosY', 'ScopePosZ', 'ChuckPosX', 'ChuckPosY', 'ChuckPosZ', 'TipOffsetX', 'TipOffsetY', 'TipOffsetZ', 'DieSizeX', 'DieSizeY']

    with open(_focus_data_csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(condition)
        file.flush()

def recoder_contact_separation_condition(target_temp, slot, die_sqe):
    print('recoder_contact_separation_condition')

    col, row, sub_index = _prober.map.step_die_seq(die_sqe, 0)

    for i in range(3):
        _prober.move_chuck_separation()
        _prober.vision.auto_focus()
        cur_z = _prober.get_chuck_z(ChuckZReference.Zero)
        now = datetime.datetime.now()
        fn = f"{_test_folder}\Slot_{slot}_Die_Seq_{die_sqe}_col_{col}_row_{row}_Contact_Cycle_{i}_Separation_{cur_z} @ {target_temp}°C in {now.strftime('%Y-%m-%d %H-%M-%S')}.png"
        _prober.vision.snap_image(fn)

        _prober.move_chuck_contact()
        _prober.vision.auto_focus()
        cur_z = _prober.get_chuck_z(ChuckZReference.Zero)
        now = datetime.datetime.now()
        fn = f"{_test_folder}\Slot_{slot}_Die_Seq_{die_sqe}_col_{col}_row_{row}_Contact_Cycle_{i}_Contact_{cur_z} @ {target_temp}°C in {now.strftime('%Y-%m-%d %H-%M-%S')}.png"
        _prober.vision.snap_image(fn)

        time.sleep(_contact_time)

    _prober.move_chuck_separation()

    # Capture image for Tips -- Not yet done
    _prober.move_chuck_contact()
    _prober.vision.auto_focus()
    _prober.vision.enable_follow_mode(False)

    _prober.move_chuck_separation()
    time.sleep(3)

    now = datetime.datetime.now()
    fn = f"{_test_folder}\Slot_{slot}_Tip image_Die_Seq_{die_sqe}_col_{col}_row_{row} @ {target_temp}°C in {now.strftime('%Y-%m-%d %H-%M-%S')}.png"
    _prober.vision.snap_image(fn)

    _prober.move_chuck_contact()

    _prober.vision.enable_follow_mode(True)

    _prober.move_chuck_separation()



def save_temperature_data():
    now = datetime.datetime.now()
    scope_z_pos = _prober.get_scope_z()
    scope_x_pos, scope_y_pos= _prober.get_scope_xy()
    chuck_z_pos = _prober.get_chuck_z(ChuckZReference.Zero)
    chuck_x_pos, chuck_y_pos = _prober.get_chuck_xy_pos()

    _prober.comm.send("map:get_prop die_size")
    resp = Response.check_resp(_prober.comm.read_line())
    tok = resp.message().split(",")
    die_size_x = tok[0]
    die_size_y = tok[1]

    data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    with open(_focus_data_csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        data[0] = now
        data[1] = scope_x_pos
        data[2] = scope_y_pos
        data[3] = scope_z_pos

        data[4] = chuck_x_pos
        data[5] = chuck_y_pos
        data[6] = chuck_z_pos

        data[7] = _tip_offset[0]
        data[8] = _tip_offset[1]
        data[9] = _tip_offset[2]

        data[10] = die_size_x
        data[11] = die_size_y
        writer.writerow(data)
        file.flush()

if __name__ == "__main__":
    try:
        main()
        _prober.comm.send("*LOCAL")
        now = datetime.datetime.now()
        print(f'{now}, Processing Finish')
    except Exception as e:
        _prober.comm.send("*LOCAL")
        print(e)