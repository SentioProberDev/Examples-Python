import time

from sentio_prober_control.Sentio.ProberSentio import *
from sentio_prober_control.Sentio.Enumerations import RemoteCommandError
from sentio_prober_control.Communication.CommunicatorTcpIp import CommunicatorTcpIp


def main():
    prober = SentioProber(CommunicatorTcpIp.create("127.0.0.1:35555"))

    buttons = prober.show_message("Are you Feeling Luky today?", DialogButtons.YesNo, "Question", 5)
    if buttons==DialogButtons.Yes:
        print("Operator is feeling lucky today!")
    else:
        print("Operator is not feeling lucky today!")

    # Display a basic hint in SENTIO
    # the hint will automatically close after a couple of seconds
    prober.show_hint("This is my message to you", "This is a rather unimportant subtext")
    time.sleep(3)

    # Display a hint with a button.
    # This is a way to interrupt the workflow from python and give the operator time to do 
    # something IRL.
    try:
        prober.show_hint_and_wait("Are we feeling excellent today?", "Go grab a coffee!", "Yes", 10, True)
        print(f"Great news everybody: Operator is feeleing excellent today!")
    except ProberException as e:
        if e.error()==RemoteCommandError.Timeout:
            print(f"Message timed out. Operator is not feeling excellent today! ({e})")
        else:
            raise e


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n#### Error ##################################")
        print(f"{e}")
