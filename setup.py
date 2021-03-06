from setuptools import setup

setup(name='finder_maker',
      version='0.1',
      description='Generate or Download Star Finders',
      url='https://github.com/gmzsebastian/finder_maker',
      author=['Sebastian Gomez'],
      author_email=['sgomez@cfa.harvard.edu'],
      license='GNU GPL 3.0',
      py_modules=['finder_maker.py'],
      scripts=['finder_maker/get_finder.py', 'finder_maker/make_finder.py'],
      packages=['finder_maker'],
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
