from sentio_prober_control.Sentio.ProberSentio import SentioProber
from sentio_prober_control.Sentio.Enumerations import Module, AxisOrient, ColorScheme, TestSelection, BinSelection, DieNumber


def main():

    try:
        prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")

        prober.select_module(Module.Wafermap)

        # setup a wafermap
        map = prober.map
        map.create(200)

        map.set_flat_params(180, 50000)
        map.set_grid_params(5000, 5000, 0, 0, 4000)
        map.set_street_size(0, 0)
        map.set_axis_orient(AxisOrient.UpRight)
        map.set_grid_origin(1, 2)
        map.set_home_die(0, 0)
        map.set_color_scheme(ColorScheme.ColorFromBin)

        map.path.select_dies(TestSelection.All)
        map.bins.set_all(3, BinSelection.All)
        map.bins.load("C:\ProgramData\MPI Corporation\Sentio\config\defaults\default_bins.xbt")

        # output content of the binning table
        num_bins = map.bins.get_num_bins()
        print(f"Number of bins in the binning table is {num_bins}")
        for i in range(num_bins):
            (val, des, quality, color) = map.bins.get_bin_info(i)
            print(f"Bin {val}: {des}, {quality}, {color}")

        # add and remove some dies
        for i in range(1,4):
            for j in range(1, 5):
                map.die.remove(4+i, 4+j)
                map.die.remove(-10+i, 4+j)

        for i in range(-7, 7):
            if abs(i) > 6:
                map.die.remove(i, -8)
            elif abs(i) > 4:
                map.die.remove(i, -9)
            else:
                map.die.remove(i, -10)

        # read map data
        print(f"Wafermap diameter: {map.get_diameter()} mm")
        print(f"Grid axis orientation: {map.get_axis_orient()}")
        print(f"Grid origin: {map.get_grid_origin()}")
        print(f"Index size: {map.get_index_size()}")
        print(f"Street Size: {map.get_street_size()}")
        print(f"present dies: {map.get_num_dies(DieNumber.Present)}")
        print(f"Selected dies: {map.get_num_dies(DieNumber.Selected)}")
    except Exception as e:
        print("\n#### Error ##################################")
        print(f"{e}")

if __name__ == "__main__":
    main()