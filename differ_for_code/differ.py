from difflib import SequenceMatcher
from typing import List, Tuple

from differ_for_code.diffs import (BulkReplace, DiffResult, DiffType, LineDiff,
                                   LineReplace, TokenDiff)


# Calculate difference between lines -> tokens
def diff(
    before_lined_tokens: List[List[str]],
    after_lined_tokens: List[List[str]]) -> DiffResult:

    before_lines = [ "".join(line_tokens) for line_tokens in before_lined_tokens ]
    after_lines = [ "".join(line_tokens) for line_tokens in after_lined_tokens ]
    line_diff_results = SequenceMatcher(None, before_lines, after_lines).get_opcodes()

    result = []
    contains_bulk_replace = False
    
    for line_diff_result in line_diff_results:
        label = DiffType(line_diff_result[0])

        # these are line number (row number)
        before_line_start_number = line_diff_result[1]
        before_line_end_number = line_diff_result[2]
        after_line_start_number = line_diff_result[3]
        after_line_end_number = line_diff_result[4]

        diff_before_lined_tokens = before_lined_tokens[before_line_start_number:before_line_end_number]
        diff_after_lined_tokens = after_lined_tokens[after_line_start_number:after_line_end_number]

        if label == DiffType.EQUAL:
            # if the line matches exactly

            # the number of lines of before/after is equal if EQUAL 
            before_line_numbers = list(range(before_line_start_number, before_line_end_number + 1))
            after_line_numbers = list(range(after_line_start_number, after_line_end_number + 1))

            # contents of before/after is equal if EQUAL
            result += [ 
                LineDiff.equal_line(line_tokens, before_line_number, after_line_number)
                for line_tokens, before_line_number, after_line_number
                in zip(diff_after_lined_tokens, before_line_numbers, after_line_numbers)
                ]
            
        elif label == DiffType.INSERT:
            # if the line is inserted

            # adjust before_line_numbers because before is empty if INSERT
            after_line_numbers = list(range(after_line_start_number, after_line_end_number + 1))
            before_line_numbers = [before_line_start_number] * len(after_line_numbers)

            result += [
                LineDiff.insert_line(line_tokens, before_line_number, after_line_number)
                for line_tokens, before_line_number, after_line_number
                in zip(diff_after_lined_tokens, before_line_numbers, after_line_numbers)
                ]
            
        elif label == DiffType.DELETE:
            # if the line is deleted

            # adjust after_line_numbers because after is empty if DELETE
            before_line_numbers = list(range(before_line_start_number, before_line_end_number + 1))
            after_line_numbers = [after_line_start_number] * len(before_line_numbers)

            result += [
                LineDiff.delete_line(line_tokens, before_line_number, after_line_number)
                for line_tokens, before_line_number, after_line_number
                in zip(diff_before_lined_tokens, before_line_numbers, after_line_numbers)
                ]
            
        elif label == DiffType.REPLACE:

            if len(diff_before_lined_tokens) != len(diff_after_lined_tokens):
                # whole lines are considerd BULK_REPLACE if different number of lines are replaced
                # NOTE: compare each line of before/after
                #       and change the label to LINE_REPLACE if the lines are very similar?
                data = BulkReplace.bulk_replace(diff_before_lined_tokens, diff_after_lined_tokens, before_line_start_number, after_line_start_number)
                result.append(data)
                contains_bulk_replace = True

            else:
                # each line is considerd LINE_REPLACE if same number of lines are replaced
                # NOTE: it's possible that the number of lines are equal but the lines are not similar at all
                lines_len = len(diff_before_lined_tokens)
                result += __diff_line_replace(before_lined_tokens, after_lined_tokens, lines_len ,before_line_start_number, after_line_start_number)

    return DiffResult(result, contains_bulk_replace)

def __diff_line_replace(
    before_lined_tokens: List[List[str]],
    after_lined_tokens: List[List[str]],
    lines_len: int,
    before_line_start_number: int,
    after_line_start_number: int) -> List[LineReplace]:

    # pre-calculate the difference for each token in the line to use it twice (before/after)
    pre_inline_diff_results_list: List[List[Tuple[str, int, int, int, int]]] = []

    for index in range(lines_len):
        diff_before_tokens = before_lined_tokens[before_line_start_number + index]
        diff_after_tokens = after_lined_tokens[after_line_start_number + index]
        inline_diff_results = SequenceMatcher(None, diff_before_tokens, diff_after_tokens).get_opcodes()
        pre_inline_diff_results_list.append(inline_diff_results)

    line_diffs: List[LineReplace] = []

    for index in range(lines_len):

        inline_diff_results = pre_inline_diff_results_list[index]
        before_line_number = before_line_start_number + index
        after_line_number = after_line_start_number + index
        diff_before_tokens = before_lined_tokens[before_line_number]
        diff_after_tokens = after_lined_tokens[after_line_number]

        before_line_token_diffs: List[TokenDiff] = []
        after_line_token_diffs: List[TokenDiff] = []


        # before
        current_before_column_number = 0
        current_after_column_number = 0
        for idx, inline_diff_result in enumerate(inline_diff_results):
            label = DiffType(inline_diff_result[0])
            # these are not column number, just a position of the token
            before_token_start_pos = inline_diff_result[1]
            before_token_end_pos = inline_diff_result[2]

            diff_before = diff_before_tokens[before_token_start_pos:before_token_end_pos]
            diff_before_line = "".join(diff_before)

            diff_result, current_before_column_number, current_after_column_number = __convert_line_replace(inline_diff_results, idx, diff_before_line, diff_before, current_before_column_number, current_after_column_number, label, True)
            before_line_token_diffs += diff_result
        
        
        # after
        current_before_column_number = 0
        current_after_column_number = 0
        for idx, inline_diff_result in enumerate(inline_diff_results):
            label = DiffType(inline_diff_result[0])
            # these are not column number, just a position of the token
            after_token_start_pos = inline_diff_result[3]
            after_token_end_pos = inline_diff_result[4]

            diff_after = diff_after_tokens[after_token_start_pos:after_token_end_pos]
            diff_after_line = "".join(diff_after)

            diff_result, current_before_column_number, current_after_column_number = __convert_line_replace(inline_diff_results, idx, diff_after_line, diff_after, current_before_column_number, current_after_column_number, label, False)
            after_line_token_diffs += diff_result
        

        line_diff = LineReplace.line_replace(before_line_token_diffs, after_line_token_diffs, before_line_number, after_line_number)
        line_diffs.append(line_diff)

    return line_diffs

def __convert_line_replace(
    inline_diff_results: List[Tuple[str, int, int, int, int]],
    idx: int,
    diff_line: str,
    diff_tokens: List[str],
    current_before_column_number: int,
    current_after_column_number: int,
    label: DiffType,
    is_before: bool) -> Tuple[List[TokenDiff], int, int]:

    # if previous and next token is insert/delete/replace and this token is empty, it will be REPLACE
    # this is because the inner empty token is often considered EQUAL even if the both(previous/next) tokens are REPLACE
    is_between = False
    if (0 < idx < len(inline_diff_results) - 1):

        before_label = DiffType(inline_diff_results[idx - 1][0])
        after_label = DiffType(inline_diff_results[idx + 1][0])
        
        if ((before_label == after_label == DiffType.INSERT)
        or (before_label == after_label == DiffType.DELETE)
        or (before_label == after_label == DiffType.REPLACE)):
            if (diff_line.strip() == ""):
                is_between = True
    
    if (is_between or label != DiffType.EQUAL):
        if is_before:
            res = []
            for token in diff_tokens:
                res.append(TokenDiff.delete_token(token, current_before_column_number, current_after_column_number))
                # after column number is the same if it's DELETE
                current_before_column_number += len(token)
            return (res, current_before_column_number, current_after_column_number)
        else:
            res = []
            for token in diff_tokens:
                res.append(TokenDiff.insert_token(token, current_before_column_number, current_after_column_number))
                # before_column_number is the same if it's INSERT
                current_after_column_number += len(token)
            return (res, current_before_column_number, current_after_column_number)
    else:
        res = []
        for token in diff_tokens:
            res.append(TokenDiff.equal_token(token, current_before_column_number, current_after_column_number))
            # update both column numbers
            current_before_column_number += len(token)
            current_after_column_number += len(token)
        return (res, current_before_column_number, current_after_column_number)
