"""Tests for the Xtherma switch platform."""

from unittest.mock import patch

import pytest
from homeassistant.components.switch import (
    SwitchEntity,
)
from homeassistant.const import Platform
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import snapshot_platform

from custom_components.xtherma_fp.xtherma_client_common import XthermaReadOnlyError
from tests.helpers import (
    get_switch_platform,
    provide_modbus_data,
    provide_rest_data,
)

from .conftest import init_integration, init_modbus_integration

SWITCH_ENTITY_ID_450 = "switch.test_entry_xtherma_config_cooling_curve_2_active"
SWITCH_ENTITY_ID_MODBUS_450 = (
    "switch.test_entry_xtherma_modbus_config_cooling_curve_2_active"
)
SWITCH_ENTITY_ID_MODBUS_350 = (
    "switch.test_entry_xtherma_modbus_config_cooling_curve_1_active"
)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_setup_switch_rest_api(
    hass, entity_registry, snapshot, mock_rest_api_client
) -> None:
    """Test the setup of switch platform using REST API."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.SWITCH]):
        entry = await init_integration(hass, mock_rest_api_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_setup_select_modbus_tcp(
    hass, entity_registry, snapshot, mock_modbus_tcp_client
) -> None:
    """Test the setup of switch platform using MODBUS TCP."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.SWITCH]):
        entry = await init_modbus_integration(hass, mock_modbus_tcp_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_binary_switch_icon(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)
    platform = get_switch_platform(hass)
    entity = platform.entities.get(SWITCH_ENTITY_ID_450)
    assert entity is not None
    assert entity.icon == "mdi:snowflake"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_set_switch_rest(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)
    platform = get_switch_platform(hass)
    state = hass.states.get(SWITCH_ENTITY_ID_450)
    assert state.state == "on"
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SwitchEntity)
    # init_integration uses REST-API, which cannot write
    with pytest.raises(HomeAssistantError) as exc_info:
        await entity.async_turn_off()
    assert isinstance(exc_info.value.__cause__, XthermaReadOnlyError)


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    provide_modbus_data(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
async def test_set_switch_modbus(hass, mock_modbus_tcp_client):
    await init_modbus_integration(hass, mock_modbus_tcp_client)
    platform = get_switch_platform(hass)
    state = hass.states.get(SWITCH_ENTITY_ID_MODBUS_450)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SwitchEntity)
    await entity.async_turn_off()
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 40
    assert kwargs["value"] == 0
    assert kwargs["slave"] == 1
    await entity.async_turn_on()


@pytest.mark.parametrize(
    "mock_modbus_tcp_client",  # This refers to the fixture
    provide_modbus_data(),
    indirect=True,  # This tells pytest to pass the parameter to the fixture
)
async def test_set_multiple_switches_modbus(hass, mock_modbus_tcp_client):
    await init_modbus_integration(hass, mock_modbus_tcp_client)
    platform = get_switch_platform(hass)
    state = hass.states.get(SWITCH_ENTITY_ID_MODBUS_450)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SwitchEntity)
    await entity.async_turn_off()
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 40
    assert kwargs["value"] == 0
    assert kwargs["slave"] == 1
    await entity.async_turn_on()
    state = hass.states.get(SWITCH_ENTITY_ID_MODBUS_350)
    entity = platform.entities.get(state.entity_id)
    assert entity is not None
    assert isinstance(entity, SwitchEntity)
    await entity.async_turn_off()
    kwargs = mock_modbus_tcp_client.write_register.call_args.kwargs
    # verify arguments passed to write_register()
    assert kwargs["address"] == 20
    assert kwargs["value"] == 0
    assert kwargs["slave"] == 1
    await entity.async_turn_on()
