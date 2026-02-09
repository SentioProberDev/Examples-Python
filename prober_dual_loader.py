import time

from sentio_prober_control.Sentio.Enumerations import AutoFocusCmd, LoaderStation, OrientationMarker, DieNumber, \
    AutoAlignCmd, DieCompensationType, DieCompensationMode
from sentio_prober_control.Sentio.ProberSentio import *
from sentio_prober_control.Communication.CommunicatorTcpIp import *
import re

prober_ww = SentioProber(CommunicatorTcpIp.create("192.200.0.11:5500"))
prober_ww_max = SentioProber(CommunicatorTcpIp.create("127.0.0.1:35555"))
converyor = CommunicatorTcpIp.create("192.168.0.50:5555")

"""
The example for the Dual Loader + WW + WW-MAX ProberSentio
The converyor communication requires the '/r/n' as the end of line.
Which the program can exeucte on one of Prober system
"""

commands = {
    "Is Locked": "MG IsTRLKD",
    "Is at Right": "MG IsTRonR",
    "Is at Left": "MG IsTRonL",
    "Move Left": "XQ #TRAYtoL",
    "Move Right": "XQ #TRAYtoR"
}

def converyor_receive_paser(s: str) -> bool:
    """Convert string like '0.0000\n' or '1.0000\n' to boolean."""
    try:
        # print(f'Debug: {s}')
        match = re.search(r'[-+]?\d*\.?\d+', s)
        if not match:
            return False
        value = float(match.group())
        return value != 0.0
    except ValueError:
        return False

def converyor_query(s: str) -> bool:
    try:
        converyor.send(s)
        res = converyor_receive_paser(converyor.read_line())
        return res
    except ValueError:
        return False

def converyor_move(cmd_str: str) -> bool:
    try:
        if cmd_str == commands["Move Left"]:
            direction = "Left"
            check_sensor = commands["Is at Left"]
        elif cmd_str == commands["Move Right"]:
            direction = "Right"
            check_sensor = commands["Is at Right"]
        else:
            raise ValueError(f"Invalid move command: {cmd_str}")

        rep = converyor_query(commands["Is Locked"])
        if (rep):
            raise Exception("Tray is still locked.")

        if converyor_query(check_sensor):
            print(f"[Info] Tray is already at {direction}. Skipping move.")
            return True

        print(f"[Info] Moving tray to {direction}...")
        time.sleep(1)
        converyor.send(cmd_str)

        timeout = 30  # total 30 second
        interval = 1
        elapsed = 0

        while elapsed < timeout:
            time.sleep(interval)
            if converyor_query(check_sensor):
                print(f"[Success] Tray reached {direction}.")
                return True
            elapsed += interval

        raise TimeoutError(f"Tray did not reach {direction} within timeout.")
    except ValueError:
        return False


def converyor_cycling_testing():
    cnt = 0
    while (True):
        cnt = cnt + 1
        print(f"********Cycling:{cnt}*********")
        time.sleep(1)

        try:
            converyor_move(commands["Move Left"])
        except Exception as e:
            print("-----------{0}---------".format(e))
            print("-----------retry-Move Left---------")
            # converyor_move(commands["Move Left"])

        time.sleep(1)

        try:
            converyor_move(commands["Move Right"])
        except Exception as e:
            print("--------{0}---------".format(e))
            print("-----------retry-Move Right---------")
            # converyor_move(commands["Move Right"])

    # ----  Loader Max, transfer wafer from Cas1/25 to Aux, converyor to Left WW Loader, to PreAligner, to WW/4------ #

def load_wafer_from_max_to_ww():
    prober_ww_max.loader.transfer_wafer(LoaderStation.Cassette1,2, LoaderStation.Aux, 1)
    time.sleep(2)
    converyor_move(commands["Move Left"])
    time.sleep(2)
    prober_ww.loader.transfer_wafer(LoaderStation.Aux,1, LoaderStation.PreAligner, 1)
    prober_ww.loader.prealign(OrientationMarker.Notch,0)
    prober_ww.loader.transfer_wafer(LoaderStation.PreAligner,1, LoaderStation.WaferWallet, 5)

    # ----  Loader WW, transfer wafer from chuck to Aux, converyor to right WW-MAX Loader, to PreAligner, to Cas1/25------ #

def load_wafer_from_ww_to_max():
    prober_ww.loader.transfer_wafer(LoaderStation.WaferWallet,5, LoaderStation.PreAligner, 1)
    prober_ww.loader.prealign(OrientationMarker.Notch,0)
    prober_ww.loader.transfer_wafer(LoaderStation.PreAligner,1, LoaderStation.Aux, 1)
    time.sleep(2)
    converyor_move(commands["Move Right"])
    time.sleep(2)
    prober_ww_max.loader.transfer_wafer(LoaderStation.Aux,1, LoaderStation.PreAligner, 1)
    prober_ww_max.loader.prealign(OrientationMarker.Notch,0)
    prober_ww_max.loader.transfer_wafer(LoaderStation.PreAligner,1, LoaderStation.Cassette1, 25)

def checking_loader():
    has_ww = prober_ww.loader.has_station(LoaderStation.WaferWallet)
    has_ww_max = prober_ww_max.loader.has_station(LoaderStation.Cassette1)
    print(f"detect system------WW:{has_ww}, WWMAX:{has_ww_max}---------")

def ww_load_wafer_ww_to_chuck():
    prober_ww.loader.transfer_wafer(LoaderStation.WaferWallet,5, LoaderStation.PreAligner, 1)
    prober_ww.loader.prealign(OrientationMarker.Notch,0)
    prober_ww.loader.transfer_wafer(LoaderStation.PreAligner,1, LoaderStation.Chuck, 1)

def ww_load_wafer_chuck_to_max_chuck():
    print('ww_load_wafer_chuck_to_max_chuck')
    prober_ww.loader.transfer_wafer(LoaderStation.Chuck,1, LoaderStation.Aux, 1)
    time.sleep(2)
    converyor_move(commands["Move Right"])
    time.sleep(2)
    prober_ww_max.loader.transfer_wafer(LoaderStation.Aux,1, LoaderStation.PreAligner, 1)
    prober_ww_max.loader.prealign(OrientationMarker.Notch,0)
    prober_ww_max.loader.transfer_wafer(LoaderStation.PreAligner,1, LoaderStation.Chuck, 1)

def ww_max_load_wafer_chuck_to_ww_chuck():
    print('ww_max_load_wafer_chuck_to_ww_chuck')
    prober_ww_max.loader.transfer_wafer(LoaderStation.Chuck,1, LoaderStation.Aux, 1)
    time.sleep(2)
    converyor_move(commands["Move Left"])
    time.sleep(2)
    prober_ww.loader.transfer_wafer(LoaderStation.Aux,1, LoaderStation.PreAligner, 1)
    prober_ww.loader.prealign(OrientationMarker.Notch,0)
    prober_ww.loader.transfer_wafer(LoaderStation.PreAligner,1, LoaderStation.Chuck, 1)

def ww_max_load_wafer_cas1_to_ww_chuck():
    print('ww_max_load_wafer_cas1_to_ww_chuck')
    prober_ww_max.loader.transfer_wafer(LoaderStation.Cassette1,25, LoaderStation.Aux, 1)
    time.sleep(2)
    converyor_move(commands["Move Left"])
    time.sleep(2)
    prober_ww_max.loader.transfer_wafer(LoaderStation.Aux,1, LoaderStation.PreAligner, 1)
    prober_ww_max.loader.prealign(OrientationMarker.Notch,0)
    prober_ww_max.loader.transfer_wafer(LoaderStation.PreAligner,1, LoaderStation.Chuck, 1)

def ww_max_load_wafer_cassette():
    print('ww_max_load_wafer_cassette')
    prober_ww_max.loader.transfer_wafer(LoaderStation.Chuck,1, LoaderStation.Cassette1, 25)

def ww_max_unload_wafer_cassette():
    print('ww_max_unload_wafer_cassette')
    prober_ww_max.loader.transfer_wafer(LoaderStation.Chuck,1, LoaderStation.Cassette1, 2)

def ww_move_positioner_site_with_stepping():
    print('ww_move_positioner_site_with_stepping')
    prober_ww.move_chuck_separation()
    prober_ww.vision.auto_focus(AutoFocusCmd.GoTo)
    prober_ww.vision.auto_focus()
    #--get site num--
    resp = prober_ww.send_cmd('probe:NorthEast:get_site_num')
    num_site = int(resp.message())
    die_num = prober_ww.map.get_num_dies(DieNumber.Selected)
    resp = prober_ww.send_cmd('map:subsite:get_num')
    subsite_num = int(resp.message())

    #--all probe back to 0 site--(Home) --//
    # resp = prober_ww.send_cmd('probe:East:step_site 0')
    resp = prober_ww.send_cmd('probe:NorthEast:step_site 0')
    resp = prober_ww.send_cmd('probe:NorthWest:step_site 0')
    # resp = prober_ww.send_cmd('probe:West:step_site 0')
    resp = prober_ww.send_cmd('probe:SouthWest:step_site 0')
    resp = prober_ww.send_cmd('probe:SouthEast:step_site 0')

    #-- loop stepping--//
    for i in range(die_num):
        prober_ww.map.step_die_seq(i,0)
        resp = prober_ww.send_cmd('probe:East:move_contact')
        resp = prober_ww.send_cmd('probe:West:move_contact')

        resp = prober_ww.send_cmd('probe:NorthEast:move_contact')
        resp = prober_ww.send_cmd('probe:NorthWest:move_contact')
        resp = prober_ww.send_cmd('probe:SouthWest:move_contact')
        resp = prober_ww.send_cmd('probe:SouthEast:move_contact')
        prober_ww.move_chuck_contact()
        time.sleep(1)

        #----Positioner Site movement---
        resp = prober_ww.send_cmd('probe:East:move_separation')
        resp = prober_ww.send_cmd('probe:West:move_separation')

        for k in range(subsite_num-1):
            prober_ww.send_cmd(f'map:subsite:step {k+1}')

            for j in range(num_site):
                prober_ww.move_chuck_separation()
            #     resp = prober_ww.send_cmd(f'probe:East:step_site {j}')
                resp = prober_ww.send_cmd(f'probe:NorthEast:step_site {j}')
                resp = prober_ww.send_cmd(f'probe:NorthWest:step_site {j}')
            #     resp = prober_ww.send_cmd(f'probe:West:step_site {j}')
                resp = prober_ww.send_cmd(f'probe:SouthWest:step_site {j}')
                resp = prober_ww.send_cmd(f'probe:SouthEast:step_site {j}')
                prober_ww.move_chuck_contact()
                time.sleep(1)

def ww_prepare_wafer_by_project():
    print('ww_prepare_wafer_by_project')
    prober_ww.move_chuck_separation()
    prober_ww.move_chuck_home()

    prober_ww.vision.auto_focus(AutoFocusCmd.GoTo)
    prober_ww.vision.auto_focus()
    prober_ww.vision.align_wafer()
    prober_ww.vision.find_home()

def ww_max_prepare_wafer_by_project():
    print('ww_max_prepare_wafer_by_project')
    prober_ww_max.move_chuck_separation()
    prober_ww_max.move_chuck_home()

    prober_ww_max.move_chuck_work_area(WorkArea.Offaxis)
    prober_ww_max.vision.auto_focus()
    prober_ww_max.vision.align_wafer()
    prober_ww_max.vision.find_home()

    resp = prober_ww_max.vision.start_execute_compensation(DieCompensationType.Offaxis, DieCompensationMode.ProbeCard)
    prober_ww_max.wait_complete(resp.cmd_id(), 300)

    prober_ww_max.move_chuck_work_area(WorkArea.Probing)

def ww_max_stepping():
    print('ww_max_stepping')
    prober_ww_max.vision.auto_focus(AutoFocusCmd.GoTo)
    prober_ww_max.move_chuck_separation()
    prober_ww_max.vision.auto_focus()
    #--get site num--
    die_num = prober_ww_max.map.get_num_dies(DieNumber.Selected)

    #-- loop stepping--//
    for i in range(die_num):
        prober_ww_max.map.step_die_seq(i,0)
        prober_ww_max.move_chuck_contact()
        time.sleep(1)


def demo_script():
    #-- WW 5 - load wafer to the chuck
    ww_load_wafer_ww_to_chuck()

    #-- WW prepare wafer
    ww_prepare_wafer_by_project()

    #-- Stepping die
    ww_move_positioner_site_with_stepping()

    #-- Load wafer from WW chuck to MAX chuck
    ww_load_wafer_chuck_to_max_chuck()

    #--WW-MAX prepare wafer + PTPA
    ww_max_prepare_wafer_by_project()

    #--ww_max_Stepping--
    ww_max_stepping()

    # -- unload wafer to cassette1 --
    ww_max_unload_wafer_cassette()

def main():
    demo_script()
    load_wafer_from_max_to_ww()

if __name__ == "__main__":
    main()