#!/usr/bin/env python3
import pathlib
import sys
import unittest

sys.path.append(pathlib.Path.cwd().parent.parent.__str__())
from sharedlib import error_handling

class ErrcodeHandlerTest(unittest.TestCase):

    def setUp(self):
        self.errcode_handler = error_handling.ErrcodeHandler()
        self.mod_name = "test_mod"

    def tearDown(self):
        self.errcode_handler = None

    def test_rng_can_generate(self):
        module = error_handling.ErrcodeModule()
        module.errcodes[1] = error_handling.Errcode("Test1", "Test is 1", 1)
        module.errcodes[2] = error_handling.Errcode("Test2", "Test is 2", 2)


        num = error_handling.ErrcodeHandler.generateErrcode(module)
        self.assertTrue(num <= error_handling.ErrcodeHandler.RNG_MAX_INT_VALUE)
        self.assertTrue(num >= error_handling.ErrcodeHandler.RNG_MIN_INT_VALUE)

    def test_errcode_add_with_num(self):
        errcode = None
        module = None
        name = "Test1"
        message = "This is Test 1"
        number = 1

        retval = self.errcode_handler.registerErrcode(
            mod_name = self.mod_name,
            name = name,
            message = message,
            number = number
        )

        self.assertEqual(retval, number)

        self.assertTrue(len(self.errcode_handler.modules) != 0)
        module = self.errcode_handler.modules.get(self.mod_name)
        self.assertTrue(module is not None)
        retval = module.errcodes_key_name.get(name)
        self.assertTrue(retval is not None)
        self.assertEqual(retval, number)

        retval = module.errcodes.get(number)
        self.assertTrue(retval is not None)

        self.assertEqual(retval.name, name)
        self.assertEqual(retval.number, number)
        self.assertEqual(retval.message, message)

    def test_errcode_add_without_num(self):
        #Hello
        name = "Test1"
        message = "This is Test 1"
        number = None
        module = None
        retval = None

        number = self.errcode_handler.registerErrcode(
                    mod_name = self.mod_name,
                    name = name,
                    message = message
                )

        self.assertTrue(number <= error_handling.ErrcodeHandler.RNG_MAX_INT_VALUE)
        self.assertTrue(number >= error_handling.ErrcodeHandler.RNG_MIN_INT_VALUE)

        self.assertTrue(len(self.errcode_handler.modules) != 0)
        module = self.errcode_handler.modules.get(self.mod_name)
        self.assertTrue(module is not None)
        retval = module.errcodes_key_name.get(name)
        self.assertTrue(retval is not None)
        self.assertEqual(retval, number)

        retval = module.errcodes.get(number)
        self.assertTrue(retval is not None)

        self.assertEqual(retval.name, name)
        self.assertEqual(retval.number, number)
        self.assertEqual(retval.message, message)

    
    def test_register_mod_name_none(self):
        self.assertRaises(ValueError, 
                              self.errcode_handler.registerErrcode,
                              None,
                              "Test1",
                              "This is Test 1",
                              1
                          ) 


    def test_register_name_none(self):
        self.assertRaises(ValueError,
                              self.errcode_handler.registerErrcode,
                              self.mod_name,
                              None,
                              "This is Test 1",
                              1
                          )

    def test_register_message_none(self):
        self.assertRaises(ValueError,
                              self.errcode_handler.registerErrcode,
                              self.mod_name,
                              "Test1",
                              None,
                              1
                         )

 
    def test_getmessage_success_number_input(self):
        name = "Test1"
        message = "This is Test 1"
        number = 1
        self.errcode_handler.registerErrcode(
                    self.mod_name,
                    name,
                    message,
                    number
                )

        retval = self.errcode_handler.getMessage(self.mod_name, number)
        self.assertEqual(message, retval)


    def test_getmessage_success_name_input(self):
        name = "Test1"
        message = "This is Test 1"
        number = 1
        self.errcode_handler.registerErrcode(
                    self.mod_name,
                    name,
                    message,
                    number
                )

        #Why is this failing?
        retval = self.errcode_handler.getMessage(self.mod_name, name)
        self.assertEqual(message, retval)


class DieFunctionText(unittest.TestCase):

    def setUp(self):
        self.errcode_handler = error_handling.ErrcodeHandler()
        self.mod_name = "test_mod"
        self.errcode_name = "test1"
        self.errcode_message = "This is test1"
        self.errcode_number = 1
        try:
            error_handling.ErrcodeHandler.instance.registerErrcode(
                                             self.mod_name,
                                             self.errcode_name,
                                             self.errcode_message,
                                             self.errcode_number
                                            )
        except ValueError as err:
            pass


    def tearDown(self):
        self.errcode_handler = None

    def test_success_number_input(self):
        with self.assertRaises(SystemExit):
            error_handling.die(self.mod_name, self.errcode_number)


    def test_success_name_input(self):
        with self.assertRaises(SystemExit):
            error_handling.die(self.mod_name, self.errcode_name)


    def test_mod_name_none(self):
        self.assertRaises(ValueError,
                              error_handling.die,
                              None,
                              self.errcode_number
                          )


    def test_errcode_input_none(self):
        self.assertRaises(ValueError,
                              error_handling.die,
                              self.mod_name,
                              None
                          )

if __name__ == "__main__":
    unittest.main(exit=False)


