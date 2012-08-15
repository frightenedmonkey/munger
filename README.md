Munger
======
Munger is a sqlite3-based wrapper around your hosts file. The intent is for the user to be able to add sets of IP addresses and associated hostnames that can be activated and deactived as the user desires. 

Usage Instructions
------------------

* `munger add-ip <hostname> <ip-address> <set>` New sets are automatically added. All arguments must be present
* `munger sets` Lists all currently available sets
* `munger list-ips <set>` Lists all IPs and hostnames for a given set
* `munger import <file.csv>` Imports CSV file with header of hostname,ip,set NOT YET IMPLEMENTED
* `munger help` Displays usage instructions 
* `munger activate <set>` Activates a set of IPs in the hosts file. *Must be run as root*, otherwise it won't succeed.
* `munger revert` Restores the backed up hosts file. Must be run as root.
* `munger delete <set>` Deletes all IP and hostname entries associated with a given set.
* `munger rip <hostname> <set>` Removes the specified hostname entry (and associated IP address) from the given set.
* `munger active` Lists the currently active set and all of its associated IP addresses and hostnames.`

Background
----------
This project was mostly done as a learning exercise, but also because I wanted a tool like this. I have to think it'd be handy for web developers in general, too.

Installation
------------

To install, download the source, and run 'python setup.py install'. The munger CLI app will then be available like any other command line app. The modules will be available for your python programs, but I'm not sure why you would want to use them — they're all too tied to munger to be generically useful at this point.

TBD:
* Add hostname dupe checking while writing IPs and hostnames
* Support for linux and windows (currently only supports Mac OS X)
* Finish the csv import functionality
* When removing sets, if that set is active, revert the hosts file to the original
* When removing individual IPs, if it's part of a set that's active, remove the IP from the hosts file
* When removing the last IP in a set, the set should be deleted, too.
* Other ideas? Requests?

Known Issues:
* Fixed the one outstanding issue related to cleaning up the db when failing to run activate as sudo.
