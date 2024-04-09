from typing import List, Tuple
import time

from sentio_prober_control.Sentio.ProberBase import ProberException
from sentio_prober_control.Sentio.ProberSentio import SentioProber
from sentio_prober_control.Sentio.Enumerations import LoaderStation, Module, RemoteCommandError, VirtualCarrierInitFlags, VirtualCarrierStepProcessingState


def process_wafer(step_info : Tuple[VirtualCarrierStepProcessingState, str, LoaderStation, int, float, int]) -> None:
    stat, id, station, slot, temp, pidx = step_info
    print(f"Processing Step: {stat}, {id}, {station}, {slot}, {temp}, {pidx}")
    time.sleep(2)


def main() -> None:
    prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")
    prober.select_module(Module.Loader, "Loader")

    # SENTIO demo mode starts with a wafer on the chuck remove this wafer to the cassette 1
    if prober.has_wafer(LoaderStation.Chuck, 1):
        prober.loader.transfer_wafer(LoaderStation.Chuck, 1, LoaderStation.Cassette1, 13)

    carrier_list : List[str] = prober.loader.vc.list()
    steps = prober.loader.vc.initialize(carrier_list[0], VirtualCarrierInitFlags.Start)
    
    # print processing steps for documentation purposes
    for i in range(len(steps)):
        stat, id, station, slot, temp, pidx = steps[i]
        print(f"  {i} - {stat}, {id}, {station}, {slot}, {temp}, {pidx}")

    try:
        while True:
            step_info = prober.loader.vc.next_step()
            process_wafer(step_info)
    except ProberException as e:
        if e.error() != RemoteCommandError.EndOfList:
            raise

    print("All wafers processed.")

if __name__ == "__main__":
    main()
