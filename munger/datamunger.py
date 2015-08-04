# -*- coding: utf-8 -*-

import sqlite3
import sys
import os 

class dataManager(object):
    """Handles all the SQLite operations for munger. Creates the needed tables if they don't exist on startup. """
    def __init__(self, test=False):
        # Open the database, and create the tables for munger if they don't exist
        home_path = os.environ['HOME'] + '/.munger/'
        if not os.path.isdir(home_path):
            try:
                os.makedirs(home_path)
            except OSError:
                print "Hmmm, there was a directory creation error; check ~/.munger/"
                sys.exit(1)
        if not test:
            file_path = home_path + 'munger.db'
            self._create_db(file_path)
        else:
            file_path = home_path + 'test.db'
            self._create_db(file_path)

    def _create_db(self, file_path):
        try:
            self.conn = sqlite3.connect(file_path)
            self.curs = self.conn.cursor()
            self.curs.execute("CREATE TABLE IF NOT EXISTS addresses (ip text, hostname text, ip_sets text)")
            self.curs.execute("CREATE TABLE IF NOT EXISTS sets (ip_sets text UNIQUE, active integer)")
            self.curs.execute("CREATE TABLE IF NOT EXISTS backup_data (hostsfile_backup_location text)")
            self.conn.commit()
            if 'test' in file_path:
                print "Loaded and initialized the munger TEST database."
            else:
                print "Loaded and initialized the munger database."
        except sqlite3.Error, e:
            print "Uh oh, the database failed to initialize. Something has gone horribly, horribly wrong: ", e.args[0]
            sys.exit(1)

    def write_single_ip_entry(self, ip, hostname, which_set):
        all_the_data = ip, hostname, which_set
        set_name = (which_set, 0)
        try:
            self.curs.execute("INSERT INTO addresses VALUES (?, ?, ?)", all_the_data)
            self.curs.execute("INSERT OR IGNORE INTO sets VALUES (?, ?)", set_name)
            self.conn.commit()
            return True
        except sqlite3.Error, e:
            print "There was an error writing to the database: %s", e.args[0]
            return False

    def get_all_ip_entries_for_set(self, which_set):
        # reminder to self that sqlite3 module uses tuples for SELECT statements
        # so first thing we do is toss the set name into a tuple
        set_names_tuple = (which_set,)
        try:
            self.curs.execute("SELECT * FROM addresses where ip_sets=?", set_names_tuple)
            return self._db_record_sanitizer(self.curs.fetchall())
        except sqlite3.Error, e:
            print "Some sort of error occurred: ", e.args[0]
            return False

    def get_all_sets(self):
        """Method that queries the SQLite database for all sets that have been created. Returns a list with all set names, or False if no sets."""
        self.curs.execute("SELECT * FROM sets")
        all_entries = self.curs.fetchall()
        if not all_entries:
            return False
        else:
            return self._db_record_sanitizer(all_entries)

    def get_active_set(self):
        self.curs.execute("SELECT * FROM sets where active=1")
        entries = self.curs.fetchall()
        if not entries:
            return False	# E.g., no active sets
        else:
            return self._db_record_sanitizer(entries)

    def make_set_active(self, set_to_activate):
        set_name = (set_to_activate,)
        # Check if the set is already active
        active_list = self.get_active_set()
        # Check that there are IPs returned for that set name
        set_checker = self.get_all_ip_entries_for_set(set_to_activate) 
        if not set_checker: # Bail if no IPs associated with this setname
            print "There is no set by that name"
            return False
        elif (not active_list) or (set_to_activate != active_list[0][0]):
            # Only allows one set to be active at a time
            self.curs.execute("UPDATE sets SET active = 0 WHERE active = 1")
            # Not sure if I can stack executes before commit,
            # so I'll just commit between every transaction
            self.conn.commit()
            self.curs.execute("UPDATE sets SET active = 1 WHERE ip_sets = ?", set_name)
            self.conn.commit()
            return True
        elif set_to_activate == active_list[0][0]:
            print "That set is already active."
            return False

    def make_all_sets_inactive(self):
        self.curs.execute("UPDATE sets SET active = 0 WHERE active = 1")
        self.conn.commit()
        return True

    def update_single_ip_address(self, hostname, ip_address, which_set):
        # Expects the hostname to remain the same, but the IP to be changed
        addresses = ip_address, hostname, which_set
        try:
            self.curs.execute("UPDATE addresses SET ip = ? WHERE hostname = ? AND ip_sets = ?", addresses)
            self.conn.commit()
            return True
        except sqlite3.Error, e:
            print "Whoops, couldn't update that hostname, error: %s", e.args[0]
            return False

    def remove_single_ip_address(self, hostname, which_set):
        addresses = hostname, which_set
        # First check for the entry
        self.curs.execute("SELECT * FROM addresses where hostname = ? AND ip_sets = ?", addresses)
        results = self.curs.fetchall()
        if not results:
            print "There is no IP entry matching that hostname and set."
            return False
        else:
            try:
                self.curs.execute("DELETE FROM addresses WHERE hostname = ? AND ip_sets = ?", addresses)
                self.conn.commit()
                return True
            except sqlite3.Error, e:
                print "There was an error removing that entry: %s", e.args[0]

    def get_backup_file(self):
        # Just returns the backup location
        a = self.curs.execute("SELECT * FROM backup_data").fetchall()
        try:
            return a[0][0]
        except IndexError:
            return False

    def record_backup_data(self, file_backup_location):
        # create tuple, yo
        backup_stuff = (file_backup_location,)
        try:
            if self.get_backup_file():
                # THERE CAN BE ONLY ONE!
                self.curs.execute("DELETE FROM backup_data")
            else:
                pass
                self.curs.execute("INSERT INTO backup_data VALUES (?)", backup_stuff)
                self.conn.commit()
                return True
        except sqlite3.Error, e:
            print "Oh crap, I couldn't write that data: %s", e.args[0]
            return False

    def delete_all_ips_for_set(self, set_name):
        if not self.get_all_ip_entries_for_set(set_name):
            print "No set by that name."
            return False
        else:
            set_to_delete = (set_name,)
            try:
                self.curs.execute("DELETE FROM addresses WHERE ip_sets = ?", set_to_delete) 
                self.curs.execute("DELETE FROM sets WHERE ip_sets = ?", set_to_delete)
                self.conn.commit()
                print "Deleted all IP addresses and hostnames for set: " + set_name
                return True
            except sqlite3.Error, e:
                print "There was an error deleting the set: %s", e.args[0]
                return False

    def _db_record_sanitizer(self, all_records):
        """Cast the tuples to lists and pop the last entry.
        Last entries in the DB tables are, by design, to be for recordkeeping
        And are unneeded for writing to the hosts file or for presenting any info
        to the user."""
        return_list = []
        if not all_records:
            return False
        else:
            for a in all_records:
                a = list(a)
                a.pop() # this method returns the popped element, so don't directly append to the list
                return_list.append(a) # Order of records isn't important
                return return_list

    def close_connection(self):
        self.conn.close()
