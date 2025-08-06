from sentio_prober_control.Sentio.ProberSentio import SentioProber, ProberException
from sentio_prober_control.Sentio.Enumerations import ChuckSite, RemoteCommandError

def main() -> None:
    prober = SentioProber.create_prober("tcpip", "127.0.0.1:35555")

    # How many chuck sites does the system have?
    i : int = prober.get_chuck_site_count()

    # Iterate over all chuck sites and print their status
    for i in range(i):
        cs : ChuckSite = ChuckSite(i)
        hasHome, hasContact, overtravelActive, vacuumOn = prober.get_chuck_site_status(cs)
        print(f"ChuckSite {cs}: hasHome={hasHome}, hasContact={hasContact}, overtravelActive={overtravelActive}, vacuumOn={vacuumOn}")

        # Move to the chuck site
        prober.move_chuck_site(cs)
        actualSite : ChuckSite = prober.get_chuck_site_name()
        print(f"  - Chuck moved to {actualSite}")
        
        # Let east probe step over all sites
        num : int = prober.probe.east.get_site_num()
        if num==0:
            print(f"  - No sites for probe east on {cs} defined!")
            continue
        else:
            try:
                prober.probe.east.step_site_first()
                while True:
                    id , x, y = prober.probe.east.step_site_next()
                    print(f"  - Stepped to {id} at x={x}, y={y} on {cs}")
            except ProberException as e:
                if e.error() != RemoteCommandError.EndOfRoute:
                    raise

if __name__ == "__main__":
    main()