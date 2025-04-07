from typing import Optional, Type
from io import StringIO

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_community.tools.file_management.utils import (
    INVALID_PATH_TEMPLATE,
    BaseFileToolMixin,
    FileValidationError,
)


class FastaFileInput(BaseModel):
    """Input for FastaFileTool."""

    file_path: str = Field(..., description="name of file")


class FastaHeadTool(BaseFileToolMixin, BaseTool):  # type: ignore[override, override]
    """Tool that reads fasta files."""

    name: str = "fasta_head_tool"
    args_schema: Type[BaseModel] = FastaFileInput
    description: str = "Read fasta files from disk and return the first n entries"

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

    def parse_fasta(self, f):
        f = iter(f)
        line = next(f)
        line = line.strip()
        assert line.startswith(">")
        desc = line[1:]
        seq = StringIO()
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                yield desc, seq.getvalue()
                desc = line[1:]
                seq = StringIO()
            else:
                # Whitespace is not meaningful
                line = line.replace(" ", "")
                seq.write(line)
        yield desc, seq.getvalue()

    def get_first_n_entries(self, f, n=10):
        entries = []
        for i, (desc, seq) in enumerate(self.parse_fasta(f)):
            if i >= n:
                break
            entries.append(f">{desc}\n{seq}")
        return "\n".join(entries)
