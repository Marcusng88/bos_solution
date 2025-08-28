"""
Windows Compatibility Module
Handles Windows-specific asyncio and subprocess issues for monitoring agents
"""

import platform
import asyncio
import sys
import logging

logger = logging.getLogger(__name__)


class WindowsCompatibilityManager:
    """Global Windows compatibility manager for asyncio subprocess issues"""
    
    _initialized = False
    
    @classmethod
    def is_windows(cls) -> bool:
        """Check if running on Windows"""
        return platform.system() == "Windows"
    
    @classmethod
    def setup_windows_event_loop(cls) -> bool:
        """Setup Windows-compatible event loop policy to fix subprocess issues"""
        if not cls.is_windows():
            return True
            
        if cls._initialized:
            return True
            
        try:
            # Force Windows ProactorEventLoop policy for subprocess support
            if sys.platform == 'win32':
                logger.info("🔄 Setting Windows ProactorEventLoop policy for subprocess support...")
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                
                # Create a new event loop with the correct policy
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                logger.info("✅ Windows ProactorEventLoop policy set successfully")
                cls._initialized = True
                return True
            else:
                logger.info("✅ Not on Windows, using default event loop policy")
                cls._initialized = True
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to set Windows event loop policy: {e}")
            return False
    
    @classmethod
    async def safe_async_operation(cls, operation, fallback_operation=None, operation_name="async operation"):
        """Safely execute async operations with Windows compatibility"""
        try:
            return await operation()
        except NotImplementedError as e:
            if cls.is_windows():
                logger.warning(f"❌ Windows asyncio subprocess error in {operation_name}: {e}")
                logger.info("🔄 Attempting to fix Windows event loop policy...")
                
                # Try to fix the event loop policy
                if cls.setup_windows_event_loop():
                    logger.info("🔄 Retrying operation with fixed event loop...")
                    try:
                        return await operation()
                    except Exception as retry_e:
                        logger.warning(f"❌ Retry failed: {retry_e}")
                
                # Use fallback if available
                if fallback_operation:
                    logger.info(f"🔄 Using fallback operation for {operation_name}")
                    return await fallback_operation()
                else:
                    logger.error(f"❌ No fallback available for {operation_name}")
                    return None
            else:
                raise
        except Exception as e:
            logger.error(f"❌ Error in {operation_name}: {e}")
            if fallback_operation:
                logger.info(f"🔄 Using fallback operation for {operation_name}")
                return await fallback_operation()
            return None
    
    @classmethod
    def ensure_windows_compatibility(cls) -> bool:
        """Ensure Windows compatibility is set up before any async operations"""
        if cls.is_windows():
            logger.info("🔄 Ensuring Windows compatibility...")
            return cls.setup_windows_event_loop()
        return True


# Global instance
windows_compat = WindowsCompatibilityManager()


def setup_windows_compatibility():
    """Global function to setup Windows compatibility"""
    return windows_compat.ensure_windows_compatibility()


async def safe_async_operation(operation, fallback_operation=None, operation_name="async operation"):
    """Global function for safe async operations"""
    return await windows_compat.safe_async_operation(operation, fallback_operation, operation_name)
