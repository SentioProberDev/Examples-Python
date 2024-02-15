from sentio_prober_control.Sentio.ProberSentio import SentioProber
from sentio_prober_control.Sentio.Enumerations import ChuckThetaReference, ChuckSite, ChuckXYReference, Module


def main():
    prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")

    # Chuck Site Switch
    x, y, z, t = prober.move_chuck_site(ChuckSite.Wafer)
    print(f"absolute chuck position is x={x}; y={y}; z={z}; theta={t}°")

    # Chuck Theta Motion
    a = prober.move_chuck_theta(ChuckThetaReference.Relative, 1)
    print(f"chuck angle is {a}")

    # Obtain chuck site status information
    hasHome, hasContact, overtravelActive, vacuumOn = prober.get_chuck_site_status(ChuckSite.Wafer)

    prober.select_module(Module.Vision)

    # move chuck to home
    xhome, yhome = prober.move_chuck_home()

    # move chuck relative by 10, 20 µm
    for x in range(-10, 10):
        for y in range(-10, 10):
            # Move Reltive to home:
            prober.move_chuck_xy(ChuckXYReference.Home, 1000 * x, 1000 * y)

            # The same motion as an absolute Motion:
            #prober.move_chuck_xy(ChuckXYReference.Zero, xhome + 1000 * x, yhome + 1000 * y)


if __name__ == "__main__":
    main()