from random import shuffle, sample, random
from copy import deepcopy
from dotenv import load_dotenv
import os

# os.environ["JUDICIOUS_SERVER_URL"] = "https://imprudent.herokuapp.com"
load_dotenv()
import judicious

# Target the server you want
# remote: https://imprudent.herokuapp.com
# os.environ["JUDICIOUS_SERVER_URL"] = "localhost:5000"


# judicious.seed("c65a01e7-079e-4e91-8a1b-cac8c5f719d9")
# judicious.seed("46b14020-5ec6-4e05-8bb7-ceb1202f3559")
# judicious.seed("fd8a2ed1-bb91-4d59-b805-c94dace586ee")
judicious.seed("d8b75930-db30-47d9-b208-72d6ffe5274b")


# def trial_sequences(n_stimuli, n_ratings, n_trials, n_retests, shuffle_sequences=False):

#     # crucial tests
#     assert n_stimuli % n_trials == 0
#     assert n_retests <= n_trials

#     # unique stimulus IDs
#     stimuli = list(range(1, n_stimuli + 1))

#     # create lists of lists of trials
#     sequences = []
#     for _ in range(n_ratings):

#         # for each rating batch, shuffle stimuli
#         shuffle(stimuli)
#         stimuli_perm = deepcopy(stimuli)

#         # partition the stimuli into n_trial chunks
#         for i in range(0, n_stimuli, n_trials):
#             sequence = stimuli_perm[i : i + n_trials]
#             retests = sample(sequence, n_retests)
#             shuffle(retests)
#             sequences += [sequence + retests]

#     if shuffle_sequences:
#         shuffle(sequences)

#     return sequences


def trial_sequences(
    n_stimuli, n_ratings, n_trials, n_retests, attributes=["trustworthy", "attractive"]
):
    """New sequence generation with repeats and indexes built in."""
    # crucial tests
    assert n_stimuli % n_trials == 0
    assert n_retests <= n_trials

    # unique stimulus IDs
    stimuli = list(range(1, n_stimuli + 1))

    # create lists of lists of trials
    sequences = {"faces": [], "repeats": [], "trial_indexes": [], "attributes": []}
    for attribute in attributes:
        for _ in range(n_ratings):

            # for each rating batch, shuffle stimuli
            shuffle(stimuli)
            stimuli_perm = deepcopy(stimuli)

            # partition the stimuli into n_trial chunks
            for i in range(0, n_stimuli, n_trials):
                faces = stimuli_perm[i : i + n_trials]
                retests = sample(faces, n_retests)
                shuffle(retests)
                faces += retests

                non_repeats = [False for s in range(len(faces))]
                seq_repeats = [True for s in range(len(retests))]
                repeats = non_repeats + seq_repeats

                trial_indexes = [s for s in range(len(faces))]
                attributes = [attribute for s in range(len(faces))]

                sequences["faces"] += [faces]
                sequences["repeats"] += [repeats]
                sequences["trial_indexes"] += [trial_indexes]
                sequences["attributes"] += [attributes]

    return sequences


def judge_faces(sequence):
    """Run through an experiment on judging faces."""
    with judicious.Person(lifetime=60 * 60) as person:
        print("got here")
        r_consent = person.consent()
        if not r_consent:
            return None
        r_attrition = person.attrition()
        r_instruct = person.instruct_judge_faces(attribute=attribute)
        results = []
        faces = sequence["faces"]
        attributes = sequence["attributes"]
        repeats = sequence["repeats"]
        trial_indexes = sequence["trial_indexes"]
        zipped = zip(faces, attributes, repeats, trial_indexes)
        for face, attribute, repeat, trial_index in zipped:
            r = person.judge_face(face, attribute, repeat, trial_index)
            results.append(r)
        r_debrief = person.debrief()
        results.append(r_debrief)
        r_complete = person.complete()
        results.append(r_complete)
        return results


attributes = ["trustworthy", "attractive"]
sequences = trial_sequences(
    n_stimuli=1000, n_ratings=30, n_trials=100, n_retests=20, attributes=attributes,
)
print(sequences)
results = judicious.map3(judge_faces, sequences)
print(results)