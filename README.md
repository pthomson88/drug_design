# drug_design

This is a project to attempt the following challenge: https://covid.postera.ai/covid

There is a trello board for this project here: https://trello.com/b/wHk8KWTo/drugdesign-project

## Getting Set up
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
conda env create --prefix ./env -f drug_design.yml
```
* Finally you'll want to get going so activate your new conda environment:
```
conda activate ./env

```

To test it's all working try and load some test data using the python shell:

```
python

from drug_design.load_data import *

term_load_data()
```

You should see an output like the following in your terminal:
```
1. test_download
2. chembl26_ph3_ph4
3. chembl26_similar_protein_mols
4. not_a_csv
5. test_key

Which dataset would you like to load. If you'd like to skip this step just press enter :>
```
Type ```1``` exactly

The output should be as follows:

```
test_download
*******************
   1  a
0  2  b
1  3  c
2  4  d
3  5  e
*******************


{'test_download': <drug_design.datasets.DataSets.DataSet object at 0x10c717c40>}
```

To exit the shell type
```
quit()
```
### Running web app locally
Check you're in the top level drug_design directory:
.
|
-- drug_design * <-- You should be here
          |
          -- drug_design   <-- you should see these directories and files or similar
          -- static
          -- templates
          -- tests
          __init__.py
          .gitignore
          app.py
          drug_design.yml
          main_term.py
          main.py
          README.md

Now simply run
```
python main.py
```
You will see the following:
```
* Serving Flask app "main" (lazy loading)
* Environment: production
  WARNING: This is a development server. Do not use it in a production deployment.
  Use a production WSGI server instead.
* Debug mode: on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 193-019-012
```

Navigate to http://127.0.0.1:500/index to start the web app.

### Useful functions

Useful functions and modules:
* ```main_term.py``` - main terminal application (main.py is set up for the web app). run this to access the full functionality via the terminal
* ```pytest``` tests are stored in test_.py . Running them with the ```pytest``` command is a great way to check that everything is set up correctly and working - it's also useful if you've made changes and want to make sure the code still works
* ```load_data.py``` - we've already explored - this module loads all the datasets you need as a DataSet object based on a dataframe, try out ```term_load_data()``` from the python shell
* ```similarity.py``` - includes functions for edit distance between two string, detween 1 string and every entry in a dataframe column and between every entry in one column with every entry in another - beware big calculations can be slow.

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
