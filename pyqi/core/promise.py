import inspect

class Promise():


    def __init__(self, in_):
        self.success = None
        self.value = None
        self.successors = []
        self.failures = []
        self.continuation_listeners = {}

        if callable(in_):
            try:
                if len(inspect.getargspec(in_)[0]) == 0:
                    self.value = in_()
                    self.success = True
                elif len(inspect.getargspec(in_)[0]) == 1:
                    in_(self._success)
                elif len(inspect.getargspec(in_)[0]) > 1:
                    in_(self._success, self._failure)

            except Exception as e:
                self._failure(e)
        else:
            self.value = in_
            self.success = True


    @staticmethod
    def from_async_result(async_result):
        pass



    @staticmethod
    def all(promise_list):
        completion_table = {}
        promises_left = 0;
        for promise in promise_list:
            completion_table[promise] = None
            promises_left += 1

        new_promise = new Promise()

        def check_completion(promise, is_success, value):
            if not is_success:
                new_promise._failure(value)
                promises_left = -1
            elif promises_left > 0:
                completion_table[promise] = value
                promises_left -= 1

                if promises_left == 0:
                    new_promise._success([completion_table[p] for p in promise_list])


        for promise in promise_list:
            def handle_factory(is_success):
                def handle(value):
                    completion_table[promise]['success'] = is_success
                    completion_table[promise]['value'] = value
                    check_completion(promise, is_success, value)
                    return value
                return handle

            promise.then(handle_factory(True), handle_factory(False))

        return new_promise


    def then(self, success, failure):

        if self.success is None:
            self.successors.append(success)
            self.failures.append(failure)
        else:
            if self.success:
                success(self.value)
            else:
                failure(self.value)

        # resolve and reject are the new class's self._success and self._failure
        def continuation(resolve, reject):
            def success_(value):
                if value is not None:
                    resolve(value)
                else:
                    resolve(self.value)
            def failure_(value):
                reject(self.value)

            self.continuation_listeners[success] = success_
            self.failures.append(failure_)



        return Promise(continuation)

    def _success(self, value):
        self.success = True
        self.value = value
        for listener in self.successors:
            continuation_result = listener(value) 
            self.continuation_listeners[listener](continuation_result)


    def _failure(self, error):
        self.success = False
        self.value = error
        for listener in self.failures:
            listener(value)
