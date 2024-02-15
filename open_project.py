from sentio_prober_control.Sentio.ProberSentio import *
from sentio_prober_control.Communication.CommunicatorTcpIp import CommunicatorTcpIp


def main():
    prober = SentioProber(CommunicatorTcpIp.create("127.0.0.1:35555"))
    prober.open_project("sample_round")

    # do something...
    prober.map.set_index_size(3333, 4444)

    # save the modified project in Sentio's project folder
    #prober.save_project("my_project")

    # save the project under an absolute path
    prober.save_project("c:\\my_project")


if __name__ == "__main__":
    main()