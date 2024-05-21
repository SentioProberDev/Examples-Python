import time

from typing import List, Tuple
from sentio_prober_control.Sentio.ProberSentio import SentioProber
from sentio_prober_control.Sentio.Enumerations import *
from sentio_prober_control.Sentio.ProberBase import ProberException


def check_preconditions(prober : SentioProber) -> None:
    if not prober.has_chuck_xyz():
        raise Exception("This script requires a motorized chuck in order to run!")

    has_ww : bool = prober.loader.has_station(LoaderStation.WaferWallet)
    has_cas1 : bool = prober.loader.has_station(LoaderStation.Cassette1)
    has_cas2 : bool = prober.loader.has_station(LoaderStation.Cassette2)
    if not has_ww and not has_cas1 and not has_cas2:
        raise Exception("The probe station needs a wafer wallet or cassette to execute this script.")


# Filter out non-existing wafers from a wafer list
def filter_nonexisting(prober : SentioProber, wafer_list : List[Tuple[LoaderStation, int]]) -> List[Tuple[LoaderStation, int]]:
    out_list : List[Tuple[LoaderStation, int]] = []
    for loc in wafer_list:
        station, slot = loc

        stat : Tuple[LoaderStation, int, int, int, float] | None = prober.loader.query_wafer_status(station, slot)
        if stat is None:
            print(f"Wafer at {station} {slot} does not exist and will be ignored!.")
            continue

        out_list.append(loc)

    return out_list


def test_wafer(prober : SentioProber) -> None:
    print("Testing wafer...")

    prober.map.step_first_die()

    try:
        while True:
            col, row, site = prober.map.step_next_die()
            print(f'Testing cell {col}, {row} (Site: {site})')
    except ProberException as e:
        if e.error() != RemoteCommandError.EndOfRoute:
            raise


def set_and_wait_for_temperature(prober : SentioProber, temp : float, soak_time_sec : float) -> None:
    prober.status.set_chuck_temp(temp)

    # wait for temperature to stabilize
    while True:
        current_temp = prober.status.get_chuck_temp()
        setpoint = prober.status.get_chuck_temp_setpoint()
        if abs(current_temp - setpoint) < 0.5:
            break

        print(f"  - Waiting for temperature to reach set point: {current_temp} Setpoint: {setpoint}", end='\r')
        time.sleep(1)

    time_total = soak_time_sec
    time_step_sec = 1
    while time_total > 0:
        print(f"  - Waiting Soak time: {time_total} seconds remaining", end='\r')
        time_total -= time_step_sec
        time.sleep(time_step_sec)

    print("  - Soak time completed.")
    

def main() -> None:
    prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")

    # Check whether a loader station exists
    check_preconditions(prober)

    # SENTIO demo mode starts with a wafer on the chuck remove this wafer to the cassette 1
    #if prober.loader.query_wafer_status(LoaderStation.Chuck, 1) is not None:
    #prober.loader.transfer_wafer(LoaderStation.Chuck, 1, LoaderStation.Cassette1, 13)

    #===> Hier Kasettenstation oder WaferWallet auswaehlen
    originStation : LoaderStation = LoaderStation.WaferWallet
    prober.loader.scan_station(originStation)

    # Set up a list of wafers for processing
    #===> Hier zu testende Wafer auswaehlen
    wafer_list : List[Tuple[LoaderStation, int]] = []
    wafer_list.append((originStation, 5))
    wafer_list.append((originStation, 5))
#    wafer_list.append((originStation, 5))

    wafer_list = filter_nonexisting(prober, wafer_list)

    #===> Hier Projektnamen eingaben
    project_name : str = "PTPAOnAxis_Test"
    print(f"Loading project {project_name}")
    prober.open_project(project_name)
    
     #===> Hier projekt einstellen
    prealigner_angle = 0
    soak_time_sec = 60
    temperatures = [25, 40]

    for temp in temperatures:
        # Iterate over all wafers.
        for wafer_origin in wafer_list:
            station, slot = wafer_origin
            
            print(f"Loading wafer from {station} {slot}")
            prober.select_module(Module.Dashboard)
            prober.loader.load_wafer(station, slot, prealigner_angle)
            
            print(f"Setting and Waiting for temperature: {temp}")
            set_and_wait_for_temperature(prober, temp, soak_time_sec)

            # Here you could manually send commands to align the wafer, find home and so on. We won't do that here
            # because we will use Fast Track instead.
            #        prober.vision.align_wafer(AutoAlignCmd.UpdateDieSize)
            #        prober.vision.find_home()
    
            # Execute Fast Track. For this to work you must have set up Fast Track in the project.
            #   - Align Wafer
            #   - Find Home
            #   - Auto Focus
            #   - and possibly additional steps
            # Once this command is done. The wafer must be aligned, in focus and the a home position must have been set.
            prober.select_module(Module.Vision)
            resp = prober.vision.start_fast_track()
            prober.wait_complete(resp)

            prober.select_module(Module.Wafermap)
            test_wafer(prober)
            
            prober.select_module(Module.Dashboard)
            prober.loader.unload_wafer()
    
    set_and_wait_for_temperature(prober, 25, 0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n#### Error ##################################")
        print(f"{e}")