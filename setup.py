from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name='dfir-unfurl',
  packages=find_packages(),
  include_package_data=True,
  scripts=['unfurl_app.py', 'unfurl_cli.py'],
  version='20230901',
  description='Unfurl takes a URL and expands ("unfurls") it into a directed graph',
  long_description_content_type='text/markdown',
  long_description=long_description,
  url='https://github.com/obsidianforensics/unfurl',
  author='Ryan Benson',
  author_email='ryan@dfir.blog',
  license='Apache',
  keywords=['unfurl', 'forensics', 'dfir', 'reverse-engineering', 'security', 'osint', 'digital forensics'],
  classifiers=[],
  install_requires=[
    'dnslib',
    'flask==2.3.3',
    'flask_cors',
    'flask-restx>=1.2.0',
    'maclookup',
    'networkx',
    'protobuf==4.*',
    'publicsuffix2',
    'pycountry',
    'pymispwarninglists>=1.5',
    'Requests',
    'torf',
    'ulid-py',
    'Werkzeug>=2.3.3'
  ]
)
