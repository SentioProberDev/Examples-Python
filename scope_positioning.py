from sentio_prober_control.Sentio.ProberSentio import *
from sentio_prober_control.Communication.CommunicatorTcpIp import CommunicatorTcpIp


def main() -> None:
    prober = SentioProber(CommunicatorTcpIp.create("127.0.0.1:35555"))

    has_scope_xyz: bool = prober.has_scope_xyz()
    print(f"Has scope xyz {has_scope_xyz}")

    has_scope_z: bool = prober.has_scope_z()
    print(f"Has scope z {has_scope_z}")

    # move chuck relative by 10, 20 µm
    for x in range(-5, 5):
        for y in range(-5, 5):
            pos_x, pos_y = prober.move_scope_xy(ScopeXYReference.Relative, 100 * x, 100 * y)
            print(f"move_scope_xy return is {pos_x}, {pos_y}")

            # query scope position without moving
            pos_x, pos_y = prober.get_scope_xy()
            print(f"get_scope_xy return is {pos_x}, {pos_y}\n")


if __name__ == "__main__":
    main()