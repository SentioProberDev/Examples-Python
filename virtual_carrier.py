from typing import List
from alive_progress import alive_bar
import time

from sentio_prober_control.Sentio.ProberBase import ProberException
from sentio_prober_control.Sentio.ProberSentio import SentioProber
from sentio_prober_control.Sentio.Response import Response
from sentio_prober_control.Sentio.Enumerations import LoaderStation, Module, RemoteCommandError


def process_wafer() -> None:
    with alive_bar(monitor=None, stats=None, title="Processing Wafer..."):
        time.sleep(2)


def main() -> None:
    prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")

    prober.select_module(Module.Loader, "Loader")

    # SENTIO demo mode starts with a wafer on the chuck remove this wafer to the cassette 1
    with alive_bar(monitor=None, stats=None, title="Removing wafer from chuck..."):
        prober.loader.transfer_wafer(LoaderStation.Chuck, 1, LoaderStation.Cassette1, 13)

    carrier_list : List[str] = prober.loader.vc.list()
    if len(carrier_list) == 0:
        raise Exception("No virtual carriers found.")

    print("Available virtual carrieres:")
    for carrier in carrier_list:
        print(f'  - {carrier}')

    # select the first virtual carrier
    prober.loader.vc.select(carrier_list[0])

    # measure all wafers in the virtual carrier
    with alive_bar(monitor=None, stats=None, title="Loading wafer..."):
        prober.loader.vc.load_first()
    
    process_wafer()

    try:
        # Loop forever. The loader will throw an exception when the end of the list is reached.
        while True:
            with alive_bar(monitor=None, stats=None, title="Loading next wafer..."):
                prober.loader.vc.load_next()

            process_wafer()
    except ProberException as e:
        if e.error() != RemoteCommandError.EndOfList:
            raise

    print("All wafers processed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")