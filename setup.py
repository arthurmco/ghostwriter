from setuptools import setup, find_packages

setup(
    name="ghostwriter",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask', "six", "enum34", 'flask_login', 'flask_sqlalchemy'
    ],
    test_suite='ghostwriter.test',
)
