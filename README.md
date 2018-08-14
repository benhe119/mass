MASS - Malware Analyst's Storage System

Simple web application to manage files for malware analysts.

- uploaded files are checksummed and typed using libmagic
- folders can be added and scanned in the background
- files included in a PCAP are extracted using bro (broids.org)
- supported archives are extracted using 7zip and extracted files are added automatically

Production:

TODO

Testing/Development:

TODO


Future Plans

- integrate with VirusTotal to automatically check hashes
- integrate more analysis (pefile, leef, etc)
- add tagging system
