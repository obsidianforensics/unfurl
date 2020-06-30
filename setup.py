from setuptools import setup, find_packages

setup(
  name='dfir-unfurl',
  packages=find_packages(),
  include_package_data=True,
  scripts=['unfurl.py', 'unfurl_app.py'],
  version='20200630',
  description='Unfurl takes a URL and expands ("unfurls") it into a directed graph',
  url='https://github.com/obsidianforensics/unfurl',
  author='Ryan Benson',
  author_email='ryan@dfir.blog',
  license='Apache',
  keywords=['unfurl', 'forensics', 'dfir', 'reverse-engineering', 'security'],
  classifiers=[],
  install_requires=[
    'flask',
    'flask_cors',
    'maclookup',
    'networkx',
    'protobuf',
    'publicsuffix2',
    'Requests',
    'torf',
    'ulid-py'
  ]
)

