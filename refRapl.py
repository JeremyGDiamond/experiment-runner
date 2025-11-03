from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from typing import Dict, List, Any, Optional
from pathlib import Path
from os.path import dirname, realpath

import os
import signal
import time
import subprocess
import shlex

class RunnerConfig:
    ROOT_DIR = Path(dirname(realpath(__file__)))

    # ================================ USER SPECIFIC CONFIG ================================
    """The name of the experiment."""
    name:                       str             = "RefRapl"

    """The path in which Experiment Runner will create a folder with the name `self.name`, in order to store the
    results from this experiment. (Path does not need to exist - it will be created if necessary.)
    Output path defaults to the config file's path, inside the folder 'experiments'"""
    results_output_path:        Path             = ROOT_DIR / 'experiments'

    """Experiment operation type. Unless you manually want to initiate each run, use `OperationType.AUTO`."""
    operation_type:             OperationType   = OperationType.AUTO

    """The time Experiment Runner will wait after a run completes.
    This can be essential to accommodate for cooldown periods on some systems."""
    time_between_runs_in_ms:    int             = 30000

    # Dynamic configurations can be one-time satisfied here before the program takes the config as-is
    # e.g. Setting some variable based on some criteria
    def __init__(self):
        """Executes immediately after program start, on config load"""

        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN       , self.before_run       ),
            (RunnerEvents.START_RUN        , self.start_run        ),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT         , self.interact         ),
            (RunnerEvents.STOP_MEASUREMENT , self.stop_measurement ),
            (RunnerEvents.STOP_RUN         , self.stop_run         ),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT , self.after_experiment )
        ])
        self.run_table_model = None  # Initialized later
        output.console_log("Custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        """Create and return the run_table model here. A run_table is a List (rows) of tuples (columns),
        representing each run performed"""
        tool = FactorModel("tool", ['runCC.sh','runEnergiBridge.sh','runNoTools.sh','runPerf.sh','runPowerjoular.sh','runRefKern.sh','runRefUser.sh','runScaphandre.sh','runTurbostat.sh'])
        # tool = FactorModel("tool", ['runRefKern.sh'])
        benchmark = FactorModel("benchmark", ['is','mg','ft','ep','cg','bt','mi','sl'])
        # benchmark = FactorModel("benchmark", ['mg'])
        self.run_table_model = RunTableModel(
            factors=[tool, benchmark],
            repetitions = 15,
            shuffle=True
        )
        print("Run Table Model",self.run_table_model)
        return self.run_table_model

    def before_experiment(self) -> None:
        """Perform any activity required before starting the experiment here
        Invoked only once during the lifetime of the program."""
        output.console_log("warming up experiment")
        
        ssh_command1 = [
            "ssh",
            "nuc",
            "cd ref_rapl/energy_exp_server && ./runCC.sh mg warm1"
        ]

        # Run the command
        try:
            result = subprocess.run(ssh_command1, check=True, text=True, capture_output=True)
            print("Output:\n", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error:\n", e.stderr)

        ssh_command2 = [
            "ssh",
            "nuc",
            "cd ref_rapl/energy_exp_server && ./runScaphandre.sh bt warm2"
        ]

        # Run the command
        try:
            result = subprocess.run(ssh_command2, check=True, text=True, capture_output=True)
            print("Output:\n", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error:\n", e.stderr)


    def before_run(self) -> None:
        """Perform any activity required before starting a run.
        No context is available here as the run is not yet active (BEFORE RUN)"""
        pass

    def start_run(self, context: RunnerContext) -> None:
        """Perform any activity required for starting the run here.
        For example, starting the target system to measure.
        Activities after starting the run should also be performed here."""
        pass

    def start_measurement(self, context: RunnerContext) -> None:
        """Perform any activity required for starting measurements."""
        tool = context.execute_run['tool'] 
        benchmark = context.execute_run['benchmark']
        run_nr = context.run_nr

        output.console_log(f"run number {run_nr} running tool {tool}, bench {benchmark}")

       
        ssh_command = [
            "ssh",
            "nuc",
            f"cd ref_rapl/energy_exp_server && ./{tool} {benchmark} run_{run_nr}"
        ]

        # Run the command
        try:
            result = subprocess.run(ssh_command, check=True, text=True, capture_output=True)
            print("Output:\n", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error:\n", e.stderr)
                
        
        #time.sleep(1) # allow the process to run a little before measuring
        

    def interact(self, context: RunnerContext) -> None:
        """Perform any interaction with the running target system here, or block here until the target finishes."""

        # No interaction. We just run it for XX seconds.
        # Another example would be to wait for the target to finish, e.g. via `self.target.wait()`
        output.console_log("Running program for 60 seconds")
        # time.sleep(60)
    def stop_measurement(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping measurements."""
        # self.profiler.wait()

    def stop_run(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping the run.
        Activities after stopping the run should also be performed here."""
        
    
    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, Any]]:
        """Parse and process any measurement data here.
        You can also store the raw measurement data under `context.run_dir`
        Returns a dictionary with keys `self.run_table_model.data_columns` and their values populated"""
        pass

    def after_experiment(self) -> None:
        """Perform any activity required after stopping the experiment here
        Invoked only once during the lifetime of the program."""
        # files on target system
        pass

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path:            Path             = None
