from diff_match_patch import diff_match_patch

def diff_original_with_corrected(original: str, corrected: str):
    dmp = diff_match_patch()
    diffs = dmp.diff_main(original, corrected)
    dmp.diff_cleanupSemantic(diffs)

    changes = []
    offset = 0
    i = 0

    while i < len(diffs):
        op, data = diffs[i]
        if op == -1: # deletion
            start_index = offset
            removed_text = data
            resolution = ""

            # Check if the next diff is an insertion (replacement)
            if i + 1 < len(diffs) and diffs[i + 1][0] == 1:
                resolution = diffs[i + 1][1].strip()
                i += 1

            changes.append({
                "startIndex": start_index,
                "endIndex": start_index + len(removed_text),
                "resolution": resolution
            })
        
        if op != 1:
            offset += len(data)
            
        i += 1

    return changes