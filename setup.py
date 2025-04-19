from setuptools import setup, find_packages


setup(name='nova_space_armada',
      version='0.0.0',
      description='automatization',
      author='',
      author_email='',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      install_requires=['numpy', 'opencv-python', 'pyautogui', 'pywin32', 'opencv-contrib-python',
                        'Pillow', 'pika', 'requests', 'pytesseract']
      )
