import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='proposal.concurrent.futures.scheduled',
    version='1.0.1',
    author="Ivan Usalko",
    author_email="ivict@rambler.ru",
    description="Scheduled thread executor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/usalko/proposal_concurrent_futures_scheduled",
    packages=setuptools.find_packages(),
    license='Apache License, Version 2.0 (Apache-2.0)',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
