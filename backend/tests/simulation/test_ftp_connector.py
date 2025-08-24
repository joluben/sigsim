"""
Tests for FTP connector functionality
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.simulation.connectors.ftp_connector import FTPConnector
from app.models.target import FTPConfig


class TestFTPConnector:
    """Test FTP connector functionality"""
    
    def test_ftp_connector_init(self):
        """Test FTP connector initialization"""
        config = FTPConfig(
            host="ftp.example.com",
            port=21,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=False
        )
        
        connector = FTPConnector(config)
        
        assert connector.config == config
        assert connector.client is None
        assert connector.connected is False
    
    def test_sftp_connector_init(self):
        """Test SFTP connector initialization"""
        config = FTPConfig(
            host="sftp.example.com",
            port=22,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=True
        )
        
        connector = FTPConnector(config)
        
        assert connector.config == config
        assert connector.client is None
        assert connector.connected is False
    
    @pytest.mark.asyncio
    async def test_ftp_connect_success(self):
        """Test successful FTP connection"""
        config = FTPConfig(
            host="ftp.example.com",
            port=21,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=False
        )
        
        connector = FTPConnector(config)
        
        # Mock aioftp.Client
        with patch('app.simulation.connectors.ftp_connector.aioftp.Client') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            result = await connector.connect()
            
            assert result is True
            assert connector.connected is True
            assert connector.client == mock_client
            
            # Verify connection calls
            mock_client.connect.assert_called_once_with("ftp.example.com", 21)
            mock_client.login.assert_called_once_with("testuser", "testpass")
    
    @pytest.mark.asyncio
    async def test_sftp_connect_success(self):
        """Test successful SFTP connection"""
        config = FTPConfig(
            host="sftp.example.com",
            port=22,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=True
        )
        
        connector = FTPConnector(config)
        
        # Mock asyncssh.connect
        with patch('app.simulation.connectors.ftp_connector.asyncssh.connect') as mock_connect:
            mock_client = AsyncMock()
            mock_connect.return_value = mock_client
            
            result = await connector.connect()
            
            assert result is True
            assert connector.connected is True
            assert connector.client == mock_client
            
            # Verify connection calls
            mock_connect.assert_called_once_with(
                "sftp.example.com",
                port=22,
                username="testuser",
                password="testpass",
                known_hosts=None
            )
    
    @pytest.mark.asyncio
    async def test_ftp_connect_failure(self):
        """Test FTP connection failure"""
        config = FTPConfig(
            host="ftp.example.com",
            port=21,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=False
        )
        
        connector = FTPConnector(config)
        
        # Mock aioftp.Client to raise exception
        with patch('app.simulation.connectors.ftp_connector.aioftp.Client') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.connect.side_effect = Exception("Connection failed")
            
            result = await connector.connect()
            
            assert result is False
            assert connector.connected is False
    
    @pytest.mark.asyncio
    async def test_ftp_send_not_connected(self):
        """Test FTP send when not connected"""
        config = FTPConfig(
            host="ftp.example.com",
            port=21,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=False
        )
        
        connector = FTPConnector(config)
        
        payload = {"test": "data"}
        result = await connector.send(payload)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_ftp_send_success(self):
        """Test successful FTP send"""
        config = FTPConfig(
            host="ftp.example.com",
            port=21,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=False
        )
        
        connector = FTPConnector(config)
        connector.connected = True
        
        mock_client = AsyncMock()
        connector.client = mock_client
        
        payload = {"test": "data", "timestamp": "2024-01-15T10:30:00Z"}
        
        with patch('tempfile.NamedTemporaryFile') as mock_temp, \
             patch('os.unlink') as mock_unlink, \
             patch('json.dump') as mock_json_dump:
            
            # Mock temporary file
            mock_temp_file = Mock()
            mock_temp_file.name = "/tmp/test_file.json"
            mock_temp.__enter__.return_value = mock_temp_file
            
            result = await connector.send(payload)
            
            assert result is True
            
            # Verify file operations
            mock_json_dump.assert_called_once()
            mock_client.upload.assert_called_once()
            mock_unlink.assert_called_once_with("/tmp/test_file.json")
    
    @pytest.mark.asyncio
    async def test_sftp_send_success(self):
        """Test successful SFTP send"""
        config = FTPConfig(
            host="sftp.example.com",
            port=22,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=True
        )
        
        connector = FTPConnector(config)
        connector.connected = True
        
        mock_client = AsyncMock()
        mock_sftp_client = AsyncMock()
        mock_client.start_sftp_client.return_value.__aenter__.return_value = mock_sftp_client
        connector.client = mock_client
        
        payload = {"test": "data", "timestamp": "2024-01-15T10:30:00Z"}
        
        with patch('tempfile.NamedTemporaryFile') as mock_temp, \
             patch('os.unlink') as mock_unlink, \
             patch('json.dump') as mock_json_dump:
            
            # Mock temporary file
            mock_temp_file = Mock()
            mock_temp_file.name = "/tmp/test_file.json"
            mock_temp.__enter__.return_value = mock_temp_file
            
            result = await connector.send(payload)
            
            assert result is True
            
            # Verify file operations
            mock_json_dump.assert_called_once()
            mock_sftp_client.put.assert_called_once()
            mock_unlink.assert_called_once_with("/tmp/test_file.json")
    
    @pytest.mark.asyncio
    async def test_ftp_send_failure(self):
        """Test FTP send failure"""
        config = FTPConfig(
            host="ftp.example.com",
            port=21,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=False
        )
        
        connector = FTPConnector(config)
        connector.connected = True
        
        mock_client = AsyncMock()
        mock_client.upload.side_effect = Exception("Upload failed")
        connector.client = mock_client
        
        payload = {"test": "data"}
        
        with patch('tempfile.NamedTemporaryFile') as mock_temp, \
             patch('os.unlink') as mock_unlink, \
             patch('json.dump') as mock_json_dump:
            
            # Mock temporary file
            mock_temp_file = Mock()
            mock_temp_file.name = "/tmp/test_file.json"
            mock_temp.__enter__.return_value = mock_temp_file
            
            result = await connector.send(payload)
            
            assert result is False
            
            # Verify cleanup still happens
            mock_unlink.assert_called_once_with("/tmp/test_file.json")
    
    @pytest.mark.asyncio
    async def test_ftp_disconnect(self):
        """Test FTP disconnect"""
        config = FTPConfig(
            host="ftp.example.com",
            port=21,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=False
        )
        
        connector = FTPConnector(config)
        connector.connected = True
        
        mock_client = AsyncMock()
        connector.client = mock_client
        
        await connector.disconnect()
        
        assert connector.client is None
        assert connector.connected is False
        mock_client.quit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sftp_disconnect(self):
        """Test SFTP disconnect"""
        config = FTPConfig(
            host="sftp.example.com",
            port=22,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=True
        )
        
        connector = FTPConnector(config)
        connector.connected = True
        
        mock_client = Mock()
        connector.client = mock_client
        
        await connector.disconnect()
        
        assert connector.client is None
        assert connector.connected is False
        mock_client.close.assert_called_once()


class TestFTPConnectorIntegration:
    """Integration tests for FTP connector"""
    
    def test_ftp_config_validation(self):
        """Test FTP configuration validation"""
        # Valid config
        config = FTPConfig(
            host="ftp.example.com",
            port=21,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=False
        )
        
        assert config.host == "ftp.example.com"
        assert config.port == 21
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.path == "/uploads"
        assert config.use_sftp is False
    
    def test_sftp_config_validation(self):
        """Test SFTP configuration validation"""
        # Valid config
        config = FTPConfig(
            host="sftp.example.com",
            port=22,
            username="testuser",
            password="testpass",
            path="/uploads",
            use_sftp=True
        )
        
        assert config.host == "sftp.example.com"
        assert config.port == 22
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.path == "/uploads"
        assert config.use_sftp is True
    
    def test_ftp_config_defaults(self):
        """Test FTP configuration defaults"""
        config = FTPConfig(
            host="ftp.example.com",
            username="testuser",
            password="testpass"
        )
        
        assert config.port == 21  # Default FTP port
        assert config.path == "/"  # Default path
        assert config.use_sftp is False  # Default to FTP