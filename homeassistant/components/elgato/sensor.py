"""Support for Elgato sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ElgatoData, ElgatoDataUpdateCoordinator
from .entity import ElgatoEntity


@dataclass
class ElgatoEntityDescriptionMixin:
    """Mixin values for Elgato entities."""

    value_fn: Callable[[ElgatoData], float | int | None]


@dataclass
class ElgatoSensorEntityDescription(
    SensorEntityDescription, ElgatoEntityDescriptionMixin
):
    """Class describing Elgato sensor entities."""

    has_fn: Callable[[ElgatoData], bool] = lambda _: True


SENSORS = [
    ElgatoSensorEntityDescription(
        key="battery",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        has_fn=lambda x: x.battery is not None,
        value_fn=lambda x: x.battery.level if x.battery else None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Elgato sensor based on a config entry."""
    coordinator: ElgatoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        ElgatoSensorEntity(
            coordinator=coordinator,
            description=description,
        )
        for description in SENSORS
        if description.has_fn(coordinator.data)
    )


class ElgatoSensorEntity(ElgatoEntity, SensorEntity):
    """Representation of a Elgato sensor."""

    entity_description: ElgatoSensorEntityDescription

    def __init__(
        self,
        coordinator: ElgatoDataUpdateCoordinator,
        description: ElgatoSensorEntityDescription,
    ) -> None:
        """Initiate Elgato sensor."""
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.data.info.serial_number}_{description.key}"
        )

    @property
    def native_value(self) -> float | int | None:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
