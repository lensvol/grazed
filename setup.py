#codng: utf-8

from setuptools import setup

setup(name="grazed",
      version="1.0",
      description="Simple scraper for personal ticket info from  Russian Railways (RZD) website.",
      author="Kirill Borisov",
      author_email="lensvol@gmail.com",
      url="https://github.com/lensvol/grazed",
      packages=["grazed"],
      install_requires=[
          'requests==1.1.0'
      ],
      classifiers=[
          'Programming Language :: Python :: 2.6',
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License'
      ],
      entry_points={
          'console_scripts': [
              'grazed = grazed.grazed:main'
          ]
      })
