#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
sys.path.insert(0, os.path.abspath('..'))
import datamunger
import unittest

class dataTester (unittest.TestCase):
	def setUp(self):
		self.dbstuff = datamunger.dataManager(test=True)
		self.home_path = os.environ['HOME'] + '/.munger/test.db'

	def tearDown(self):
		self.dbstuff.close_connection()
		if not os.path.exists(self.home_path):
			print "All the tests that just ran should not have been successful. You were running without a test.db file. FAIL."
		else:
			os.remove(self.home_path)
	
	def test_does_init_create_test_db(self):
		self.assertTrue(os.path.exists(self.home_path))

	def test_can_write_and_retrieve_single_ip_entry(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'blammer.com', 'this_test_set')
		test_results = self.dbstuff.get_all_ip_entries_for_set('this_test_set')
		test_compare = [['10.10.10.10', 'blammer.com']]
		self.assertEqual(test_compare, test_results)

	def test_can_get_all_ips_for_set(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'blammer.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.11', 'blammer2.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.12', 'blammer3.com', 'this_test_set')
		test_results = self.dbstuff.get_all_ip_entries_for_set('this_test_set')
		test_compare = [['10.10.10.10', 'blammer.com'],['10.10.10.11', 'blammer2.com'],['10.10.10.12', 'blammer3.com']]
		self.assertEqual(test_compare, test_results)

	def test_no_ips_returns_false(self):
		self.assertFalse(self.dbstuff.get_all_ip_entries_for_set('some_random_text'))
		
	def test_no_sets_returns_false(self):
		self.assertFalse(self.dbstuff.get_all_sets())

	def test_all_sets_are_returned(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'blammer.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.11', 'blammer2.com', 'this_test_set2')
		self.dbstuff.write_single_ip_entry('10.10.10.12', 'blammer3.com', 'this_test_set3')
		test_results = self.dbstuff.get_all_sets()
		test_comparison = [['this_test_set'],['this_test_set2'],['this_test_set3']]
		self.assertEqual(test_results, test_comparison)
	
	def test_no_active_set_returns_false(self):
		self.assertFalse(self.dbstuff.get_active_set())

	def test_already_active_set_returns_false(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'blammer.com', 'this_test_set')
		self.dbstuff.make_set_active('this_test_set')
		self.assertFalse(self.dbstuff.make_set_active('this_test_set'))

	def test_activated_set_is_correctly_returned(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'blammer.com', 'this_test_set')
		self.dbstuff.make_set_active('this_test_set')
		result = self.dbstuff.get_active_set()
		self.assertEqual(result, [['this_test_set']])
	
	def test_nonexistent_set_returns_false(self):
		self.assertFalse(self.dbstuff.make_set_active('oogie-boogie'))

	def test_correct_active_set_returned_after_multi_activations(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'blammer.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.11', 'blammer2.com', 'this_test_set2')
		self.dbstuff.write_single_ip_entry('10.10.10.12', 'blammer3.com', 'this_test_set3')
		self.dbstuff.make_set_active('this_test_set')
		self.dbstuff.make_set_active('this_test_set2')
		result = self.dbstuff.get_active_set()
		self.assertEqual(result, [['this_test_set2']])

	def test_all_sets_can_be_made_inactive(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'blammer.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.11', 'blammer2.com', 'this_test_set2')
		self.dbstuff.write_single_ip_entry('10.10.10.12', 'blammer3.com', 'this_test_set3')
		self.dbstuff.make_set_active('this_test_set')
		self.dbstuff.make_all_sets_inactive()
		self.assertFalse(self.dbstuff.get_active_set())

	def test_ip_addresses_can_be_updated(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'blammer.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.11', 'blammer2.com', 'this_test_set2')
		self.dbstuff.update_single_ip_address('blammer.com', '10.10.10.12', 'this_test_set')
		result = self.dbstuff.get_all_ip_entries_for_set('this_test_set')
		self.assertEqual(result, [['10.10.10.12', 'blammer.com']])

	def test_does_empty_backup_location_return_false(self):
		self.assertFalse(self.dbstuff.get_backup_file())

	def test_can_backup_location_be_written(self):
		self.dbstuff.record_backup_data('/jim/jam/bazoo.bak')
		self.assertEqual(self.dbstuff.get_backup_file(), '/jim/jam/bazoo.bak')

	def test_can_backup_location_be_updated(self):
		self.dbstuff.record_backup_data('/jim/jam/bazoo.bak')
		self.dbstuff.record_backup_data('/flim/flam/kazoo.bak')
		self.assertEqual(self.dbstuff.get_backup_file(), '/flim/flam/kazoo.bak')

	def test_can_remove_all_ips_for_a_set(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'hugo.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.11', 'dexter.com', 'this_test_set2')
		self.dbstuff.write_single_ip_entry('10.10.10.13', 'buster.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.14', 'marshall.com', 'this_test_set2')
		self.dbstuff.delete_all_ips_for_set('this_test_set')
		self.assertFalse(self.dbstuff.get_all_ip_entries_for_set('this_test_set'))

	def test_delete_nonexistent_set(self):
		self.assertFalse(self.dbstuff.delete_all_ips_for_set('blahblahblah'))

	def test_can_delete_the_active_set(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'hugo.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.11', 'dexter.com', 'this_test_set2')
		self.dbstuff.write_single_ip_entry('10.10.10.13', 'buster.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.14','marshall.com', 'this_test_set2')
		self.dbstuff.make_set_active('this_test_set')
		self.dbstuff.delete_all_ips_for_set('this_test_set')
		self.assertFalse(self.dbstuff.get_active_set())

	def test_can_remove_single_ip(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'hugo.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.11', 'dexter.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.13', 'buster.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.14','marshall.com', 'this_test_set')
		self.dbstuff.remove_single_ip_address('buster.com', 'this_test_set')
		test_results = self.dbstuff.get_all_ip_entries_for_set('this_test_set')
		self.assertEqual(test_results, [['10.10.10.10', 'hugo.com'],['10.10.10.11', 'dexter.com'],['10.10.10.14','marshall.com']])

	def test_remove_nonexistent_host_returns_false(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'hugo.com', 'this_test_set')
		self.assertFalse(self.dbstuff.remove_single_ip_address('buster.com', 'this_test_set'))

	def test_no_dupes_for_sets(self):
		self.dbstuff.write_single_ip_entry('10.10.10.10', 'hugo.com', 'this_test_set')
		self.dbstuff.write_single_ip_entry('10.10.10.11', 'dexter.com', 'this_test_set')
		test_results = self.dbstuff.get_all_sets()
		self.assertEqual(len(test_results), 1)

if __name__ == '__main__':
	unittest.main()
