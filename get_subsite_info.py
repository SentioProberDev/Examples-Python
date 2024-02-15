from sentio_prober_control.Sentio.ProberSentio import SentioProber
from sentio_prober_control.Sentio.Enumerations import AxisOrient
from sentio_prober_control.Communication.CommunicatorBase import CommunicatorBase
from sentio_prober_control.Communication.CommunicatorGpib import *
from sentio_prober_control.Communication.CommunicatorTcpIp import *


def main() -> None:
    CommunicatorBase._verbose = False
    prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")

    num = prober.map.subsites.get_num()
    print(f"Number of subsites: {num}")

    for i in range(0, num):
        desc, x, y = prober.map.subsites.get(i)
        print(f"Subsite {i}: desc={desc}, x={x}, y={y}")

if __name__ == "__main__":
    main()