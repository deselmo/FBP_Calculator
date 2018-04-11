# FBP Calculator
FBP Calculator is a graphical tool for calculating Reaction System predictors.

## Installation
#### Release:
If there's a [release](https://github.com/deselmo/FBP_Calculator/releases) for your platform, you can simply use that.

#### Using pip:
```
$ pip3 install fbp_calculator
```
#### From the repository:

Download the repository:
```
$ git clone git://github.com/deselmo/fbp_calculator.git
```
move into the repository direcory:
```
cd fbp_calculator:
```
install the application:
```
$ python3 setup.py install
```

> ### Notes for installation with pip or from the repository:
> fbp_calculator depends on pyeda, in order to install it you will need to have python headers and libraries.
>
> #### Linux
> You will probably need to install the python3 "development" package.
>
> - For Debian-based systems (eg Ubuntu, Mint):
>   ```
>   $ sudo apt-get install python3-dev
>   ```
>
> - For RedHat-based systems (eg RHEL, Centos):
>
>   ```
>   $ sudo yum install python3-devel
>   ```
>
> - For ArchLinux-based systems:
>
>   ```
>   $ pacman -S base-devel
>   ```
>
> #### Windows
> Download the pyeda binary file for your platform from Christoph Gohlke's [pythonlibs page](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyeda) and install it.
>
> ```
> > pip3 install pyeda‑*.whl
> ```
>
> #### MacOs
> 1. Install Xcode’s separate Command Line Tools app
>
>       ```
>       $ xcode-select --install
>       ```
>
> 2. Installing and setting up Homebrew
>
>       ```
>       $ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
>       ```
>
> 3. Put the Homebrew directory at the top of the PATH environment variable.
>
>       You should create or open the `~/.bash_profile` file. Using the nano command:
>
>       ```
>       $ nano ~/.bash_profile
>       ```
>
>       Write the following:
>
>       ```
>       export PATH=/usr/local/bin:$PATH
>       ```
>
>       For these changes to activate, in the Terminal window, type:
>
>       ```
>       $ source ~/.bash_profile
>       ```
>
> 4. Install python3:
>
>       ```
>       $ brew install python3
>       ```

## Usage
After pip installing you can run the application from command line:
```
$ fbp_calculator
```
or using the `FBP Calculator.pyw` file  in the repository.

## License
This project is licensed under the [MIT License](https://github.com/deselmo/FBP-Calculator/blob/master/LICENSE).
