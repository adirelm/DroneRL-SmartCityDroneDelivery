"""Entry point for the DroneRL application."""

from src.config_loader import Config, load_config
from src.gui import GUI


def main():
    """Load configuration and launch the GUI."""
    raw_config = load_config("config/config.yaml")
    config = Config(raw_config)
    gui = GUI(config)
    gui.run()


if __name__ == "__main__":
    main()
