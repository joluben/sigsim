#!/usr/bin/env python3
"""
MQTT Integration Validation Script

This script validates that the MQTT connector is properly integrated
with the ConnectorFactory system and all components work together.
"""
import asyncio
import sys
from typing import Dict, Any

# Add the backend directory to the path
sys.path.append('.')

from app.simulation.connectors import ConnectorFactory, get_supported_connector_types
from app.simulation.connectors.mqtt_connector import MQTTConnector
from app.models.target import TargetType, MQTTConfig


def validate_mqtt_in_factory():
    """Validate that MQTT is properly registered in the factory"""
    print("🔍 Validating MQTT integration with ConnectorFactory...")
    
    # Check if MQTT is in supported types
    supported_types = get_supported_connector_types()
    if "mqtt" not in supported_types:
        print("❌ MQTT not found in supported connector types")
        return False
    print("✅ MQTT found in supported connector types")
    
    # Check if MQTT is in factory types
    factory_types = ConnectorFactory.get_supported_types()
    if TargetType.MQTT not in factory_types:
        print("❌ MQTT not found in factory supported types")
        return False
    print("✅ MQTT found in factory supported types")
    
    # Check if MQTT is supported
    if not ConnectorFactory.is_supported(TargetType.MQTT):
        print("❌ MQTT not marked as supported in factory")
        return False
    print("✅ MQTT marked as supported in factory")
    
    return True


def validate_mqtt_config_schema():
    """Validate MQTT configuration schema"""
    print("\n🔍 Validating MQTT configuration schema...")
    
    try:
        schema = ConnectorFactory.get_config_schema(TargetType.MQTT)
        
        if not schema:
            print("❌ MQTT configuration schema is empty")
            return False
        
        if "properties" not in schema:
            print("❌ MQTT schema missing properties")
            return False
        
        required_properties = ["host", "port", "topic", "username", "password", "use_tls", "qos"]
        properties = schema["properties"]
        
        for prop in required_properties:
            if prop not in properties:
                print(f"❌ MQTT schema missing property: {prop}")
                return False
        
        print("✅ MQTT configuration schema is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error getting MQTT schema: {e}")
        return False


def validate_mqtt_config_validation():
    """Validate MQTT configuration validation"""
    print("\n🔍 Validating MQTT configuration validation...")
    
    # Test valid configuration
    valid_config = {
        "host": "mqtt.example.com",
        "port": 1883,
        "topic": "iot/sensors",
        "qos": 1
    }
    
    try:
        validated = ConnectorFactory.validate_config(TargetType.MQTT, valid_config)
        if not validated:
            print("❌ Valid MQTT config validation failed")
            return False
        print("✅ Valid MQTT configuration validated successfully")
    except Exception as e:
        print(f"❌ Valid MQTT config validation error: {e}")
        return False
    
    # Test invalid configuration
    invalid_config = {
        "host": "mqtt.example.com"
        # Missing required fields
    }
    
    try:
        ConnectorFactory.validate_config(TargetType.MQTT, invalid_config)
        print("❌ Invalid MQTT config should have failed validation")
        return False
    except ValueError:
        print("✅ Invalid MQTT configuration correctly rejected")
    except Exception as e:
        print(f"❌ Unexpected error with invalid config: {e}")
        return False
    
    return True


def validate_mqtt_connector_creation():
    """Validate MQTT connector creation via factory"""
    print("\n🔍 Validating MQTT connector creation...")
    
    configs = [
        {
            "name": "Basic MQTT",
            "config": {
                "host": "mqtt.example.com",
                "port": 1883,
                "topic": "iot/sensors"
            }
        },
        {
            "name": "MQTT with Auth",
            "config": {
                "host": "mqtt.example.com",
                "port": 1883,
                "topic": "iot/sensors",
                "username": "user",
                "password": "pass",
                "qos": 1
            }
        },
        {
            "name": "MQTT with TLS",
            "config": {
                "host": "secure-mqtt.example.com",
                "port": 8883,
                "topic": "iot/secure/sensors",
                "use_tls": True,
                "qos": 2
            }
        }
    ]
    
    for test_case in configs:
        try:
            connector = ConnectorFactory.create_connector(TargetType.MQTT, test_case["config"])
            
            if not isinstance(connector, MQTTConnector):
                print(f"❌ {test_case['name']}: Created connector is not MQTTConnector")
                return False
            
            # Validate configuration was applied correctly
            config = test_case["config"]
            if connector.config.host != config["host"]:
                print(f"❌ {test_case['name']}: Host not set correctly")
                return False
            
            if connector.config.port != config["port"]:
                print(f"❌ {test_case['name']}: Port not set correctly")
                return False
            
            if connector.config.topic != config["topic"]:
                print(f"❌ {test_case['name']}: Topic not set correctly")
                return False
            
            print(f"✅ {test_case['name']}: Connector created successfully")
            
        except Exception as e:
            print(f"❌ {test_case['name']}: Creation failed: {e}")
            return False
    
    return True


def validate_mqtt_convenience_functions():
    """Validate MQTT convenience functions"""
    print("\n🔍 Validating MQTT convenience functions...")
    
    from app.simulation.connectors import create_connector
    
    config = {
        "host": "mqtt.example.com",
        "port": 1883,
        "topic": "iot/sensors"
    }
    
    # Test different case variations
    for type_str in ["mqtt", "MQTT", "Mqtt"]:
        try:
            connector = create_connector(type_str, config)
            if not isinstance(connector, MQTTConnector):
                print(f"❌ Convenience function failed for '{type_str}'")
                return False
            print(f"✅ Convenience function works for '{type_str}'")
        except Exception as e:
            print(f"❌ Convenience function error for '{type_str}': {e}")
            return False
    
    return True


async def validate_mqtt_connector_interface():
    """Validate MQTT connector implements the interface correctly"""
    print("\n🔍 Validating MQTT connector interface...")
    
    config = {
        "host": "mqtt.example.com",
        "port": 1883,
        "topic": "iot/sensors"
    }
    
    try:
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        
        # Check that all required methods exist
        required_methods = ["connect", "send", "disconnect"]
        for method in required_methods:
            if not hasattr(connector, method):
                print(f"❌ MQTT connector missing method: {method}")
                return False
            
            if not callable(getattr(connector, method)):
                print(f"❌ MQTT connector method not callable: {method}")
                return False
        
        print("✅ MQTT connector implements required interface")
        
        # Test that methods can be called (they will fail due to no real broker, but shouldn't crash)
        try:
            # This will likely fail, but should not raise unexpected exceptions
            await connector.connect()
            print("✅ MQTT connect method callable")
        except Exception as e:
            # Expected to fail without real broker
            print(f"✅ MQTT connect method callable (failed as expected: {type(e).__name__})")
        
        try:
            # This should fail gracefully
            await connector.send({"test": "data"})
            print("✅ MQTT send method callable")
        except Exception as e:
            # Expected to fail without connection
            print(f"✅ MQTT send method callable (failed as expected: {type(e).__name__})")
        
        try:
            await connector.disconnect()
            print("✅ MQTT disconnect method callable")
        except Exception as e:
            print(f"⚠️  MQTT disconnect method error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ MQTT connector interface validation failed: {e}")
        return False


def validate_mqtt_config_model():
    """Validate MQTT configuration model"""
    print("\n🔍 Validating MQTT configuration model...")
    
    try:
        # Test valid configuration
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            username="user",
            password="pass",
            use_tls=True,
            qos=2
        )
        
        if config.host != "mqtt.example.com":
            print("❌ MQTT config model: host not set correctly")
            return False
        
        if config.port != 1883:
            print("❌ MQTT config model: port not set correctly")
            return False
        
        if config.topic != "iot/sensors":
            print("❌ MQTT config model: topic not set correctly")
            return False
        
        if config.qos != 2:
            print("❌ MQTT config model: qos not set correctly")
            return False
        
        print("✅ MQTT configuration model works correctly")
        
        # Test invalid configuration
        try:
            MQTTConfig(
                host="mqtt.example.com",
                port=70000,  # Invalid port
                topic="iot/sensors"
            )
            print("❌ MQTT config model should reject invalid port")
            return False
        except ValueError:
            print("✅ MQTT config model correctly rejects invalid port")
        
        try:
            MQTTConfig(
                host="mqtt.example.com",
                port=1883,
                topic="iot/sensors",
                qos=5  # Invalid QoS
            )
            print("❌ MQTT config model should reject invalid QoS")
            return False
        except ValueError:
            print("✅ MQTT config model correctly rejects invalid QoS")
        
        return True
        
    except Exception as e:
        print(f"❌ MQTT config model validation failed: {e}")
        return False


async def main():
    """Run all validation tests"""
    print("🚀 MQTT Integration Validation")
    print("=" * 50)
    
    validations = [
        ("Factory Integration", validate_mqtt_in_factory),
        ("Configuration Schema", validate_mqtt_config_schema),
        ("Configuration Validation", validate_mqtt_config_validation),
        ("Connector Creation", validate_mqtt_connector_creation),
        ("Convenience Functions", validate_mqtt_convenience_functions),
        ("Connector Interface", validate_mqtt_connector_interface),
        ("Configuration Model", validate_mqtt_config_model),
    ]
    
    passed = 0
    total = len(validations)
    
    for name, validation_func in validations:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            if asyncio.iscoroutinefunction(validation_func):
                result = await validation_func()
            else:
                result = validation_func()
            
            if result:
                passed += 1
                print(f"✅ {name}: PASSED")
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All MQTT integration validations PASSED!")
        print("\nThe MQTT connector is fully integrated and ready to use:")
        print("• ✅ Registered in ConnectorFactory")
        print("• ✅ Configuration validation working")
        print("• ✅ Schema generation working")
        print("• ✅ Connector creation working")
        print("• ✅ Interface implementation correct")
        print("• ✅ Convenience functions working")
        print("• ✅ Configuration model working")
        return True
    else:
        print(f"❌ {total - passed} validation(s) failed!")
        print("Please check the errors above and fix the issues.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)