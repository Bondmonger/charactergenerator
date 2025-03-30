import random


def create_alignment_dictionary(preferred_alignment):
    alignment_list = ["Lawful Good", "Neutral Good", "Chaotic Good", "Chaotic Neutral",
                      "Chaotic Evil", "Neutral Evil", "Lawful Evil", "Lawful Neutral"]
    side_list, edge_list = [8, 4, 2, 1, 2, 1, 2, 4], [16, 8, 4, 2, 1, 2, 4, 8]
    index = alignment_list.index(preferred_alignment)
    reordered_list = alignment_list[index:] + alignment_list[:index]
    if "Neutral" in preferred_alignment:
        alignment_dict = dict(zip(reordered_list, side_list))
    else:
        alignment_dict = dict(zip(reordered_list, edge_list))
    alignment_dict["Neutral"] = 2
    return alignment_dict


def filter_alignment_dictionary(alignment_dict, permitted_alignments):
    filtered_dict = alignment_dict.copy()
    if permitted_alignments and all(isinstance(item, list) for item in permitted_alignments):
        allowed = set(permitted_alignments[0])              # start with the first list...
        for alignment_list in permitted_alignments[1:]:     # ...and take intersection with each subsequent list...
            allowed = allowed.intersection(set(alignment_list))
        permitted_alignments = list(allowed)                # ...then convert back to list
    for align in list(filtered_dict.keys()):                # keep only alignments that are in the permitted list
        if align not in permitted_alignments:
            del filtered_dict[align]
    return filtered_dict                                    # this could probably use empty list error handling


def get_random_weighted_alignment(preferred_alignment, permitted_alignments):
    alignment_dict = create_alignment_dictionary(preferred_alignment)   # generates weighted alignment table
    if permitted_alignments:                                            # generates OR conjunction of permitted aligns.
        alignment_dict = filter_alignment_dictionary(alignment_dict, permitted_alignments)
    alignments = list(alignment_dict.keys())
    weights = list(alignment_dict.values())
    selected_alignment = random.choices(alignments, weights=weights, k=1)[0]
    return selected_alignment


# # Test cases
# for test_alignment in ["Lawful Good", "Neutral Good", "Chaotic Evil"]:
#     print(f"\nTest with preferred_alignment = '{test_alignment}':")
#     # Run multiple times to show the weighted distribution
#     results = {}
#     for _ in range(100000):
#         # result = get_random_weighted_alignment(test_alignment, filter_rules="chaotic_only")
#         result = get_random_weighted_alignment(test_alignment, permitted_alignments=[["Chaotic Good", "Chaotic Evil",
#                                                                                      "Chaotic Neutral"],
#                                                                                      ["Chaotic Good", "Lawful Good",
#                                                                                      "Lawful Evil", "Chaotic Evil"]])
#         results[result] = results.get(result, 0) + 1
#
#     # Print distribution of results
#     print("Distribution from 100,000 selections:")
#     total = sum(results.values())
#     for alignment, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
#         percentage = (count / total) * 100
#         print(f"  {alignment}: {count} times ({percentage:.1f}%)")
