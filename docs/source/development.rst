.. _development:

Development
============


.. _development.installing:

Installing for Development
--------------------------

To setup awslimitchecker for development:

1. Fork the `awslimitchecker <https://github.com/jantman/awslimitchecker>`_ repository on GitHub

2. Create a `virtualenv` to run the code in:

.. code-block:: bash

    $ virtualenv awslimitchecker
    $ cd awslimitchecker
    $ source bin/activate

3. Clone your fork and install it in the virtualenv

.. code-block:: bash

    $ git clone https://github.com/YOUR_NAME/awslimitchecker src/awslimitchecker
    $ cd src/awslimitchecker
    $ python setup.py develop

4. Check out a new git branch. If you're working on a GitHub issue you opened, your
   branch should be called "issues/N" where N is the issue number.


.. _development.guidelines:

Guidelines
-----------

* pep8 compliant with some exceptions (see pytest.ini)
* 100% test coverage with pytest (with valid tests)
* each :py:class:`~awslimitchecker.services.base.AwsService` subclass
  should only connect to boto once, and should save the connection as ``self.conn``.


.. _development.adding_checks:

Adding New Checks to Existing Services
---------------------------------------

TODO


.. _development.adding_services:

Adding New Services
--------------------

All Services are sublcasses of :py:class:`~awslimitchecker.services.base.AwsService`
using the :py:mod:`abc` module.

1. In ``awslimitchecker.services`` copy ``base.py`` to ``new_service_name.py``.
2. Change the file path on line 2 in the docstring, the class name, and the
   ``service_name`` class attribute.
3. Add an import line for the new service in ``awslimitchecker/services/__init__.py``.
4. Write at least high-level tests; TDD is greatly preferred.
5. Implement all abstract methods from :py:class:`~awslimitchecker.services.base.AwsService`.
6. Test your code; 100% test coverage is expected, and mocks should be using ``autospec`` or ``spec_set``.
7. TBD - write integration tests.
8. Run all tox jobs, or at least one python version, docs and coverage.
9. Submit your pull request.

.. _development.adding_ta:

Adding Trusted Advisor Checks
------------------------------

TODO

.. _development.tests:

Unit Testing
-------------

Testing is done via `pytest <http://pytest.org/latest/>`_, driven by `tox <http://tox.testrun.org/>`_.

* testing is as simple as:

  * ``pip install tox``
  * ``tox``

* If you want to see code coverage: ``tox -e cov``

  * this produces two coverage reports - a summary on STDOUT and a full report in the ``htmlcov/`` directory

* If you want to pass additional arguments to pytest, add them to the tox command line after "--". i.e., for verbose pytext output on py27 tests: ``tox -e py27 -- -v``

Note that while boto currently doesn't have python3 support, we still run tests against py3 to ensure that this package
is ready for it when boto is.


.. _development.integration_tests:

Integration Testing
--------------------

TBD.


.. _development.docs:

Building Docs
-------------
Much like the test suite, documentation is build using tox:

.. code-block:: bash

    $ tox -e docs

Output will be in the ``docs/build/html`` directory under the project root.

.. _development.release_checklist:

Release Checklist
-----------------

1. Open an issue for the release; cut a branch off master for that issue.
2. Confirm that there are CHANGES.rst entries for all major changes.
3. Ensure that Travis tests passing in all environments.
4. Ensure that test coverage is no less than the last release (ideally, 100%).
5. Increment the version number in awslimitchecker/version.py and add version and release date to CHANGES.rst, then push to GitHub.
6. Confirm that README.rst renders correctly on GitHub.
7. Upload package to testpypi, confirm that README.rst renders correctly.

   * Make sure your ~/.pypirc file is correct
   * ``python setup.py register -r https://testpypi.python.org/pypi``
   * ``python setup.py sdist upload -r https://testpypi.python.org/pypi``
   * Check that the README renders at https://testpypi.python.org/pypi/awslimitchecker

8. Create a pull request for the release to be merge into master. Upon successful Travis build, merge it.
9. Tag the release in Git, push tag to GitHub:

   * tag the release. for now the message is quite simple: ``git tag -a vX.Y.Z -m 'X.Y.Z released YYYY-MM-DD'``
   * push the tag to GitHub: ``git push origin vX.Y.Z``

11. Upload package to live pypi:

    * ``python setup.py sdist upload``

10. make sure any GH issues fixed in the release were closed.
