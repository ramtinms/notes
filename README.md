# notes
My jupyter notebooks and codes to publish them


## setup

1. clone this repo with submodules
```
git clone --recurse-submodules git@github.com:ramtinms/notes.git
```
or clone it and setup submodules(one for theme and one for blog)
```
mkdir output
cd output
git submodule add -f ssh://git@github.com/ramtinms/random-walk.git 

cd ..
git submodule add https://github.com/nairobilug/pelican-alchemy themes/pelican-alchemy
```

check `.gitmodules` file and make sure you have `ignore = all`
```
[submodule "output"]
        path = output
        url = https://github.com/ramtinms/random-walk.git
        ignore = all
```

Install pelican 
```
pip install pelican
```

## test locally 
to start server
```
make devserver
```

to stop server
```
make stopserver
```
## steps to publish content

#### add notebooks to `note` repo
```
make notebook
```

#### publish new notebooks and push to github
```
make github
```
