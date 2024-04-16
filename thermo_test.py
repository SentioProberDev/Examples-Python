from typing import List, Tuple
from sentio_prober_control.Sentio.ProberSentio import SentioProber
from sentio_prober_control.Sentio.Enumerations import LoaderStation, Module, RemoteCommandError, ChuckSite, AutoAlignCmd
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


def main() -> None:
    prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")

    # Check whether a loader station exists
    check_preconditions(prober)

    # SENTIO demo mode starts with a wafer on the chuck remove this wafer to the cassette 1
    #if prober.loader.query_wafer_status(LoaderStation.Chuck, 1) is not None:
    #    prober.loader.transfer_wafer(LoaderStation.Chuck, 1, LoaderStation.Cassette1, 13)

    # Scan the station
    originStation : LoaderStation = LoaderStation.WaferWallet
    prober.loader.scan_station(originStation)

    # Set up a list of wafers for processing
    wafer_list : List[Tuple[LoaderStation, int]] = []
    wafer_list.append((originStation, 5))
    wafer_list.append((originStation, 5))
#    wafer_list.append((originStation, 2))
#    wafer_list.append((originStation, 3))
#    wafer_list.append((originStation, 4))
#    wafer_list.append((originStation, 5))
#    wafer_list.append((originStation, 6))
#    wafer_list.append((originStation, 7))
#    wafer_list.append((originStation, 8))
#    wafer_list.append((originStation, 9))
#    wafer_list.append((originStation, 10))
#    wafer_list.append((originStation, 11))
#    wafer_list.append((originStation, 12))
#    wafer_list.append((originStation, 13))
#    wafer_list.append((originStation, 14))
#    wafer_list.append((originStation, 15))
    wafer_list = filter_nonexisting(prober, wafer_list)

    restoreContactHeights : bool = True
    prober.open_project("handling_test", restoreContactHeights)
    hasHome, hasContact, _, _ = prober.get_chuck_site_status(ChuckSite.Wafer)
    if not hasContact:
        raise Exception("A project with a defined contact height is required.")
    
    # Iterate over all wafers.
    for wafer_origin in wafer_list:
        station, slot = wafer_origin
        print(f"Processing wafer at {station} {slot}")

        prober.loader.load_wafer(station, slot)
#        prober.vision.align_wafer(AutoAlignCmd.UpdateDieSize)
#        prober.vision.find_home()
        resp = prober.vision.start_fast_track()
        prober.wait_complete(resp)

        test_wafer(prober)
        
        prober.loader.unload_wafer()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n#### Error ##################################")
        print(f"{e}")