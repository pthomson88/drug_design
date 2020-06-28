from drug_design.load_data import load_data
from drug_design.similarity import run_similarity
from drug_design.save_load import *
from drug_design.term_num_opts import *
from drug_design.gsheet_store import *
from drug_design.PipeLine import TermPipeLine
from drug_design.key_increment import key_increment, sub_key_gen
import settings

#A terminal friendly way to load a dataset
def term_load_data():
    url_dict = UrlDict(name = "url_dict")
    options = [key for key in url_dict.dictionary]
    selection = selector(options,"Which dataset would you like to load. If you'd like to skip this step just press enter")
    if selection == False:
        print("No new data loaded")
        return False
    #assume that a new pipeline is warranted
    pipeline_obj = TermPipeLine( False , source_key = selection )
    return pipeline_obj

def normalise_on(pipeline_obj):
    #indicates that levenshtein_norm should be used ratehr than levenshtein - see similarity module
    print("Would you like to use normalised scores?")
    print("This balances the score for the length of Smiles - exactly matching smiles score 100, completely dissimilar strings score 0")
    print("")
    norm_on = input("Type Y to turn normalisation on or N to keep it off :> ")

    if norm_on.lower() == "y":
        norm = True
        print("Normalised scoring on \n")
    else:
        norm = False
        print("Normalised scoring off \n")

    norm_key = sub_key_gen("normalise", "similarity_score", **pipeline_obj.dictionary)
    kwargs = {norm_key : norm}
    pipeline_obj.update_property_terminal(**kwargs)

def main_term():
    quit = False
    retry = True
    #when we start for the first time dataframes should be empty
    pipeline = {}
    try:
        while quit == False:
            #first we're going to need to import some data
            print("\n ******************************************************** \n ** You can hit Ctrl-C at any time to exit the program ** \n ********************************************************")
            while not "source_key" in pipeline:

                print("\n Before we get started you're going to need to load some data.\n ")

                pipeline_obj = term_load_data()
                if pipeline_obj == False:
                    quit = True
                    print("See you next time... \n")
                    retry = False
                    break
                else:
                    pipeline = pipeline_obj.dictionary

                if not "source_key" in pipeline:
                    print("** Remember you can hit Ctrl-C to quit at any time **")

            while retry == True:
                print("What would you like to do next? \n Your options are: \n")
                next_action = selector(["View and run pipeline","Similarity score","Load different data","Clear my pipeline","Link or unlink a dataset","Quit"])

                if next_action == "View and run pipeline":
                    for key in pipeline_obj.dictionary:
                        print(key + " : " + str(pipeline_obj.dictionary[key]))

                    do_things = input("Type Y to turn run this pipeline or N to return to go back:> ")
                    if do_things.lower() == "y":
                        cores = input("How many cores would you like to use? The default is " + str(settings.CORES) + " (just press enter to keep the default):> ")
                        if cores == "":
                            cores = settings.CORES
                        result = pipeline_obj.run_pipeline_terminal(cores = cores)
                        print("********************************************************")
                        print(result)
                        result.to_csv('../drug_design_results.csv', index = False)

                elif next_action == "Similarity score":
                    sim_key = key_increment("similarity_score",**pipeline)
                    ds_key = pipeline_obj.source_key
                    #data is only loaded for the headers - even 1 chunk is wasteful
                    loaded_data = load_data( ds_key , chunk_limit = 1 )
                    headers = loaded_data[ ds_key ].headers
                    column = selector( headers , "Which column contains the smiles you'd like to compare to?")

                    if column == False:
                        break
                    else:
                        kwargs = {sim_key : column}
                        pipeline_obj.update_property_terminal(**kwargs)

                    url_dict = UrlDict(name = "url_dict")
                    data_options = [key for key in url_dict.dictionary]
                    data_options.append("Manual entry")

                    print("Where are the SMILES for comparison?")
                    SMILES_source = selector(data_options)

                    if SMILES_source == False:
                        break
                    elif SMILES_source == "Manual entry":
                        SMILES = input("Paste or type the SMILES you'd like to score similarity for :> ")
                        print("")
                        new_entry = sub_key_gen("single_smiles", "similarity_score", **pipeline)

                        kwargs = {new_entry : SMILES}
                        pipeline_obj.update_property_terminal(**kwargs)
                    else:
                        ref_data_key = SMILES_source
                        new_entry = sub_key_gen("dataframe_smiles_ref", "similarity_score", **pipeline)

                        dataset = load_data(ref_data_key, chunk_limit = 1)
                        ref_headers = dataset[ref_data_key].headers
                        ref_column = selector( ref_headers , "Which column contains the SMILE?" )
                        new_entry2 = sub_key_gen("dataframe_smiles_col", "similarity_score", **pipeline)

                        kwargs = {new_entry : ref_data_key , new_entry2 : ref_column}
                        pipeline_obj.update_property_terminal(**kwargs)

                    normalise_on(pipeline_obj)

                elif next_action == "Load different data":

                    print("")
                    print("Lets load some other data: ")
                    term_load_data()

                elif next_action == "Clear my pipeline":

                    print("")
                    print("Clearing the current pipeline... ")
                    clearout = {key:"delete_me" for key in pipeline_obj.dictionary}
                    pipeline_obj.delete_property_terminal(**clearout)
                    #clearing out the pipeline means you need to load some more data
                    break

                elif next_action == "Link or unlink a dataset":
                    gsheet_store()

                elif next_action == "Quit":
                    quit = True
                    print("See you next time... \n")
                    retry = False

                else:
                    print("Error: Something went wrong there. Make sure you are entering a number")
                    print("(Remember you can use Ctrl-C to escape at any time)")

    except KeyboardInterrupt:
        print("\nSee you next time... \n")

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main_term()
