# Chunked Download Feature Guide

## Overview

AutoSeedr now supports **intelligent chunked downloads** to handle large files that exceed your Seedr storage limit. This feature automatically splits large files into smaller chunks, downloads them in parallel, and reassembles them on your local machine with the correct file extension.

## How It Works

### The Challenge
- Your Seedr free account has **4GB storage limit**
- Multi-file torrents with individual files >4GB cannot be fully downloaded to Seedr's cloud
- Large video files (e.g., 10GB .mp4) need to be downloaded efficiently

### The Solution
1. **Chunked Download with HTTP Range Requests**
   - Files larger than the chunk size (default: 2GB) are automatically split
   - Each chunk is downloaded in parallel using HTTP Range headers
   - Chunks are saved as `.part0`, `.part1`, `.part2`, etc.
   - After all chunks complete, they're reassembled into the final file with the correct extension

2. **Sequential File Processing** (Multi-file Torrents)
   - Downloads files one at a time from the torrent
   - Optionally deletes each file from Seedr after downloading
   - Frees up space for the next file automatically

3. **Smart Fallback**
   - If Range requests aren't supported, falls back to standard download
   - If a file is smaller than chunk size, uses standard download

## Important Limitations

### Critical Understanding
**Seedr downloads the entire torrent to their cloud storage first**, then you download from their servers.

- ✅ **Files ≤4GB**: Can be chunked and downloaded successfully
- ❌ **Single files >4GB**: Seedr itself cannot download them (won't fit in your 4GB storage)
- ✅ **Multi-file torrents**: Download files sequentially with automatic cleanup

### What This Feature DOES
- Downloads large files (≤4GB) in chunks for faster, resumable downloads
- Automatically reassembles chunks with correct file extensions
- Deletes files from Seedr after download to free space for next file
- Parallel chunk downloads for improved speed

### What This Feature DOESN'T DO
- Cannot download a single file >4GB if Seedr can't download it first
- Cannot split a torrent file before Seedr downloads it
- Solution: Upgrade your Seedr account for files >4GB

## Usage Examples

### Example 1: Basic Usage with Chunked Downloads (Default)

```bash
python3 cli.py -e your@email.com -p yourpassword
```

By default, chunked downloads are **enabled** with:
- Chunk size: 2GB
- Max parallel workers: 4
- Delete after download: Disabled

### Example 2: Custom Chunk Size

Download files in 1GB chunks:

```bash
python3 cli.py -e your@email.com -p yourpassword --chunk-download-size 1.0
```

### Example 3: Enable Auto-Delete (Free Up Seedr Space)

Automatically delete files from Seedr after downloading:

```bash
python3 cli.py -e your@email.com -p yourpassword --delete-after-download
```

This is **highly recommended** for multi-file torrents with limited Seedr storage!

### Example 4: Maximum Speed (More Parallel Downloads)

Use 8 parallel workers for faster downloads:

```bash
python3 cli.py -e your@email.com -p yourpassword --max-workers 8
```

### Example 5: Disable Chunked Downloads

Revert to traditional single-stream downloads:

```bash
python3 cli.py -e your@email.com -p yourpassword --disable-chunked-download
```

### Example 6: Optimal Settings for 4GB Seedr Limit

```bash
python3 cli.py -e your@email.com -p yourpassword \
  --chunk-download-size 1.5 \
  --max-workers 4 \
  --delete-after-download
```

This configuration:
- Downloads in 1.5GB chunks (fits comfortably in 4GB limit)
- Uses 4 parallel workers
- Automatically deletes files after download to free space

### Example 7: Using Config File

Create a config file with chunked download settings:

```bash
python3 cli.py --create-config \
  -e your@email.com \
  -p yourpassword \
  --chunk-download-size 2.0 \
  --max-workers 4 \
  --delete-after-download
```

Then load it:

```bash
python3 cli.py --load-config -f config.ini
```

## CLI Options Reference

### Chunked Download Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--enable-chunked-download` | flag | True | Enable chunked downloads for large files |
| `--disable-chunked-download` | flag | False | Disable chunked downloads |
| `--chunk-download-size` | float | 2.0 | Size of each chunk in GB |
| `--max-workers` | int | 4 | Number of parallel chunk downloads |
| `--delete-after-download` | flag | False | Delete files from Seedr after downloading |

## Real-World Scenarios

### Scenario 1: Downloading a 10GB Movie (Single File)

**Problem**: Your Seedr account has 4GB storage. The movie file is 10GB.

**Solution**: This won't work with free Seedr because:
1. Seedr needs to download the entire 10GB file first
2. It won't fit in your 4GB storage
3. **Action**: Upgrade Seedr account or find a smaller version

### Scenario 2: Downloading a TV Series (Multiple Files)

**Problem**: A TV series torrent with 10 episodes, each 3GB (30GB total).

**Solution**: ✅ This works perfectly!

```bash
python3 cli.py -e your@email.com -p yourpassword \
  --chunk-download-size 1.5 \
  --delete-after-download
```

**What happens**:
1. Seedr downloads Episode 1 (3GB) - fits in 4GB storage
2. AutoSeedr downloads Episode 1 in 2 chunks (1.5GB each)
3. Chunks are reassembled into Episode1.mp4
4. Episode 1 is deleted from Seedr (frees up 3GB)
5. Seedr downloads Episode 2... repeat
6. All 10 episodes downloaded successfully!

### Scenario 3: Downloading a 3.5GB Video File

**Problem**: File is larger than typical chunk size but fits in Seedr storage.

**Solution**: ✅ Perfect use case for chunked download!

```bash
python3 cli.py -e your@email.com -p yourpassword --chunk-download-size 1.0
```

**What happens**:
1. Seedr downloads the 3.5GB file
2. AutoSeedr downloads it in 4 chunks (1GB each)
3. Chunks: file.mp4.part0, file.mp4.part1, file.mp4.part2, file.mp4.part3
4. Reassembled into final file: file.mp4
5. Chunks are automatically deleted
6. Final file is ready to use with correct extension!

## Technical Details

### Chunk Reassembly Process

1. **Download Phase**:
   ```
   video.mp4.part0 (2GB) - downloading in parallel
   video.mp4.part1 (2GB) - downloading in parallel
   video.mp4.part2 (2GB) - downloading in parallel
   video.mp4.part3 (1GB) - downloading in parallel
   ```

2. **Reassembly Phase**:
   ```
   Reading part0... writing to video.mp4
   Reading part1... appending to video.mp4
   Reading part2... appending to video.mp4
   Reading part3... appending to video.mp4
   Deleting temporary .part files...
   Done! video.mp4 ready (7GB total)
   ```

3. **File Extension Preservation**:
   - Original file: `movie.mp4`
   - Chunks: `movie.mp4.part0`, `movie.mp4.part1`, etc.
   - Final file: `movie.mp4` (extension preserved)

### HTTP Range Request Headers

AutoSeedr uses standard HTTP Range headers:

```
Range: bytes=0-2147483647          (First 2GB chunk)
Range: bytes=2147483648-4294967295  (Second 2GB chunk)
Range: bytes=4294967296-6442450943  (Third 2GB chunk)
...
```

## Troubleshooting

### "Server doesn't support Range requests"

**Cause**: The download server doesn't support partial content requests.

**Solution**: AutoSeedr automatically falls back to standard download. No action needed.

### "Chunk reassembly error"

**Cause**: A chunk file is missing or corrupted.

**Solution**:
1. Check your disk space
2. Check network stability
3. Retry the download
4. Reduce `--max-workers` to avoid overwhelming your connection

### "File too large for Seedr storage"

**Cause**: Individual file >4GB in the torrent.

**Solution**:
1. Upgrade your Seedr account
2. Find a different torrent with smaller files
3. Use a different cloud torrent service

### Downloaded file won't play

**Cause**: Reassembly failed or incomplete download.

**Solution**:
1. Check if all `.part` files were downloaded completely
2. Verify file size matches expected size
3. Re-download the file
4. Check for disk space during reassembly

## Performance Tips

1. **Optimal Chunk Size**:
   - For 4GB Seedr: Use 1-2GB chunks
   - For faster networks: Smaller chunks (0.5-1GB) for better parallelization
   - For slower networks: Larger chunks (2-3GB) to reduce overhead

2. **Max Workers**:
   - Fast connection (100+ Mbps): 6-8 workers
   - Medium connection (20-100 Mbps): 4 workers
   - Slow connection (<20 Mbps): 2 workers

3. **Delete After Download**:
   - Always enable for multi-file torrents
   - Disable if you want to keep files on Seedr

## Frequently Asked Questions

**Q: Can I pause and resume chunked downloads?**
A: Not currently. If interrupted, the download will restart. Future versions may add resume support.

**Q: Does this work with magnet links?**
A: Yes! Seedr handles magnet links, and once downloaded to Seedr, AutoSeedr downloads them normally.

**Q: Will chunk files take up double the space?**
A: Temporarily yes. During reassembly, both chunks and final file exist. Chunks are deleted immediately after successful reassembly.

**Q: Can I download to multiple computers simultaneously?**
A: Yes! Each computer can download different files from the same Seedr torrent.

**Q: Does this reduce Seedr bandwidth usage?**
A: No. Total data transferred is the same. However, parallel chunks can maximize your connection speed.

## Support

For issues or questions:
- GitHub Issues: [https://github.com/Pasanlaksitha/AutoSeedr/issues](https://github.com/Pasanlaksitha/AutoSeedr/issues)
- Check logs: `auto_seedr_cli.log`

## License

This feature is part of AutoSeedr and follows the same license as the main project.
