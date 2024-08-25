import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
url = "https://www.stanford.edu/"
capture_file = "capture1.pcap"
interface = "wlo1"  # Replace with your network interface
capture_duration = 30  # Duration to capture in seconds

log_entries = []
# Start the browser using Selenium
def start_browser(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.script.add_console_message_handler(log_entries.append)

    driver.get(url)
    return driver


# Start tshark to capture traffic
def start_tshark(interface, capture_file, duration):
    command = [
        "tshark",
        "-i",
        interface,
        "-w",
        capture_file,
        "-a",
        f"duration:{duration}",
    ]
    return subprocess.Popen(command)


# Main execution
def main():

    # Start packet capture
    print(
        f"Starting capture on interface {interface} for {capture_duration} seconds..."
    )
    tshark_process = start_tshark(interface, capture_file, capture_duration)
    # Start the browser
    driver = start_browser(url)

    # Wait for the capture to complete
    time.sleep(capture_duration)

    # Close the browser
    print("Closing browser...")
    driver.quit()
    print(log_entries)
    # Stop tshark
    print("Stopping capture...")
    tshark_process.terminate()

    # Wait for tshark to finalize the capture
    tshark_process.wait()

    print(f"Capture saved to {capture_file}")
    print("Opening capture in Wireshark...")

    # Open the capture file in Wireshark
    subprocess.run(["wireshark", capture_file])


if __name__ == "__main__":
    main()
