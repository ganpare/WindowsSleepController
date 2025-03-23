import sys
import os
import logging
import socket
import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess

# Configure logging
logging.basicConfig(
    filename='alexa_sleep_service.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AlexaSleepService')

class AlexaSleepService(win32serviceutil.ServiceFramework):
    """Windows Service for Alexa Sleep Integration"""
    
    _svc_name_ = "AlexaSleepService"
    _svc_display_name_ = "Alexa Sleep Service"
    _svc_description_ = "Service to allow Alexa to trigger sleep mode on this computer"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        
        # Get the directory of the service script
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        
        # Process ID for the server process
        self.process = None
        
        socket.setdefaulttimeout(60)
        
    def SvcStop(self):
        """Stop the service"""
        logger.info("Stopping service...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_alive = False
        
        # Terminate the server process if it's running
        if self.process:
            try:
                self.process.terminate()
                logger.info("Server process terminated")
            except Exception as e:
                logger.error(f"Error terminating server process: {e}")

    def SvcDoRun(self):
        """Run the service"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        logger.info("Starting service...")
        self.main()

    def main(self):
        """Main service logic"""
        logger.info("Service running in directory: %s", self.base_dir)
        
        # Path to the Python script
        main_script = os.path.join(self.base_dir, 'main.py')
        
        # Check if script exists
        if not os.path.exists(main_script):
            logger.error(f"Main script not found: {main_script}")
            return
        
        try:
            # Get Python interpreter path
            python_exe = sys.executable
            
            # Start the server as a subprocess
            logger.info(f"Starting server with {python_exe} {main_script}")
            self.process = subprocess.Popen(
                [python_exe, main_script],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            logger.info(f"Server started with PID: {self.process.pid}")
            
            # Wait for the service to be stopped
            while self.is_alive:
                # Check if the process is still running
                if self.process.poll() is not None:
                    logger.error(f"Server process exited unexpectedly with code: {self.process.returncode}")
                    # Log stderr output from the process
                    error_output = self.process.stderr.read().decode('utf-8', errors='ignore')
                    logger.error(f"Server error output: {error_output}")
                    
                    # Restart the server
                    logger.info("Attempting to restart server...")
                    self.process = subprocess.Popen(
                        [python_exe, main_script],
                        cwd=self.base_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    logger.info(f"Server restarted with PID: {self.process.pid}")
                
                # Wait for stop event or check again in 10 seconds
                rc = win32event.WaitForSingleObject(self.stop_event, 10000)
                if rc == win32event.WAIT_OBJECT_0:
                    # Stop event triggered
                    break
            
            logger.info("Service stop event received")
            
        except Exception as e:
            logger.exception(f"Error in service main loop: {e}")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AlexaSleepService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AlexaSleepService)
