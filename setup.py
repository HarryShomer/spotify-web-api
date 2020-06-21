import os
from setuptools import setup


def read():
    return open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name='spotify_web_api',
    version='0.0.2',
    description="""An extremely minimal client library for the spotify web api""",
    long_description=read(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
    ],
    keywords='Spotify',
    url='https://github.com/HarryShomer/spotify-web-api',
    author='Harry Shomer',
    author_email='Harryshomer@gmail.com',
    license='MIT',
    packages=['spotify_web_api'],
    install_requires=['requests', 'pytest'],
    include_package_data=True,
    zip_safe=False
)