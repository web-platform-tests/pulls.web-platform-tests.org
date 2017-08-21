from setuptools import setup, find_packages


setup(
    name='wptdash',
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        'flask', 'flask-sqlalchemy', 'flask-migrate', 'flask-script',
        'jsonschema', 'pyOpenSSL', 'requests', 'requests-cache',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest', 'pytest-cov', 'pytest-mock'
    ],
    python_requires='>=3',
)
