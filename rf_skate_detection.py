from sentio_prober_control.Sentio.ProberSentio import *
from sentio_prober_control.Communication.CommunicatorTcpIp import CommunicatorTcpIp
import threading

import datetime
import time
import csv

_prober = SentioProber(CommunicatorTcpIp.create("127.0.0.1:35555"))
_test_dies_seq = [400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412]
_debug = False

#
# main function
#
def main():
    contact_cnt = 0
    check_drift_time = 5
    execute_clean_pad = True
    die_num = _prober.map.get_num_dies(DieNumber.Selected)

    for die_sqe in range(die_num):
        col, row ,sub_index =_prober.map.step_die_seq(die_sqe, 0)

        _prober.move_chuck_contact()
        # Measurement ----
        contact_cnt = contact_cnt + 1

        if contact_cnt == check_drift_time:
            contact_cnt = 0
            ret = _prober.qalibria.verify_calibration_drift()

            if (ret == 'Failed'):
                if (execute_clean_pad):
                    _prober.aux.start_clean()

                _prober.move_chuck_site(ChuckSite.AuxLeft)
                _prober.qalibria.start_calibration()

                _prober.qalibria.set_calibration_drift_probe12()


if __name__ == "__main__":
    try:
        main()
        _prober.comm.send("*LOCAL")
        now = datetime.datetime.now()
        print(f'{now}, Processing Finish')
    except Exception as e:
        _prober.comm.send("*LOCAL")
        print(e)