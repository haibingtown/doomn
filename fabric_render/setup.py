from setuptools import setup, find_packages

setup(
    name='fabric_render',
    version='0.1',
    description='fabric_render',
    author='doomn',
    packages=find_packages(),
    install_requires=[
        'requests', 'aiohttp'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
