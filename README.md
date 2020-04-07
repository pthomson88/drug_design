# drug_design

This is a project to attempt the following challenge: https://covid.postera.ai/covid

There is a trello board for this project here: https://trello.com/b/wHk8KWTo/drugdesign-project

## Getting Started
Get setup on Github and git:
* This is a pretty good walkthrough - https://kbroman.org/github_tutorial/pages/first_time.html

Next clone the repo and get stuck in:
* In your terminal window you'll want to navigate to a sensible directory
   * If you have a folder in your home drive called projects that you'd like to keep this in then in a unix environment (mac or linux) use the command:

```
cd projects
```
   * From here you'll want to clone the repository with the command:

```
git clone git@github.com:pthomson88/drug_design.git
```

Next up you'll want to install miniconda:
* This will let you set up a python environment with all the libraries you need (don't worry if you're not sure you have python - miniconda comes with a version of it)
     * This tutorial will help you get up and running: http://deeplearning.lipingyang.org/2018/12/24/install-miniconda-on-mac/
* Next you'll want to load the environment I have from the `drug_design` directory - if this is in a folder called projects you'll want to do the following to get there from Downloads (where you'll be after installing miniconda):
```
cd ..
```

```
cd projects
```

```
cd drug_design
```
   * Now to load the environment:
```
conda env create -f drug_design.yml
```
* Finally you'll want to get going so activate your new conda environment:
```
conda activate drug_design

```

To test it's all working try and load some test data:

```
python load_data.py
```

You should see:
```
The available dataset keys are :

test_download
chembl26_ph3_ph4

Which dataset would you like to load :>
```
Type ```test_download``` exactly

You will be asked if you want to load another dataset:

```
Would you like to load another dataset? enter Y for yes or N for no :>
```

Type ```n``` the output should be as follows:

```
test_download
*******************
   1  a
0  2  b
1  3  c
2  4  d
3  5  e
*******************

```
Remember load_data - you'll need to run this function whenever you want to start:

### Prerequisites

Useful functions and modules:

* ```pytest``` tests are stored in test_.py . Running them with the ```pytest``` command is a great way to check that everything is set up correctly and working - it's also useful if you've made changes and want to make sure the code still works
* ```load_data.py``` - we've already explored - loads all the dataframes you need into a dictionary object called df
* ```similarity.py``` - takes in 2 strings and tells you how similar one is to another

### Prerequisites

Instructions above are based on Mac - they might be similar for Linux - Windows will probably be a little different and might require some Googling

## Authors

* **Peter Thomson**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
