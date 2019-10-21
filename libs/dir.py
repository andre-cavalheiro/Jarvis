from os.path import join, exists, isfile, isdir, basename, normpath
from os import makedirs, listdir, rename, getcwd
from pathlib import Path


def getWorkDir(jconfig, folderName, extraName='', completedText='', createNew=True):
    if 'outputDir' in jconfig.keys() and jconfig['outputDir'] is not None:
        outputDir = jconfig['outputDir']
        return makeDir(outputDir, folderName + extraName, createNew=createNew, completedText=completedText)
    else:
        return getcwd()      # Current working directory


# fixme - this one is a bit ugly and can be improved
def makeDir(outputDir, name, createNew=True, completedText=''):
    dir = join(outputDir, name)
    dirCompleted = join(outputDir, name+completedText)
    if exists(dir) or exists(dirCompleted):
        j = 1
        while exists(dir) or exists(dirCompleted):
            j += 1
            dir = join(outputDir, '{}-{}'.format(name, j))
            dirCompleted = join(outputDir, '{}-{}{}'.format(name, j, completedText))

        if createNew:
            print('> Wanted directory already exists, created - "{}"'.format(dir))
            makedirs(dir)
        else:
            dir = join(outputDir, '{}-{}'.format(name, j-1)) if j != 2 else join(outputDir, name)
            print('> Using already existent dir - "{}"'.format(dir))
    else:
        print('> Created Directory - "{}"'.format(dir))
        makedirs(dir)
    return dir


def changeDirName(origPath, nemName='', extraText=''):
    if not isdir(origPath):
        print('Error: Given Path is not a directory, name unchanged')
        return
    pathToFolder = Path(origPath).parent
    oldFoderName = basename(normpath(origPath))
    newFolderName = oldFoderName + extraText

    rename(origPath, join(pathToFolder, newFolderName))


def getFilesInDir(dir):
    files = [f for f in listdir(dir) if isfile(join(dir, f))]
    return files
