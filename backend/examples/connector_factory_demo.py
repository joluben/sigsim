#!/usr/bin/env python3
"""
Demonstration script for the ConnectorFactory system

This script shows how to use the ConnectorFactory to create and test
different types of target system connectors.
"""
import asyncio
import json
from typing import Dict, Any

from app.simulation.connectors import ConnectorFactory, get_supported_connector_types
from app.models.target import TargetType


async def demo_http_connector():
    """Demonstrate HTTP connector usage"""
    print("\n=== HTTP Connector Demo ===")
    
    config = {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "timeout": 30
    }
    
    try:
        # Create connector using factory
        connector = ConnectorFactory.create_connector(TargetType.HTTP, config)
        print(f"✓ Created HTTP connector for {config['url']}")
        
        # Connect
        connected = await connector.connect()
        if connected:
            print("✓ Connected successfully")
            
            # Send test payload
            test_payload = {
                "device_id": "demo-device-001",
                "temperature": 23.5,
                "humidity": 65.2,
                "timestamp": "2024-01-01T12:00:00Z"
            }
            
            sent = await connector.send(test_payload)
            if sent:
                print("✓ Test payload sent successfully")
                print(f"  Payload: {json.dumps(test_payload, indent=2)}")
            else:
                print("✗ Failed to send test payload")
            
            # Disconnect
            await connector.disconnect()
            print("✓ Disconnected")
        else:
            print("✗ Failed to connect")
            
    except Exception as e:
        print(f"✗ HTTP connector demo failed: {e}")


async def demo_mqtt_connector():
    """Demonstrate MQTT connector usage (requires MQTT broker)"""
    print("\n=== MQTT Connector Demo ===")
    
    config = {
        "host": "test.mosquitto.org",  # Public test broker
        "port": 1883,
        "topic": "iot-simulator/demo",
        "qos": 1
    }
    
    try:
        # Create connector using factory
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        print(f"✓ Created MQTT connector for {config['host']}:{config['port']}")
        
        # Connect
        connected = await connector.connect()
        if connected:
            print("✓ Connected to MQTT broker")
            
            # Send test payload
            test_payload = {
                "device_id": "demo-device-002",
                "sensor_type": "temperature",
                "value": 24.8,
                "unit": "°C",
                "timestamp": "2024-01-01T12:00:00Z"
            }
            
            sent = await connector.send(test_payload)
            if sent:
                print("✓ Test payload published successfully")
                print(f"  Topic: {config['topic']}")
                print(f"  Payload: {json.dumps(test_payload, indent=2)}")
            else:
                print("✗ Failed to publish test payload")
            
            # Disconnect
            await connector.disconnect()
            print("✓ Disconnected from MQTT broker")
        else:
            print("✗ Failed to connect to MQTT broker")
            
    except Exception as e:
        print(f"✗ MQTT connector demo failed: {e}")


async def demo_websocket_connector():
    """Demonstrate WebSocket connector usage"""
    print("\n=== WebSocket Connector Demo ===")
    
    config = {
        "url": "wss://echo.websocket.org",  # Public WebSocket echo service
        "ping_interval": 20
    }
    
    try:
        # Create connector using factory
        connector = ConnectorFactory.create_connector(TargetType.WEBSOCKET, config)
        print(f"✓ Created WebSocket connector for {config['url']}")
        
        # Connect
        connected = await connector.connect()
        if connected:
            print("✓ Connected to WebSocket")
            
            # Send test payload
            test_payload = {
                "device_id": "demo-device-003",
                "event_type": "motion_detected",
                "location": "entrance",
                "timestamp": "2024-01-01T12:00:00Z"
            }
            
            sent = await connector.send(test_payload)
            if sent:
                print("✓ Test payload sent successfully")
                print(f"  Payload: {json.dumps(test_payload, indent=2)}")
            else:
                print("✗ Failed to send test payload")
            
            # Disconnect
            await connector.disconnect()
            print("✓ Disconnected from WebSocket")
        else:
            print("✗ Failed to connect to WebSocket")
            
    except Exception as e:
        print(f"✗ WebSocket connector demo failed: {e}")


def demo_factory_features():
    """Demonstrate factory features"""
    print("\n=== ConnectorFactory Features Demo ===")
    
    # Show supported types
    supported_types = get_supported_connector_types()
    print(f"✓ Supported connector types: {', '.join(supported_types)}")
    
    # Show config schemas
    for type_str in supported_types[:3]:  # Show first 3 for brevity
        try:
            target_type = TargetType(type_str)
            schema = ConnectorFactory.get_config_schema(target_type)
            if schema:
                print(f"✓ {type_str.upper()} config schema available")
                # Show required fields if available
                if 'required' in schema:
                    print(f"  Required fields: {', '.join(schema['required'])}")
            else:
                print(f"- {type_str.upper()} config schema not available")
        except Exception as e:
            print(f"✗ Error getting schema for {type_str}: {e}")
    
    # Test config validation
    print("\n--- Config Validation Demo ---")
    
    # Valid HTTP config
    valid_http_config = {
        "url": "https://api.example.com/webhook",
        "method": "POST"
    }
    
    try:
        validated = ConnectorFactory.validate_config(TargetType.HTTP, valid_http_config)
        print("✓ Valid HTTP config validated successfully")
    except Exception as e:
        print(f"✗ HTTP config validation failed: {e}")
    
    # Invalid HTTP config
    invalid_http_config = {
        "method": "POST"  # Missing URL
    }
    
    try:
        ConnectorFactory.validate_config(TargetType.HTTP, invalid_http_config)
        print("✗ Invalid HTTP config should have failed validation")
    except Exception as e:
        print(f"✓ Invalid HTTP config correctly rejected: {e}")


async def demo_error_handling():
    """Demonstrate error handling"""
    print("\n=== Error Handling Demo ===")
    
    # Test unsupported connector type
    try:
        ConnectorFactory.create_connector("unsupported_type", {})
        print("✗ Should have failed for unsupported type")
    except ValueError as e:
        print(f"✓ Correctly handled unsupported type: {e}")
    
    # Test invalid configuration
    try:
        ConnectorFactory.create_connector(TargetType.HTTP, {"invalid": "config"})
        print("✗ Should have failed for invalid config")
    except ValueError as e:
        print(f"✓ Correctly handled invalid config: {e}")
    
    # Test connection failure (invalid host)
    config = {
        "host": "invalid-mqtt-broker-host-12345.com",
        "port": 1883,
        "topic": "test/topic"
    }
    
    try:
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        print("✓ Created connector with invalid host")
        
        # This should fail
        connected = await connector.connect()
        if not connected:
            print("✓ Correctly failed to connect to invalid host")
        else:
            print("✗ Unexpectedly connected to invalid host")
            await connector.disconnect()
            
    except Exception as e:
        print(f"✓ Correctly handled connection error: {e}")


async def main():
    """Run all demonstrations"""
    print("🚀 ConnectorFactory Demonstration")
    print("=" * 50)
    
    # Show factory features
    demo_factory_features()
    
    # Test error handling
    await demo_error_handling()
    
    # Test actual connectors (these may fail if services are not available)
    print("\n" + "=" * 50)
    print("🔗 Testing Real Connectors")
    print("Note: These tests may fail if external services are not available")
    
    await demo_http_connector()
    await demo_mqtt_connector()
    await demo_websocket_connector()
    
    print("\n" + "=" * 50)
    print("✅ ConnectorFactory demonstration completed!")
    print("\nThe factory system provides:")
    print("• Unified interface for all connector types")
    print("• Automatic configuration validation")
    print("• Easy extensibility for new connector types")
    print("• Consistent error handling")
    print("• Type safety with Pydantic models")


if __name__ == "__main__":
    asyncio.run(main())