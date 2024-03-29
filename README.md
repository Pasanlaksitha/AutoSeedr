 
<p align="center">
  <img src="images/logo.png" width="200" />
</p>


<p align="center">
    <h1 align="center">Seedr Torrent Downloader - AutoSeedr</h1>
</p>

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



### Getting Started `main.py`:

+ Install Python: Ensure you have Python 3.x installed on your system.
+ Install Dependencies
```
pip install -r requirements.txt
``` 
+ Create a Seedr Account: Sign up for a Seedr account at https://www.seedr.cc/.

+ Configure Settings: in first when program execute it will ask for your seedr username, password, Download folder path, from 2nd execute it will automattically download all the torrents located in `torrent` folder

+ Run the Script:  
```
python main.py
``` 
+ After input your Seedr Account credentials and App Settings run `main.py` file again

### Getting Started `cli.py`:
 you should run and setup config.ini file before run this script
+ Run the Script for help:  
```
python cli.py -h
``` 
+ Example Commands:  
```
    
    usage: cli.py [-h] [-C] [-L] [-f CONFIG_FILE] [-e EMAIL] [-p PASSWORD] [-td TORRENT_DIRECTORY]
              [-dd DOWNLOAD_DIRECTORY] [-cs CHUNK_SIZE] [-ll {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-lf LOG_FILE]

AutoSeedr CLI

optional arguments:
  -h, --help            show this help message and exit
  -C, --create-config   Create a new config file
  -L, --load-config     Load an existing config file

Configuration Options:
  -f CONFIG_FILE, --config-file CONFIG_FILE
                        INI file path for configuration (default: config.ini)
  -e EMAIL, --email EMAIL
                        Seedr account email
  -p PASSWORD, --password PASSWORD
                        Seedr account password
  -td TORRENT_DIRECTORY, --torrent-directory TORRENT_DIRECTORY
                        Directory containing torrent files (default: torrents)
  -dd DOWNLOAD_DIRECTORY, --download-directory DOWNLOAD_DIRECTORY
                        Directory to store downloaded files (default: downloads)
  -cs CHUNK_SIZE, --chunk-size CHUNK_SIZE
                        Chunk size for downloading files in kilobytes (default: 1024)

Logging Options:
  -ll {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level (default: ERROR)
  -lf LOG_FILE, --log-file LOG_FILE
                        Log file path (default: auto_seedr_cli.log)
```

+ Load from config and download torrents from seedr
```
python cli.py -L -f config.ini
```

### Usage:

Additional Information:

For detailed configuration options and troubleshooting tips, refer to the script's comments and the `README.md` file.
Feel free to contribute to the project by reporting issues, suggesting improvements, or submitting pull requests.


I hope this helps! Let me know if you have any other questions.

## TODO

- [x] Cli.py Command line interface with more features.
- [ ] add a function to check if the file is already downloaded
- [ ] Multiple torrent download from multiple seedr accounts to use maximum bandwidth from isp and avoid limits of seedr server bandwidth
- [x] add argument parser using argparse (fastdownload, progressbar download)
- [x] few bugs while release 'indipendent .ini file
- [x] GUI interface and compiled exe file for windows users
- [x] fix icon in GUI interface
- [ ] ADD features to gui interface that are in cli.py
- [ ] multiple seedr account add to GUI interface

[Send Email: hello@pasanlaksitha.com](mailto:hello@pasanlaksitha.com)


## License

This project is licensed under the [MIT License](./LICENSE).
