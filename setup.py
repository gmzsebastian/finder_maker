from setuptools import setup

setup(name='finder_maker',
      version='0.1',
      description='Generate or Download Star Finders',
      url='https://github.com/gmzsebastian/finder_maker',
      author=['Sebastian Gomez'],
      author_email=['sgomez@cfa.harvard.edu'],
      license='GNU GPL 3.0',
      py_modules=['finder_maker.py'],
      scripts=['get_finder.py', 'make_finder.py'],
      install_requires=[
            'numpy',
            'matplotlib',
            'astropy',
            'requests',
            'reproject',
            'photutils',
            'bs4',
      ],
      test_suite='nose.collector',
      zip_safe=False)
