from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_community.tools.file_management.utils import (
    INVALID_PATH_TEMPLATE,
    BaseFileToolMixin,
    FileValidationError,
)


class FastqFileInput(BaseModel):
    """Input for FastqFileTool."""

    file_path: str = Field(..., description="name of file")


class FastqHeadTool(BaseFileToolMixin, BaseTool):  # type: ignore[override, override]
    """Tool that reads fastq files."""

    name: str = "fastq_head_tool"
    args_schema: Type[BaseModel] = FastqFileInput
    description: str = "Read fastq files from disk and return the first n entries"

    def _run(
        self,
        file_path: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            read_path = self.get_relative_path(file_path)
        except FileValidationError:
            return INVALID_PATH_TEMPLATE.format(arg_name="file_path", value=file_path)
        if not read_path.exists():
            return f"Error: no such file or directory: {file_path}"
        try:
            with read_path.open("r", encoding="utf-8") as f:
                content = self.get_first_n_entries(f)
            return content
        except Exception as e:
            return "Error: " + str(e)

    def _grouper(self, iterable, n):
        "Collect data into fixed-length chunks or blocks"
        args = [iter(iterable)] * n
        return zip(*args)

    def parse_fastq(self, f):
        for desc, seq, _, qual in self._grouper(f, 4):
            desc = desc.rstrip()[1:]
            seq = seq.rstrip()
            qual = qual.rstrip()
            yield desc, seq, qual

    def get_first_n_entries(self, f, n=10):
        entries = []
        for i, (desc, seq, qual) in enumerate(self.parse_fastq(f)):
            if i >= n:
                break
            entries.append(f"@{desc}\n{seq}\n+\n{qual}")
        return "\n".join(entries)
