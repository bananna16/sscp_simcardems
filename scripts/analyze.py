from pathlib import Path
import matplotlib.pyplot as plt
import simcardems
import numpy as np
import json

# Define pathes here
here = Path(__file__).absolute().parent
folder = here.parent 
results_folder =  folder / "results"
num_models = 2

# Generate dictionary for results
results = {}
for PoMm in range(1, num_models + 1):
    #print(f"Analyzing model {PoMm}")
    #results_file = population_folder.joinpath("results.h5")

    # workaround for healthy vs. DOX
    if PoMm == 1:
        print(f"Analyzing healthy (model {PoMm})")
        results_file = folder / "demos/results_healthy/results.h5"
    elif PoMm == 2:
        print(f"Analyzing DOX (model {PoMm})")
        results_file = folder / "demos/results_DOX_M1/results.h5"

    if not results_file.is_file():
        #results_file = population_folder.joinpath(f"m{PoMm}/results.h5")
        if not results_file.is_file():
            raise FileNotFoundError(f"File {results_file} does not exist")

    loader = simcardems.DataLoader(results_file)
    results[f"m{PoMm}"] = simcardems.postprocess.extract_traces(loader=loader)


# Analyze data
outdir = results_folder / "DOX_vs_healthy"
print("------------------------------------------")
print("Start analysis of results")
biomarker_dict = simcardems.postprocess.get_biomarkers(results, outdir, num_models)
print("------------------------------------------")
print("Start plotting")
simcardems.postprocess.plot_population(results, outdir , num_models)

# Compare healthy vs. DOX
##outfile = outdir / "biomarkers_PoMcontrol.json"
print("------------------------------------------")
print("Start analyis of changes healthy vs. DOX")
#with open(outfile) as f:
    #biomarkers = simcardems.postprocess.numpyfy(json.load(f))
biomarker_comparison = {}
change_DOX_dict = {}
for biomarker in biomarker_dict["m1"].keys(): #loop through all biomarkers
    biomarker_comparison[biomarker] = []
    change_DOX_dict[biomarker] = []
    #for PoMm in biomarker_dict.keys():
    #    biomarker_comparison[biomarker].append(biomarker_dict[PoMm][biomarker]) #store data from all models for the current biomarker
    #print("{} healthy: {}".format(biomarker, biomarker_dict["m1"][biomarker]))
    #print("{} DOX: {}".format(biomarker, biomarker_dict["m2"][biomarker]))
    change_DOX_dict[biomarker] = biomarker_dict["m2"][biomarker] / biomarker_dict["m1"][biomarker]
    change_DOX_dict[biomarker] = np.round((change_DOX_dict[biomarker]-1) *100) # convert to increase / decrease in % and round
    if np.isnan(change_DOX_dict[biomarker]):
        print("Change for {} from healthy to DOX: {:+}% ".format(biomarker, change_DOX_dict[biomarker]))
    else:
        print("Change for {} from healthy to DOX: {:+}% ".format(biomarker, int(change_DOX_dict[biomarker])))

with open(outdir.joinpath("changes_biomarkers_PoMcontrol.json"), "w") as f:
        json.dump(change_DOX_dict, f)






""" 
PREVIOUS VERSION TO PLOT FUNCTION --> DO NOT DELETE YET 
# Function with array of output directories and path to results and labels as input: loops through the arrays

def plot_multiple_state_traces(
    outdir_arr,
    label_arr,
    path_results,
    reduction: str = "center",
):
    
    fig, axs = plt.subplots(2, 2, figsize=(10, 8), sharex=True)

    for outdir, label in zip(outdir_arr, label_arr):
        loader = simcardems.DataLoader(outdir / "results.h5")
        values = simcardems.postprocess.extract_traces(loader, reduction=reduction)
        times = np.array(loader.time_stamps, dtype=float)

        for i, (group, key) in enumerate(
            (("ep", "lambda"), ("mechanics", "Ta"), ("ep", "V"), ("ep", "Ca")),
        ):
            ax = axs.flatten()[i]
            try:
                y = values[group][key]
            except KeyError:
                # Just skip it
                continue
            ax.plot(times, y, label = label)
            if key == "lambda":
                ax.set_title(r"$\lambda$")
                #ax.set_ylim(min(0.9, min(y)), max(1.1, max(y)))
            else:
                ax.set_title(key)
            #ax.grid()
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Add legends to all subplots
    for ax in axs.flatten():
        ax.legend()

    axs[1, 0].set_xlabel("Time [ms]")
    axs[1, 1].set_xlabel("Time [ms]")
    axs[0, 0].set_ylabel("Active stretch")
    axs[0, 1].set_ylabel("Active tension (kPa)")
    axs[1, 0].set_ylabel("Voltage (mV)")
    axs[1, 1].set_ylabel(r"Intracellular calcium concentration ($\mu$M)")

    fig.savefig(path_results.joinpath(f"state_traces_center_loop.png"), dpi=300)

# Call function to plot multiple simulation results in one plot
outdir_arr = [here.parent / "demos/results_DOX_M1", here.parent / "demos/results_healthy"]
label_arr = ["DOX", "Healthy"]
reduction =  "center"

plot_multiple_state_traces(outdir_arr, label_arr, path_results, "center")

"""