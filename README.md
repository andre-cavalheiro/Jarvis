# Jarvis

## Introduction
A tool to abstract ML projects making it easier to run them with different configurations and organize its outputs. 

For Jarvis to work a Puppet class must be provided by the user which does a certain task such as, for example, training and testing a neural network while outputing the results and plots. Jarvis will process the user input and process before delivering it to the Puppet pipeline developed by the user allowing the puppet to work in an abstract and cleaner way. Also for each runtime Jarvis will manage directory creation and attribution.

The puppet class should be called **Puppet** and be inside **src/puppet.py** directory. (I'm planning to make this dynamic in a near future). It must also have a pipeline() method. The processed arguments are received via args dictionary in the ```__init__()``` function. Its keys and values are defined by the user via configuration.

Both Jarvis and the puppet require two configuration files, one to define the structure of the argument (.py) and the other to pass the value itself (.yaml). This will allows the preprocessing of arguments before reaching the puppet's pipeline. For example:

```
  src/args.py
  
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
  
 argListPuppet = [{
        'name': 'classifier',
        'type': str,
        'default': None,
        'help': 'Classifier to be tested.',
        'required': True,
        'possibilities': [
            ('KNN', KNeighborsClassifier),
            ('naiveBays', GaussianNB),
            ('decisionTree', DecisionTreeClassifier),
            ('randomForest', RandomForestClassifier)]
        },
        {
          'name': 'classifierParams',
          'type': str,              
          'default': None,
          'help': 'Possible parameters to be passed to the classifier.',
          'required': False,
          'children': [{
              'name': 'n_neighbors',
              'optimize': False,
              'optimizeInt': [1, 10]
            },
            {
              'name': 'weights',
            }]
        }
      ]
    

```
```
  src/config.yaml
  ...
  classifier: KNN
  classifierParams:
      n_neighbors: 5
      weights: uniform
  
```

```
  src/puppet.py
  
  class Puppet:
  
    def __init__(self, args, debug, outputDir):
      self.args = args
          self.debug = debug
          self.outputDir = outputDir
          
          if 'classifierParams' in self.args.keys() and self.args['classifierParams'] is not None:
            self.clf = self.args['classifier'](**self.args['classifierParams'])
          else:
            self.clf = self.args['classifier']()
            
    def pipeline(self):
    
          f = pd.read_csv(self.args['dataset'])
          
          x, y = self._gimmeSomePrettyData(df)
          
          x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=420)

          self.clf.fit(x_train, y_train)
          y_predict = self.clf.predict(x_test)
```
  

The objective of this configuration method is to allow the simplification of running the puppet's pipeline in several different ways. Enabling the definition of long test runs to be done in a simple config file instead of in the middle of the code. 

Jarvis has 3 distinct modes, them being: *Single execution*, *sequential execution* and *optimization*. 

- Single execution - the puppet's pipeline will run once with different arguments defined by the user.
- Sequential - the puppet's pipeline will run several times each time with different arguments defined by the user. 
- Optimization -the puppet's pipeline will run several times but this time the parameters will be selected by Optuna which performs [Baysian Optimization](https://www.cs.ox.ac.uk/people/nando.defreitas/publications/BayesOptLoop.pdf) in order to find the best combination of hyperparameters for the task at hand. The optimization parameters can only be defined in the configuration file.  

Although i believe the most convenient way to use Jarvis is by using yaml configuration files i've also added the option of passing most of the parameters (both for Jarvis and the Puppet) through command line arguments which is explained in the section: "Single excution and command line arguments".

## Jarvis Configuration

Jarvis can be configured in several different ways and its parameters are as follows:

```
jc            # Name of yaml configuration file for Jarvis (default: jarvisConfig.yaml)
conf          # Name of yaml configuration file for Puppet (default: src/config.yaml)
confSeq       # Name of yaml configuration file for Puppet in Sequential execution (default: src/configSeq.yaml)
outputDir     # Directory in which the output files and dirs will be created
debug         # Boolean to indicate if we're in production or development
seq           # Turns sequential mode on and off  (default: False)
optimize      # Turns optimizer mode on and off   (default: False)
optimizer     # Optimizer configurations  
  numTrials    
  numJobs
```
The configurations can then be passed by command-line or by using a yaml configuration. (see Single execution and command line arguments)

The architecture for each of Jarvis' arguments is specified in the **argListJarvis** array exported in **jarvisArgs.py**. If you only want to use Jarvis and not change it's standard functionality you shouldn't need to change this, but feel welcome to improve it :) .


## Puppet Class

The puppet class is created by the user and should be called **Puppet** and be inside **src/puppet.py** directory. (I'm planning to make this location dynamic in a near future). It must have a pipeline() method which will be called by Jarvis. In it the user can define what to do  in a single execution. The class will receives the following arguments:

```
name          # Configuration name
debug         # Boolean indicating whether we're in production or development
outputDir     # Directory in which to output whatever we want in an execution
args          # Dictionary containing whatever variables the user as defined as puppet arguments 
```

For each execution a new directory output is created, using the variable ```name``` or a randomly generated string if none was provided.

The class will receive as arguments processed by Jarvis as a dictionary via the ```args``` variable passed to the class.

The user can define this params, and how to process them in the **argListPuppet** array which is exported in src/args.py (I'm planning to make this location dynamic in a near future). For each argument the following fields can be specified: You can see an example below every parameter you can use the make your configuration

```
from src.libs.treatment import standardize, normalize

name: 'classifier',                           # Name of argument, should be the same as the key values in the yaml file
type: str,                                    # Type of argument (booleans should be specified as str2bool)
default: None,                                # Default value for the argument
required: False,                              # Specification is argument is mandatory or not
help: 'Classifier to be used in prediction'   # Tip to be displayed describing the argument

# For dynamic arguments, define the different possibilities and its name to be used in the configuration
possibilities:             
            [('normalize', normalize),
              ('standardize', standardize)]        

# To indicate simpler child components, useful to be passed as arguments for function arguments
children: [{           
            name: n_neighbors
            optimize: True
            optimizeInt: [1, 10]
        },

# Enable/Disable optimization mode (to try and optimize this variable or not). 
optimize : False,  

# Depending on the type of variable only one of the following should be indicated:                                                      
optimizeCategorical: ['smote', 'clusterCentroidsUnderSample', 'notBalanced']
optimizeDiscreteUniform: [0.80, 0.99]     
optimizeLogUniform: [0.80, 0.99]
optimizeUniform: [0.80, 0.99]
optimizeInt: [1, 4]

```

In the optimization variables, the array values define the search space in which to look for the optimal parameters following a certain way of looking for those same parameters. To better understand this you can look up [optuna's documentation](https://optuna.readthedocs.io/en/stable/tutorial/configurations.html).



## Single execution and command line arguments

This is the default mode, and it will only run the program with a single parameter configuration. An output directory is created inside the ```outputDir``` folder specified in the jarvis configuration. To enable this mode you just have to set the **seq** and **optimize** to False.

As stated above, Jarvis enables the usage of command line arguments instead the yaml configuration files. Whenever different values are passed for the same argument via two different methods (yaml and command line), the command line value will always take priority. This enables easier and faster manipution of the configuration during development. Both Jarvis and Puppet arguments can be received via command line.

For example in a project in which the puppet needs a parameter called ```learningRate``` we can make sure it's in default mode to use and specify the value of learning rate by simply doing:

```python main.py --seq=False --optimize=False --learningRate=0.001```

## Sequential execution

Sequential execution is enabled using the **seq** variable in Jarvis 'condiguration. To use it you must provide a special yaml configuration file via the ```confSeq```variable. In it you can have several different configurations in an array as so:

```
configs:
  - name: test run
    classifier: KNN
    classifierParams:
      n_neighbors: 1
      weights: uniform
    nanStrategy: median
    covarianceThreshold: 0.95
  - name: test run 2
    classifier: naiveBays
    nanStrategy: median
    covarianceThreshold: 0.95
```

Remember that you are the one that chooses which arguments are passed here via the Puppet's configuration. (See example in Puppet Class)

Jarvis will create a new directory in the output called "sequential - {ID}", and inside of it will create several directories for the outputs of each test run. 

## Optimization

This last mode needs a little more experimentation to be at full potential but it's function for the moment. The abstraction made to the code enables us to very simply use optimization techniques. The one enabled so far is [Baysian Optimization](https://www.cs.ox.ac.uk/people/nando.defreitas/publications/BayesOptLoop.pdf). 

Jarvis uses the Optuna package to do it. You need to configure it via the Puppet's configuration file ```src/args.py``` depending on the type of variable. (See example in Puppet Class).

You can configure the optimization process in Jarvis' configurations with:

```
  numTrials: 500
  numJobs: 1
```

To better understand this you can look up [optuna's documentation](https://optuna.readthedocs.io/en/stable/tutorial/configurations.html).

