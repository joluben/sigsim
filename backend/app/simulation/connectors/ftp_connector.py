"""
FTP/SFTP target connector
"""
import json
import asyncio
import tempfile
import os
from typing import Dict, Any
from datetime import datetime
import aioftp
import asyncssh
from app.simulation.connectors.base_connector import TargetConnector
from app.models.target import FTPConfig


class FTPConnector(TargetConnector):
    """Connector for FTP/SFTP file transfer"""
    
    def __init__(self, config: FTPConfig):
        self.config = config
        self.client = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to FTP/SFTP server"""
        try:
            if self.config.use_sftp:
                # SFTP connection using asyncssh
                self.client = await asyncssh.connect(
                    self.config.host,
                    port=self.config.port,
                    username=self.config.username,
                    password=self.config.password,
                    known_hosts=None  # Disable host key checking for simplicity
                )
            else:
                # FTP connection using aioftp
                self.client = aioftp.Client()
                await self.client.connect(self.config.host, self.config.port)
                await self.client.login(self.config.username, self.config.password)
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"FTP connection failed: {e}")
            return False
    
    async def send(self, payload: Dict[str, Any]) -> bool:
        """Upload payload as JSON file to FTP/SFTP server"""
        if not self.connected:
            return False
        
        try:
            # Create temporary file with JSON payload
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"payload_{timestamp}.json"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(payload, temp_file, indent=2)
                temp_file_path = temp_file.name
            
            try:
                # Ensure remote directory exists and upload file
                remote_path = os.path.join(self.config.path, filename).replace('\\', '/')
                
                if self.config.use_sftp:
                    # SFTP upload
                    async with self.client.start_sftp_client() as sftp:
                        # Try to create directory if it doesn't exist
                        try:
                            await sftp.makedirs(self.config.path, exist_ok=True)
                        except Exception:
                            pass  # Directory might already exist or we might not have permissions
                        
                        await sftp.put(temp_file_path, remote_path)
                else:
                    # FTP upload
                    # Try to create directory if it doesn't exist
                    try:
                        await self.client.make_directory(self.config.path)
                    except Exception:
                        pass  # Directory might already exist or we might not have permissions
                    
                    await self.client.upload(temp_file_path, remote_path)
                
                return True
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            print(f"FTP send failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from FTP/SFTP server"""
        if self.client:
            try:
                if self.config.use_sftp:
                    self.client.close()
                else:
                    await self.client.quit()
            except:
                pass  # Ignore errors during disconnect
            finally:
                self.client = None
                self.connected = False