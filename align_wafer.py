import os

from sentio_prober_control.Sentio.ProberSentio import SentioProber
from sentio_prober_control.Sentio.Enumerations import Module, AutoFocusCmd, AutoAlignCmd, ChuckSite


def main():
    prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")
    prober.select_module(Module.Wafermap)

    # open a project
    # - must have contact height set
    # - must have a home position set
    # - align_wafer must be set up properly
    # - focus height should be set in the project

    project = os.path.dirname(os.path.abspath(__file__)) + "\\projects\\sample_align"
    prober.open_project(project)
    prober.select_module(Module.Vision)

    x, y = prober.move_chuck_home()
    print(f"Chuck at home position (x={x}, y={y} um)")

    z = prober.move_chuck_separation()
    print(f"Chuck at separation (z={z} um)")

    # bring scope down to the old focus height. This is probably close to focus,
    # but may not exactly be the focus height
    prober.vision.auto_focus(AutoFocusCmd.GoTo)

    # Do an autofocus. This will perform a focus scan and determine the best focus position
    prober.vision.auto_focus(AutoFocusCmd.Focus)

    # perform wafer alignment
    prober.vision.align_wafer(AutoAlignCmd.AutoDieSize)

    home, contact, overtravel, vacuum = prober.get_chuck_site_status(ChuckSite.Wafer)

    t = prober.get_chuck_theta(ChuckSite.Wafer)
    print(f"Chuck alignment angle is {t} Deg")


if __name__ == "__main__":
    main()