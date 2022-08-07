from enum import Enum
from typing import Any, List, Optional

from differ_for_code import visualizer


class DiffType(Enum):
    EQUAL = "equal"
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"
    BULK_REPLACE = "bulk_replace"
    LINE_REPLACE = "line_replace"


class DiffBase:

    def __init__(self, label: DiffType, before: Any, after: Any):
        self.label = label
        self.before = before
        self.after = after


class LineDiff(DiffBase):

    def __init__(
        self,
        label: DiffType,
        before_line_tokens: Optional[List[str]],
        after_line_tokens: Optional[List[str]],
        before_line_number: int,
        after_line_number: int):

        super().__init__(label, before_line_tokens, after_line_tokens)
        self.before_line_number = before_line_number
        self.after_line_number = after_line_number
    

    def __str__(self):
        before_str = None if self.before is None else "".join(self.before)
        after_str = None if self.after is None else "".join(self.after)
        res = f"[{self.label.value}]\n"
        res += f"    [before: {self.before_line_number}]\n"
        res += f"        {before_str}\n"
        res += f"    [after: {self.after_line_number}]\n"
        res += f"        {after_str}"
        return res


    def __repr__(self):
        return self.__str__()


    @staticmethod
    def equal_line(
        line_tokens: List[str],
        before_line_number: int,
        after_line_number: int) -> 'LineDiff':

        return LineDiff(DiffType.EQUAL, line_tokens, line_tokens, before_line_number, after_line_number)
    

    @staticmethod
    def insert_line(
        line_tokens: List[str],
        before_line_number: int,
        after_line_number: int) -> 'LineDiff':

        return LineDiff(DiffType.INSERT, None, line_tokens, before_line_number, after_line_number)


    @staticmethod
    def delete_line(
        line_tokens: List[str],
        before_line_number: int,
        after_line_number: int) -> 'LineDiff':

        return LineDiff(DiffType.DELETE, line_tokens, None, before_line_number, after_line_number)


class BulkReplace(DiffBase):

    def __init__(
        self,
        before_lined_tokens: List[List[str]],
        after_lined_tokens: List[List[str]],
        before_line_number_start: int,
        after_line_number_start: int):

        super().__init__(DiffType.BULK_REPLACE, before_lined_tokens, after_lined_tokens)
        self.before_line_start_number = before_line_number_start
        self.before_line_end_number = before_line_number_start + len(before_lined_tokens)
        self.after_line_start_number = after_line_number_start
        self.after_line_end_number = after_line_number_start + len(after_lined_tokens)
    

    def __str__(self):
        before_str = "\n        ".join([ "".join(line_tokens) for line_tokens in self.before ])
        after_str = "\n        ".join([ "".join(line_tokens) for line_tokens in self.after ])
        res = f"[{self.label.value}]\n"
        res += f"    [before: {self.before_line_start_number}:{self.before_line_end_number}]\n"
        res += f"        {before_str}\n"
        res += f"    [after: {self.after_line_start_number}:{self.after_line_end_number}]\n"
        res += f"        {after_str}"
        return res
    

    def __repr__(self):
        return self.__str__()
    

    @staticmethod
    def bulk_replace(
        before_lined_tokens: List[List[str]],
        after_lined_tokens: List[List[str]],
        before_line_start_number: int,
        after_line_start_number: int) -> 'BulkReplace':

        return BulkReplace(before_lined_tokens, after_lined_tokens, before_line_start_number, after_line_start_number)


class LineReplace(DiffBase):

    def __init__(
        self,
        before_line_token_diffs: List['TokenDiff'],
        after_line_token_diffs: List['TokenDiff'],
        before_line_number: int,
        after_line_number: int):

        super().__init__(DiffType.LINE_REPLACE, before_line_token_diffs, after_line_token_diffs)
        self.before_line_number = before_line_number
        self.after_line_number = after_line_number
    

    def __str__(self):
        res = f"[{self.label.value}]\n"
        res += f"    [before: {self.before_line_number}]\n"
        res += f"        {self.before}\n"
        res += f"    [after: {self.after_line_number}]\n"
        res += f"        {self.after}"
        return res
    

    def __repr__(self) -> str:
        return self.__str__()
    

    @staticmethod
    def line_replace(
        before_line_token_diffs: List['TokenDiff'],
        after_line_token_diffs: List['TokenDiff'],
        before_line_number: int,
        after_line_number: int) -> 'LineReplace':

        return LineReplace(before_line_token_diffs, after_line_token_diffs, before_line_number, after_line_number)


class TokenDiff(DiffBase):

    def __init__(
        self,
        label: DiffType,
        before_token: Optional[str],
        after_token: Optional[str],
        before_column_start_number: int,
        after_column_start_number: int):

        super().__init__(label, before_token, after_token)
        self.before_column_start_number = before_column_start_number
        if before_token is None:
            self.before_column_end_number = before_column_start_number
        else:
            self.before_column_end_number = before_column_start_number + len(before_token)
        self.after_column_start_number = after_column_start_number
        if after_token is None:
            self.after_column_end_number = after_column_start_number
        else:
            self.after_column_end_number = after_column_start_number + len(after_token)
    

    def __str__(self):
        return f"({self.label.value}, {self.before.__repr__()}, {self.after.__repr__()}, {self.before_column_start_number}:{self.before_column_end_number}, {self.after_column_start_number}:{self.after_column_end_number})"
    

    def __repr__(self):
        return self.__str__()


    @staticmethod
    def equal_token(
        token: str,
        before_column_start_number: int,
        after_column_start_number: int) -> 'TokenDiff':

        return TokenDiff(DiffType.EQUAL, token, token, before_column_start_number, after_column_start_number)
    

    @staticmethod
    def insert_token(
        token: str,
        before_column_start_number: int,
        after_column_start_number: int) -> 'TokenDiff':

        return TokenDiff(DiffType.INSERT, None, token, before_column_start_number, after_column_start_number)
    

    @staticmethod
    def delete_token(
        token: str,
        before_column_start_number: int,
        after_column_start_number: int) -> 'TokenDiff':

        return TokenDiff(DiffType.DELETE, token, None, before_column_start_number, after_column_start_number)


class DiffResult:

    def __init__(self, diffs: List[DiffBase], contain_bulk_replace: bool):
        self.diffs = diffs
        self.contain_bulk_replace = contain_bulk_replace


    def __str__(self):
        res = ""
        for diff in self.diffs:
            res += f"{diff}\n"
        res = res.strip()
        return res


    def visualize(self):
        for diff in self.diffs:
            if type(diff) == BulkReplace:
                before_str = "\n".join([ "".join(line_tokens) for line_tokens in diff.before ])
                visualizer.print_delete(before_str)
                print()
                after_str = "\n".join([ "".join(line_tokens) for line_tokens in diff.after ])
                visualizer.print_insert(after_str)
                print()
            elif type(diff) == LineDiff:
                if diff.label == DiffType.INSERT:
                    visualizer.print_insert("".join(diff.after))
                elif diff.label == DiffType.DELETE:
                    visualizer.print_delete("".join(diff.before))
                else:
                    visualizer.print_normal("".join(diff.before))
                print()
            elif type(diff) == LineReplace:
                for token_diff in diff.before:
                    if token_diff.label == DiffType.DELETE:
                        visualizer.print_replace(token_diff.before)
                    else:
                        visualizer.print_delete(token_diff.before)
                print()
                for token_diff in diff.after:
                    if token_diff.label == DiffType.INSERT:
                        visualizer.print_replace(token_diff.after)
                    else:
                        visualizer.print_insert(token_diff.after)
                print()
            else:
                raise Exception("unknown diff type")
    