from unittest import TestCase, main
from pyqi.core.promise import Promise

class TestPromise(TestCase):

    def do_continuation(self, p, success_list, failure_list):
        for success, failure in zip(success_list, failure_list):
            p = p.then(success, failure)

        return p

    def check_success_no_modification(self, in_, expected):
        self.count = 0

        def success(v):
            self.count += 1
            self.assertEqual(expected, v)

        def failure(e):
            # This should not be called, this assert is not indicitive of the real error.
            # The real error is that failure() was executed at all.
            self.assertEqual(True, False)

        p = Promise(in_)
        p.then(success, failure)

        p = self.do_continuation(p, 
            [success, success, success],
            [failure, failure, failure])


        p.then(success, failure)
        p.then(success, failure)

        self.assertEqual(6, self.count)

    def check_failure(self, in_):
        self.count = 0;

        def success(v):
            # This should not be called, this assert is not indicitive of the real error.
            # The real error is that sucess() was executed at all.
            self.assertEqual(True, False)

        def failure(e):
            self.count += 1
            self.assertRaises(Exception)

        p = Promise(in_)
        p.then(success, failure)

        p = self.do_continuation(p, 
            [success, success, success],
            [failure, failure, failure])


        p.then(success, failure)
        p.then(success, failure)

        self.assertEqual(6, self.count)


    def test_success_no_modification_direct_value(self):
        self.check_success_no_modification("This is a string", "This is a string")
        self.check_success_no_modification(41, 41)

    def test_success_no_modification_callable_no_param(self):
        def callable_no_param():
            return "This is a string"
        self.check_success_no_modification(callable_no_param, "This is a string")

    def test_success_no_modification_callable_single_param(self):
        def callable_single_param(success):
            success(31)
        self.check_success_no_modification(callable_single_param, 31)

    def test_success_no_modification_callable_all_params(self):
        def callable_many_param(success, failure):
            success(31)
        self.check_success_no_modification(callable_many_param, 31)


    def test_failure_no_modification_callable_no_param(self):
        def callable_no_param():
            raise Exception("This should trigger failure()")
        self.check_failure(callable_no_param)

    def test_failure_no_modification_callable_single_param(self):
        def callable_single_param(success):
            raise Exception("This should trigger failure()")
        self.check_failure(callable_single_param)

    def test_failure_no_modification_callable_all_params(self):
        def callable_many_param(success, failure):
            failure(Exception("This should trigger failure()"))
        self.check_failure(callable_many_param)



    def test_function_without_params_continuation(self):
        def no_param_callable():
            return 1

        def success1(v):
            self.assertEqual(v, 1)
            return v + 1

        def success2(v):
            self.assertEqual(v, 2)
            return v + 1

        def success3(v):
            self.assertEqual(v, 3)

        def failure(e):
            # This should not be called, this assert is not indicitive of the real error.
            # The real error is that failure() was executed at all.
            self.assertEqual(True, False)

        p = self.do_continuation(Promise(no_param_callable), 
            [success1, success2, success3], 
            [failure , failure , failure ])

        p.then(success3, failure)
        p.then(success3, failure)
        p.then(success3, failure)


    def test_function_with_params_continuation_complex(self):
        def no_param_callable(success, failure):
            success(1)

        def success1(v):
            self.assertEqual(v, 1)
            return v + 1

        def success2(v):
            self.assertEqual(v, 2)
            return v + 1

        def success3(v):
            raise Exception("This should trigger failure2")

        def success4(v):
            # This should not be called, this assert is not indicitive of the real error.
            # The real error is that success4() was executed at all.
            self.assertEqual(True, False)

        def failure1(e):
            # This should not be called, this assert is not indicitive of the real error.
            # The real error is that failure1() was executed at all.
            self.assertEqual(True, False)

        def failure2(e):
            self.assertRaises(Exception)


        #Expected path: s1 -> s2 -> s3 -> f2
        p = self.do_continuation(Promise(no_param_callable), 
            [success1, success2, success3, success4], 
            [failure1, failure1, failure1, failure2])


if __name__ == '__main__':
    main()