# lscgen ***WIP***
***lscgen****.py* generates a dircolors-like output from a human-readable config file.

## Installation
- `git clone` to your preferred location, for example **~/**.
- Specify a theme by copying your desired config file replacing the existing *theme.cfg*
```sh
cp mytheme theme.cfg
```
- use lscgen.py everytime:
	```sh
	if [ -x ~/lscgen.py ]; then
		eval "$(~/lscgen.py 2>nul)"
	fi
	```