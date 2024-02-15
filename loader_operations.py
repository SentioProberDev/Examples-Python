from sentio_prober_control.Sentio.ProberSentio import SentioProber
from sentio_prober_control.Sentio.Enumerations import LoaderStation, OrientationMarker


def main() -> None:
    prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")

    #
    # Check whether a loader station exists
    #

    stat = prober.loader.has_station(LoaderStation.WaferWallet)
    if stat:
        print("Station has a Wafer Wallet")

    stat = prober.loader.has_station(LoaderStation.Cassette1)
    if stat:
        print("Station has a Cassette Station 1")

    stat = prober.loader.has_station(LoaderStation.Cassette2)
    if stat:
        print("Station has a Cassette Station 2")

    #
    # Scan the content of a loader station
    #

    slots = prober.loader.scan_station(LoaderStation.Cassette1)
    first_occupied_slot = None
    for i in range(0, len(slots)):
        if (slots[i]=='0'):
            print(f"Slot {i + 1}: Empty")
        elif (slots[i]=='1'):
            print(f"Slot {i + 1}: Occupied")
            if (first_occupied_slot is None):
                first_occupied_slot = i
        else:
            print(f"Slot {i + 1}: ERROR")

    #
    # Move a wafer from the Cassette to the prealigner
    #

    if (not first_occupied_slot is None):
        # mind you: slots are 1 based!
        prober.loader.transfer_wafer(LoaderStation.Cassette1, first_occupied_slot + 1, LoaderStation.PreAligner, 1)

        # prealign the wafer
        prober.loader.prealign(OrientationMarker.Notch, 180)


if __name__ == "__main__":
    main()