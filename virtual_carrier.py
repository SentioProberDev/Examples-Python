from typing import List, Tuple
import time

from sentio_prober_control.Sentio.ProberBase import ProberException
from sentio_prober_control.Sentio.ProberSentio import SentioProber
from sentio_prober_control.Sentio.Enumerations import WaferStatusItem, LoaderStation, Module, RemoteCommandError, VirtualCarrierInitFlags, VirtualCarrierStepProcessingState


def process_wafer(prober : SentioProber, step_info : Tuple[VirtualCarrierStepProcessingState, str, LoaderStation, int, float, int]) -> None:
    stat, id, station, slot, temp, pidx = step_info
    print(f"Wafer Processing: {stat}, {id}, {station}, {slot}, {temp}, {pidx}")
    prober.loader.set_wafer_status(station, slot, WaferStatusItem.Progress, 100)
    time.sleep(2)


def main() -> None:
    prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")
    prober.select_module(Module.Loader, "Loader")

    carrier_list : List[str] = prober.loader.vc.list()
    
    # print available virtual carriers for documentation purposes
    print(f"Available Virtual Carriers:")
    for i in range(len(carrier_list)):
        print(f"  {i} - \"{carrier_list[i]}\"")

    # select the first virtual carrier in the list and start processing
    steps = prober.loader.vc.initialize(carrier_list[0], VirtualCarrierInitFlags.Continue)
    
    # print processing steps for documentation purposes
    print(f"\r\nProcessing steps of Virtual Carrier \"{carrier_list[0]}\":")
    for i in range(len(steps)):
        stat, id, station, slot, temp, pidx = steps[i]
        print(f"  {i} - {stat}, {id}, {station}, {slot}, {temp}, {pidx}")

    try:
        while True:
            # Iterate over all processing steps. This command will also iterate
            # over the processing steps if the processing state is 
            # VirtualCarrierStepProcessingState.Skip but it will not do anything
            # in that case.
            step_info = prober.loader.vc.next_step()
            
            # At this point SENTIO should have executed the processing step.
            # The wafer should be aligned and at the chuck. You could now
            # do your own wafer processing but you probably want to check 
            # if the processing state is not VirtualCarrierStepProcessingState.Skip:
            if step_info[0] == VirtualCarrierStepProcessingState.Skip:
                print("Skipping processing step.")
            else:
                process_wafer(prober, step_info)
                
    except ProberException as e:
        if e.error() != RemoteCommandError.EndOfList:
            raise

    finally:
        # This call will make sure to save the state of the selected virtual carrier
        prober.loader.vc.save_state()

    print("All wafers processed.")

if __name__ == "__main__":
    main()
