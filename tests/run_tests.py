import unittest
import coverage

# Start code coverage
cov = coverage.Coverage(
    branch=True,
    include=['app/*'],
    omit=['tests/*', '*/templates/*']
)
cov.start()

# Load test suites
test_loader = unittest.TestLoader()
test_suite = test_loader.discover('tests', pattern='test_*.py')

# Run tests
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(test_suite)

# Stop coverage and generate report
cov.stop()
cov.save()
cov.report()
cov.html_report(directory='coverage_report')