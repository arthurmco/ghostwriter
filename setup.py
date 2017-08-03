from setuptools import setup, find_packages

setup(
    name="ghostwriter",
    version="0.0.2",
    author="Arthur M",
    description="a simple article/blog management tool of which *you* show how to show",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask', "six", "enum34", 'flask_login', 'flask_sqlalchemy'
    ],
    test_suite='ghostwriter.ghtest',
)
