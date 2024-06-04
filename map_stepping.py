from sentio_prober_control.Sentio.ProberSentio import *
from sentio_prober_control.Sentio.Enumerations import Module, AxisOrient, ColorScheme, TestSelection, RoutingStartPoint, RoutingPriority, RemoteCommandError, ChuckSite
from sentio_prober_control.Communication.CommunicatorGpib import *
from sentio_prober_control.Communication.CommunicatorTcpIp import *


def main() -> None:

    try:
        #       Setup GPIB Communication
#        prober = SentioProber(CommunicatorGpib.create(GpibCardVendor.Adlink, "GPIB0:20"))

        #       Setup TCPIP Communication
        prober = SentioProber.create_prober(SentioCommunicationType.TcpIp, "127.0.0.1:35555")

        x, y, z, t = prober.move_chuck_site(ChuckSite.Wafer)
        print(f"absolute chuck position is x={x}; y={y}; z={z}; theta={t}°")

        hasHome, hasContact, overtravelActive, vacuumOn = prober.get_chuck_site_status(ChuckSite.Wafer)

        if not hasHome:
            raise Exception("Home position must be set to execute this script!")

        if not hasContact:
            raise Exception("Contact must be set for stepping!")

        prober.select_module(Module.Wafermap)

        # setup a wafermap
        prober.map.create(200)
        prober.map.set_flat_params(90, 50000)
        prober.map.set_grid_params(15000, 15000, 0, 0, 1000)
        prober.map.set_street_size(0, 0)
        prober.map.set_grid_origin(0, 0)
        prober.map.set_home_die(1, 1)
        prober.map.set_axis_orient(AxisOrient.UpRight)
        prober.map.set_color_scheme(ColorScheme.ColorFromBin)

        prober.map.bins.load("C:\\ProgramData\\MPI Corporation\\Sentio\\config\\defaults\\default_bins.xbt")

        # Write content of the binning table
        print(f"\r\nBinning Table:")
        num_bins : int = prober.map.bins.get_num_bins()
        for i in range(0, num_bins):
            idx, id, quality, color = prober.map.bins.get_bin_info(i)
            print(f"Bin index={idx}; quality={quality}; id={id}; color={color}")

        prober.map.bins.clear_all()

        prober.map.path.select_dies(TestSelection.All)
        prober.map.path.set_routing(RoutingStartPoint.UpperRight, RoutingPriority.ColBiDir)

        #
        # Stepping Loop
        #

        prober.map.step_first_die()
        bin_value = 0

        try:
            while True:
                col, row, site = prober.map.bin_step_next_die(bin_value)
                print(f'Position {col}, {row} (Site: {site})')

                # uncomment to use inker:
                # prober.set_ink(1)
        except ProberException as e:
            if e.error() != RemoteCommandError.EndOfRoute:
                raise

    except Exception as e:
        print("\n#### Error ##################################")
        print(e)


if __name__ == "__main__":
    main()