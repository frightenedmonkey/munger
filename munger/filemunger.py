# -*- coding: utf-8 -*-

import sys, subprocess, os, shutil
import csv
import datamunger

class fileManager(object):
	def __init__(self):
		self.home_path = os.environ['HOME']
		self.backup = self.home_path + "/.munger/hosts_backup.bak"	
		# Initialize the database object for use by file manager
		self.dbstuff = datamunger.dataManager()
		# check for the backup, and create if it doesn't exist. Bad comments.
		backup_data = self.dbstuff.get_backup_file()
		if not backup_data:		
			try:
				shutil.copy('/etc/hosts', self.home_path + "/.munger/hosts_backup.bak")
				self.dbstuff.record_backup_data(self.home_path + '/.munger/hosts_backup.bak')
			except IOError:
				print "Oops, trouble backing up your hosts file. Check write permissions in the home directory and try running this again."
				sys.exit(1)
		else:
			pass

	def activate_hosts_set(self, set_to_activate):
		# Change the active set data
		if not self.dbstuff.make_set_active(set_to_activate):
			return False
		else:
			temp_file = self._append_sets_to_temp(set_to_activate)
			if self._copy_to_etc_hosts(temp_file):
				return True
			else:
				return False

	def deactivate_hosts(self):
		"""This method calls a couple other methods to: 
		1. Create a temp file from backup (let's never touch the backup directly) 
			(gets a string for the file location backup in the db); 
		2. Copies over the temp file to /etc/hosts
		3. Flushes the local DNS cache. 
		Returns True if all successful
		Returns False if things fail (most likely because this wasn't run as root."""
		temp_file = self._create_temp_file_from_backup()
		if self._copy_to_etc_hosts(temp_file):
			self.dbstuff.make_all_sets_inactive()
			return True
		else:
			return False
			
	def _create_temp_file_from_backup(self):
		shutil.copy(self.backup, self.home_path + '/.munger/hosts_temp.bak')
		temp_file = self.home_path + '/.munger/hosts_temp.bak'
		return temp_file

	def _append_sets_to_temp(self, set_to_activate):
		list_of_ips = self.dbstuff.get_all_ip_entries_for_set(set_to_activate)
		temp_location = self._create_temp_file_from_backup ()
		with open(temp_location, 'a') as temp_file:
			for row in list_of_ips:
				entries = '\t'
				entries = entries.join(row)
				temp_file.write(entries + '\n')
		return temp_location

	def _copy_to_etc_hosts(self, file_to_copy, deactivate=False):
		if file_to_copy == None:
			return False
		else:
			try:
				shutil.copy(file_to_copy, '/etc/hosts') # copy tempfile to replace /etc/hosts
				# flush the local dns cache. Don't care too much about the return code — 
				# it's a simple call on the mac, need to find out how to do this on linux and windows, and whatnot
				# As a side note, probably need to change this to make it cross-OS. For now, laziness.
				try:
					subprocess.call(["dscacheutil", "-flushcache"]) 
				except Exception:
					pass
				return True
			except IOError:
				print "You must run this command with sudo; please retry as such. Hint: just type 'sudo !!'."
				if deactivate == False:
					self.dbstuff.make_all_sets_inactive()
				return False

	#def import_csv_file(self, csv_file_path):
	#	with open(csv_file_path)
