'''
TutImport() shows importing and instantiating various cell models, randomly
    connecting the models into recurrent network, providing background synaptic
    input and plotting the output.

    TODO:  
'''

from netpyne import specs, sim
import os
from os.path import join

# Create class NetParams object to store imported parameters
netParams = specs.NetParams()

if __name__ == '__main__':

####################################
#                                  #
#                                  #
#        NETWORK PARAMETERS        #
#                                  #
#                                  #
####################################


    ###################################
    #  POPULATION-LEVEL DESCRIPTIONS
    ###################################

    # Population parameters
    netParams.popParams['HH_pop'] = {'cellType': 'PYR', 'numCells': 12, 'cellModel': 'HH'}
    netParams.popParams['HH3D_pop'] = {'cellType': 'PYR', 'numCells': 12, 'cellModel': 'HH3D'}
    #netParams.popParams['Traub_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Traub'}
    # netParams.popParams['Mainen_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Mainen'}
    # netParams.popParams['Friesen_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Friesen'}

    ###################################
    #  POPULATION MODEL IMPORTS
    ###################################
    '''
        Requires importCellParams() method.
        INPUTS:
            - label :
            - conds :
            - fileName : name of .py or .hoc file including format
            - cellName : name of object or template in model file
            - importSynMechs : boolean
    '''

    ##### HH model
    ''' Example of model as PYTHON object. '''
    netParams.importCellParams(label='PYR_HH_rule', conds={'cellType': 'PYR', 'cellModel': 'HH'},
        fileName='HHCellFile.py', cellName='HHCellClass', importSynMechs=True)

    ##### HH3D model
    ''' Example of a HOC-format model with only morphology information '''
    cellRule = netParams.importCellParams(label='PYR_HH3D_rule', conds={'cellType': 'PYR', 'cellModel': 'HH3D'},
        fileName='geom.hoc', cellName='E21')
    # somatic active mechanisms
    cellRule['secs']['soma']['mechs']['hh'] = { 'gnabar' : 0.12,
                                                'gkbar' : 0.036,
                                                'gl' : 0.003,
                                                'el' : -70}
    # passive mechanisms
    for secName in cellRule['secs']:
        cellRule['secs'][secName]['mechs']['pas'] = {'g' : 0.0000357, 'e' : -70}
        cellRule['secs'][secName]['geom']['cm'] = 1

    # #### Traub model
    # ''' Example of model as .hoc file with NEURON template. '''
    # cellRule = netParams.importCellParams(label='PYR_Traub_rule', conds={'cellType': 'PYR', 'cellModel': 'Traub'},
    #     fileName=join('Traub2003','pyr3_traub.hoc'), cellName='pyr3')
    # # somatic spike generating locus loc (why?)
    # somaSec = cellRule['secLists']['Soma'][0] # called 'Soma' in objref of file
    # cellRule['secs'][somaSec]['spikeGenLoc'] = 0.5

    # #### Mainen model
    # ''' Example of model as PYTHON object and mechanisms as .mod files. '''
    # netParams.importCellParams(label='PYR_Mainen_rule', conds={'cellType': 'PYR', 'cellModel': 'Mainen'},
    #     fileName=join('Mainen','mainen.py'), cellName='PYR2')
    #
    # #### Friesen model TODO: Download these files
    # ''' Example of model as PYTHON object with spike gen in axon (not soma). '''
    # cellRule = netParams.importCellParams(label='PYR_Friesen_rule', conds={'cellType': 'PYR', 'cellModel': 'Friesen'},
    # 	fileName='friesen.py', cellName='MakeRSFCELL')
    # cellRule['secs']['axon']['spikeGenLoc'] = 0.5

    #### NOTE: There are other cell files for Izhikevich models but not included here


    ###################################
    #  SYNAPTIC MECHANISMS
    ###################################
    '''
        Only PYR cells so AMPA synapses only.
    '''

    # Synaptic mechanism parameters
    netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 10, 'tau2': 5.0, 'e': 0}

    # Synaptic background stimulation
    netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 50, 'noise': 0.5} # rate in Hz
    netParams.stimTargetParams['bkg1'] = {'source': 'bkg', 'conds': {'cellType': 'PYR', 'cellModel': ['HH','HH3D']},
                                            'weight': 0.1, 'delay': 5, 'sec': 'soma'}
    # netParams.stimTargetParams['bkg2'] = {'source': 'bkg', 'conds': {'cellType': 'PYR', 'cellModel': 'Friesen'},
    #                                         'weight': 5, 'delay': 5, 'sec': 'soma'}

    ###################################
    #  CONNECTIVITY PARAMETERS
    ###################################

    # Recurrent connectivity
    netParams.connParams['recurrent'] = {
        'preConds': {'cellType': 'PYR'}, 'postConds': {'cellType': 'PYR'}, # randomly connect PYR->PYR
        'connFunc': 'convConn',             # predefined connectivity function (=conventional, i.e., random)
        'convergence': 'uniform(0,10)',     # max num of incoming connections to cell
        'weight': 0.001,                    # synaptic weight
        'delay': 5,                         # transmition delay
        'sec': 'soma'
    }


####################################
#                                  #
#                                  #
#      SIMULATION PARAMETERS       #
#                                  #
#                                  #
####################################


    ###################################
    #  CONFIGURATION SPECIFICATIONS
    ###################################

    simConfig = specs.SimConfig()       # class SimConfig object to store sim details
    simConfig.duration = 1*1e3          # run for 1 s (ms)
    simConfig.dt = 0.025                # internal timestep (ms)
    simConfig.verbose = 0               # show detailed messages
    simConfig.recordTraces = {'V_soma':
                                    {'sec': 'soma',
                                     'loc':0.5, 'var':'v'}
                              }
    simConfig.recordStep = 1            # downsampling for saved data (ms)
    simConfig.filename = 'model_output'
    simConfig.savePickle = False        # save params, network and sim output in pickle file

    ###################################
    #  ANALYSIS SPECIFICATIONS
    ###################################

    simConfig.analysis['plotRaster'] = {'orderInverse': True, 'saveFig': 'TutImport_raster.png'}
    simConfig.analysis['plotTraces'] = {'include' : [0]}        # plot traces for list of cells


####################################
#                                  #
#                                  #
#       SIMULATION RUN CALLS       #
#                                  #
#                                  #
####################################

    # Create network and run simulation
    sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)
