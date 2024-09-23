import argparse
import logging  
import json 
import time 

from rag.rag_classifier import RAG_Classifier

def parse_arguments():
    '''
    Parses command-line arguments for the application.
    '''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--loglevel', default='warning')
    parser.add_argument('--db', default='../sql_dbs/ragnews.db')
    parser.add_argument('--article_limit', default=3)
    parser.add_argument('--llm_model', default='llama-3.1-70b-versatile')
    # default database 
    default_testing_data_path = (
        "../hairy-trumpet/data/"
        "wiki__page=2024_United_States_presidential_election,"
        "recursive_depth=0__dpsize=paragraph,"
        "transformations=[canonicalize, group, rmtitles, split]"
    )
    parser.add_argument('--testing_data_path', default=default_testing_data_path)
    parser.add_argument('--verbose', default=True)
    return parser.parse_args()

def setup_logging(loglevel):
    '''
    Configures the logging level and format.
    '''
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=loglevel.upper(),
    )

def parse_file(fp):
    '''
    Parses hairy-trump/data/ files into datasets.
    Returns a list of dictionaries where the keys are "masked_text" and "masks".
    Each dictionary is a testing dataset instance. 
    '''
    # Read all lines from the file
    with open(fp, 'r') as file:
        data = file.readlines() 
    
    #  Convert each line to a dictionary
    parsed_data = []
    for line in data:
        try:
            parsed_data.append(json.loads(line))  
        except json.JSONDecodeError:
            print(f"Could not parse line: {line}")

    return parsed_data

def run_tests(testing_data, model, verbose=True):
    n_correct = 0
    start_time = time.process_time()
    # iterate through testing data
    for i, data in enumerate(testing_data):
        masked_text = data["masked_text"]
        mask = data["masks"]
        tic = time.time()
        prediction = model.predict(masked_text)
        toc = time.time()
        # check if prediction is equal to mask
        if [p.lower() for p in prediction] == [m.lower() for m in mask]:
            n_correct += 1
            if verbose:
                print(f"Instance {i + 1} -> Prediction: ", prediction, "Truth:", mask)
                print("Time elapsed:", toc - tic, "secs")
                print()
        time.sleep(3)
    # display results
    end_time = time.process_time()
    print("Result Summary")
    print("--------------")
    percent_accuracy = 1.0 * n_correct / len(testing_data)
    print("Accuracy:", str(n_correct) + "/" + str(len(testing_data)), "or", str(percent_accuracy) + "%")
    print("Total time taken:", end_time - start_time, "secs")
    return percent_accuracy


def main():
    '''
    >>> python evaluate.py 
    Instance 1 -> Prediction:  ['Biden'] Truth: ['Biden']
    Time elapsed: 1.2827351093292236 secs

    Instance 2 -> Prediction:  ['Harris'] Truth: ['Harris']
    Time elapsed: 1.3710718154907227 secs

    Instance 3 -> Prediction:  ['Walz'] Truth: ['Walz']
    Time elapsed: 0.9932000637054443 secs

    Instance 4 -> Prediction:  ['Biden'] Truth: ['Biden']
    Time elapsed: 1.2004013061523438 secs

    Instance 5 -> Prediction:  ['Trump'] Truth: ['Trump']
    Time elapsed: 1.5423197746276855 secs

    ...


    '''
    # setup args and logging 
    args = parse_arguments()
    setup_logging(args.loglevel)

    # retrive testing data
    testing_data = parse_file(args.testing_data_path)
    # create model
    model = RAG_Classifier(
        db_name=args.db,
        llm_model=args.llm_model,
        article_limit=str(args.article_limit)
    )

    # test model on testing_data
    percent_accuracy = run_tests(testing_data, model, verbose=args.verbose)
    
if __name__ == "__main__":
    main()