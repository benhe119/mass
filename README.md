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


Short Term TODOs:

- TODO: improve views.py and tasks.py coverage
- TODO: reduce reliance on files already present, i.e. create and delete files/folders in the tests
- TODO: make a temp path and us os/pathlib to manage dirs when extracting PCAPs
- TODO: add test_forms.py
- TODO: determine why "from .tasks import extract_pcap, scan_folder" is necessary in views.py
- TODO: abstract common code from FileList and FolderList in views.py
- TODO: abstract common code from FileList and FolderList in forms.py
- TODO: abstract tearDown() method from TestCase classes
