#  **Seedr-Auto-Downloader - _AutoSeedr_**

---

---
## **Automate Torrent Downloads and Bypass ISP Throttling**
Tired of ISP throttling slowing down your torrent downloads? 
AutoSeedr is built for that problem. This Python script automates the process of uploading torrents to Seedr, 
a cloud storage service that lets you download files over HTTPS, bypassing ISP restrictions and maximizing your download speed.

---
## What is Seedr
Seedr is a cloud-based torrent client that allows users to download and stream torrents directly from the cloud without the need for a dedicated torrent client on their local 

**Uploading Torrents:** Users upload torrent files or magnet links to Seedr's platform.


**Cloud-Based Processing:** Seedr processes these torrents in the cloud, fetching the data associated with the torrent files and making it available for users.

**Secure Storage:** The downloaded data is stored securely in the cloud on Seedr's servers.

**User Access:** Users can access and manage their torrents through Seedr's web interface.

**Streaming and Downloading:** Seedr allows users to either stream content directly from the cloud or download it to their local device.

**HTTPS Encryption:** Seedr uses HTTPS encryption for data transfer, providing a secure connection.

## How seedr increase Internet Speed 

**ISP Throttling Avoidance:** 
Seedr helps users avoid ISP throttling by downloading torrents to its servers in the cloud. Since the actual torrent activity is not on the user's local network, ISPs may not be able to identify and throttle the torrent traffic.

**Server Locations and Network Speed:** 
Seedr's servers may be located in data centers with high-speed internet connections. The proximity and quality of these servers can contribute to faster download speeds compared to using a local torrent client.

**Parallel Downloading:** Seedr may employ parallel downloading techniques, enabling the client to download different parts of a file simultaneously. This can optimize download speeds, especially for larger files.

**Seedr's CDN (Content Delivery Network):**
Seedr may use a CDN to distribute content efficiently. CDNs cache content on multiple servers across different locations, reducing latency and improving download speeds for users accessing the same content from various locations.

**HTTPS Encryption:**
Seedr uses encrypted HTTPS connections for data transfer. While encryption adds a layer of security, it may also impact the speed slightly due to the additional processing required for encryption and decryption.


### Features:

**Automatic Torrent Uploading:** Scan your designated folder for new torrents and automatically upload them to Seedr.

**Efficient File Management:** Only you have to put all you torrents that need to download in a folder and the script will automatically upload them to Seedr and download them to your local device.

**HTTPS Download:** Download files directly from Seedr servers over HTTPS, avoiding ISP throttling and enjoying faster speeds.

**Logging and Error Handling:** Track successful downloads and record any errors for troubleshooting.

**Configurable Settings:** Customize the script's behavior to fit your needs, including torrent folder, download directory, and chunk size.



### Getting Started:

+ Install Python: Ensure you have Python 3.x installed on your system.
+ Install Dependencies: .
```
pip install -r requirements.txt
``` 
+ Create a Seedr Account: Sign up for a Seedr account at https://www.seedr.cc/.

+ Configure Settings: in first when program execute it will ask for your seedr username, password, Download folder path, from 2nd execute it will automattically download all the torrents located in `torrent` folder

+ Run the Script:  
```
python main.py
``` 

### Usage:

Additional Information:

For detailed configuration options and troubleshooting tips, refer to the script's comments and the `README.md` file.
Feel free to contribute to the project by reporting issues, suggesting improvements, or submitting pull requests.


I hope this helps! Let me know if you have any other questions.

## TODO
- [ ] add a function to check if the file is already downloaded
- [ ] Multiple torrent download from multiple seedr accounts to use maximum bandwidth from isp and avoid limits of seedr server bandwidth
- [ ] add argument parser using argparse (fastdownload, progressbar download,)
- [ ] few bugs while release 'indipendent .ini file

[Send Email: hello@pasanlaksitha.com](mailto:hello@pasanlaksitha.com)


## License

This project is licensed under the [MIT License](./LICENSE).