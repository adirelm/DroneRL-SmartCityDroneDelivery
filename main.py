"""Entry point for the DroneRL application."""

from dronerl.gui import GUI
from dronerl.sdk import DroneRLSDK


def main():
    """Construct the SDK from config, then launch the GUI on top of it (§4.1)."""
    sdk = DroneRLSDK("config/config.yaml")
    gui = GUI(sdk=sdk)
    gui.run()


if __name__ == "__main__":
    main()
