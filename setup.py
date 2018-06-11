import io

from setuptools import find_packages, setup

# with io.open('README.rst', 'rt', encoding='utf8') as f:
#     readme = f.read()

setup(
    name='ResearchHelper',
    version='1.0.0',
    url='',
    license='BSD',
    maintainer='Wikty',
    maintainer_email='wiktymouse@gmail.com',
    description='A helper tool for improve research work.',
    # long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'sqlalchemy',
        'flask-sqlalchemy',
        'flask-wtf',
        'wtforms-alchemy'
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
    setup_requires=[
        "pytest-runner"
    ],
    tests_require=["pytest"]
)