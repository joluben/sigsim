#!/usr/bin/env python3
"""
MQTT Connector Demonstration

This script demonstrates the MQTT connector functionality including:
- Basic connection and messaging
- Authentication with username/password
- TLS/SSL connections
- Different QoS levels
- Error handling
"""
import asyncio
import json
from datetime import datetime
from app.simulation.connectors import ConnectorFactory
from app.models.target import TargetType


async def demo_basic_mqtt():
    """Demonstrate basic MQTT functionality"""
    print("\n=== Basic MQTT Demo ===")
    
    config = {
        "host": "test.mosquitto.org",  # Public test broker
        "port": 1883,
        "topic": "iot-simulator/demo/basic",
        "qos": 1
    }
    
    try:
        # Create connector using factory
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        print(f"✓ Created MQTT connector for {config['host']}:{config['port']}")
        
        # Connect to broker
        print("Connecting to MQTT broker...")
        connected = await connector.connect()
        
        if connected:
            print("✓ Connected to MQTT broker successfully")
            
            # Send multiple test messages
            for i in range(3):
                payload = {
                    "message_id": i + 1,
                    "device_id": "demo-sensor-001",
                    "temperature": 20.0 + i * 2.5,
                    "humidity": 60.0 + i * 5.0,
                    "timestamp": datetime.now().isoformat(),
                    "demo_type": "basic"
                }
                
                print(f"Sending message {i + 1}...")
                sent = await connector.send(payload)
                
                if sent:
                    print(f"✓ Message {i + 1} sent successfully")
                    print(f"  Topic: {config['topic']}")
                    print(f"  QoS: {config['qos']}")
                else:
                    print(f"✗ Failed to send message {i + 1}")
                
                # Small delay between messages
                await asyncio.sleep(1)
            
            # Disconnect
            await connector.disconnect()
            print("✓ Disconnected from MQTT broker")
            
        else:
            print("✗ Failed to connect to MQTT broker")
            
    except Exception as e:
        print(f"✗ Basic MQTT demo failed: {e}")


async def demo_mqtt_with_auth():
    """Demonstrate MQTT with authentication"""
    print("\n=== MQTT with Authentication Demo ===")
    
    # Note: This uses a public broker that may not require auth
    # In real scenarios, replace with your authenticated broker
    config = {
        "host": "test.mosquitto.org",
        "port": 1883,
        "topic": "iot-simulator/demo/auth",
        "username": "demo_user",  # These credentials won't work on public broker
        "password": "demo_pass",  # but demonstrate the configuration
        "qos": 1
    }
    
    try:
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        print(f"✓ Created MQTT connector with authentication")
        print(f"  Username: {config['username']}")
        print(f"  Password: {'*' * len(config['password'])}")
        
        # This will likely fail on public broker, but shows the process
        connected = await connector.connect()
        
        if connected:
            print("✓ Connected with authentication")
            
            payload = {
                "device_id": "authenticated-device",
                "status": "online",
                "auth_demo": True,
                "timestamp": datetime.now().isoformat()
            }
            
            sent = await connector.send(payload)
            if sent:
                print("✓ Authenticated message sent successfully")
            
            await connector.disconnect()
            print("✓ Disconnected")
        else:
            print("✗ Authentication failed (expected on public broker)")
            
    except Exception as e:
        print(f"✗ Authentication demo failed: {e}")


async def demo_mqtt_tls():
    """Demonstrate MQTT with TLS/SSL"""
    print("\n=== MQTT with TLS Demo ===")
    
    config = {
        "host": "test.mosquitto.org",
        "port": 8883,  # TLS port
        "topic": "iot-simulator/demo/tls",
        "use_tls": True,
        "qos": 2  # Highest QoS level
    }
    
    try:
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        print(f"✓ Created MQTT connector with TLS")
        print(f"  Port: {config['port']} (TLS)")
        print(f"  QoS: {config['qos']}")
        
        connected = await connector.connect()
        
        if connected:
            print("✓ Connected with TLS encryption")
            
            payload = {
                "device_id": "secure-device",
                "sensor_data": {
                    "temperature": 22.5,
                    "pressure": 1013.25,
                    "altitude": 150.0
                },
                "security": "TLS encrypted",
                "timestamp": datetime.now().isoformat()
            }
            
            sent = await connector.send(payload)
            if sent:
                print("✓ Encrypted message sent successfully")
                print(f"  Payload size: {len(json.dumps(payload))} bytes")
            
            await connector.disconnect()
            print("✓ Secure disconnection completed")
        else:
            print("✗ TLS connection failed")
            
    except Exception as e:
        print(f"✗ TLS demo failed: {e}")


async def demo_mqtt_qos_levels():
    """Demonstrate different QoS levels"""
    print("\n=== MQTT QoS Levels Demo ===")
    
    qos_descriptions = {
        0: "At most once (fire and forget)",
        1: "At least once (acknowledged delivery)",
        2: "Exactly once (assured delivery)"
    }
    
    for qos_level in [0, 1, 2]:
        print(f"\n--- Testing QoS {qos_level}: {qos_descriptions[qos_level]} ---")
        
        config = {
            "host": "test.mosquitto.org",
            "port": 1883,
            "topic": f"iot-simulator/demo/qos{qos_level}",
            "qos": qos_level
        }
        
        try:
            connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
            connected = await connector.connect()
            
            if connected:
                payload = {
                    "qos_level": qos_level,
                    "description": qos_descriptions[qos_level],
                    "device_id": f"qos-test-device-{qos_level}",
                    "test_data": f"QoS {qos_level} test message",
                    "timestamp": datetime.now().isoformat()
                }
                
                sent = await connector.send(payload)
                if sent:
                    print(f"✓ QoS {qos_level} message sent successfully")
                else:
                    print(f"✗ QoS {qos_level} message failed")
                
                await connector.disconnect()
            else:
                print(f"✗ Failed to connect for QoS {qos_level} test")
                
        except Exception as e:
            print(f"✗ QoS {qos_level} demo failed: {e}")


async def demo_mqtt_error_scenarios():
    """Demonstrate error handling scenarios"""
    print("\n=== MQTT Error Handling Demo ===")
    
    # Test 1: Invalid broker host
    print("\n--- Test 1: Invalid Broker Host ---")
    config = {
        "host": "invalid-mqtt-broker-12345.com",
        "port": 1883,
        "topic": "test/topic",
        "qos": 1
    }
    
    try:
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        print("✓ Connector created with invalid host")
        
        connected = await connector.connect()
        if not connected:
            print("✓ Correctly failed to connect to invalid host")
        else:
            print("✗ Unexpectedly connected to invalid host")
            await connector.disconnect()
            
    except Exception as e:
        print(f"✓ Correctly handled invalid host error: {e}")
    
    # Test 2: Send without connection
    print("\n--- Test 2: Send Without Connection ---")
    config = {
        "host": "test.mosquitto.org",
        "port": 1883,
        "topic": "test/topic",
        "qos": 1
    }
    
    try:
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        # Don't connect
        
        payload = {"test": "data"}
        sent = await connector.send(payload)
        
        if not sent:
            print("✓ Correctly failed to send without connection")
        else:
            print("✗ Unexpectedly sent message without connection")
            
    except Exception as e:
        print(f"✓ Correctly handled send without connection: {e}")
    
    # Test 3: Invalid configuration
    print("\n--- Test 3: Invalid Configuration ---")
    try:
        invalid_config = {
            "host": "test.mosquitto.org",
            # Missing required fields
        }
        
        ConnectorFactory.create_connector(TargetType.MQTT, invalid_config)
        print("✗ Should have failed with invalid config")
        
    except ValueError as e:
        print(f"✓ Correctly rejected invalid config: {e}")


async def demo_mqtt_performance():
    """Demonstrate MQTT performance with multiple messages"""
    print("\n=== MQTT Performance Demo ===")
    
    config = {
        "host": "test.mosquitto.org",
        "port": 1883,
        "topic": "iot-simulator/demo/performance",
        "qos": 1
    }
    
    try:
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        connected = await connector.connect()
        
        if connected:
            print("✓ Connected for performance test")
            
            message_count = 10
            start_time = datetime.now()
            successful_sends = 0
            
            print(f"Sending {message_count} messages...")
            
            for i in range(message_count):
                payload = {
                    "message_id": i + 1,
                    "device_id": "performance-test-device",
                    "batch_id": "perf-001",
                    "data": f"Performance test message {i + 1}",
                    "timestamp": datetime.now().isoformat()
                }
                
                sent = await connector.send(payload)
                if sent:
                    successful_sends += 1
                
                # Small delay to avoid overwhelming the broker
                await asyncio.sleep(0.1)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✓ Performance test completed")
            print(f"  Messages sent: {successful_sends}/{message_count}")
            print(f"  Duration: {duration:.2f} seconds")
            print(f"  Rate: {successful_sends/duration:.2f} messages/second")
            
            await connector.disconnect()
            print("✓ Performance test disconnected")
            
        else:
            print("✗ Failed to connect for performance test")
            
    except Exception as e:
        print(f"✗ Performance demo failed: {e}")


async def main():
    """Run all MQTT demonstrations"""
    print("🚀 MQTT Connector Demonstration")
    print("=" * 50)
    
    # Basic functionality
    await demo_basic_mqtt()
    
    # Authentication (will likely fail on public broker)
    await demo_mqtt_with_auth()
    
    # TLS encryption
    await demo_mqtt_tls()
    
    # QoS levels
    await demo_mqtt_qos_levels()
    
    # Error handling
    await demo_mqtt_error_scenarios()
    
    # Performance testing
    await demo_mqtt_performance()
    
    print("\n" + "=" * 50)
    print("✅ MQTT Connector demonstration completed!")
    print("\nThe MQTT connector provides:")
    print("• Support for standard MQTT brokers")
    print("• Authentication with username/password")
    print("• TLS/SSL encryption support")
    print("• All QoS levels (0, 1, 2)")
    print("• Robust error handling")
    print("• Async/await compatibility")
    print("• Integration with ConnectorFactory")
    
    print("\nConfiguration options:")
    print("• host: MQTT broker hostname")
    print("• port: MQTT broker port (1883 standard, 8883 TLS)")
    print("• topic: MQTT topic for publishing")
    print("• username/password: Authentication credentials")
    print("• use_tls: Enable TLS/SSL encryption")
    print("• qos: Quality of Service level (0, 1, 2)")


if __name__ == "__main__":
    asyncio.run(main())