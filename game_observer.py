
from abc import ABC, abstractmethod


class Subject(ABC):
    """Pub interface for managing subscribers."""

    @abstractmethod
    def attach(self, observer) -> None:
        """Attach an observer to the subject."""
        pass

    @abstractmethod
    def detach(self, observer) -> None:
        """Detach an observer from the subject."""
        pass

    @abstractmethod
    def notify(self) -> None:
        """Notify all observers about an event."""
        pass


class GameObserver(ABC):
    """Interface for the game observers."""
    @abstractmethod
    def update_dev_cards(self, cards_count, current_time):
        """Updates the development cards and current game time."""
        pass

    @abstractmethod
    def update_tile_count(self, indoor_count, outdoor_count):
        """Updates the indoor and outdoor tile counts."""
        pass

    @abstractmethod
    def update_player_info(self, health, attack, items, location):
        """Updates the player stats and location."""
        pass
